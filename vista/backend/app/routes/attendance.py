from __future__ import annotations

import base64
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Attendance
from ..models.student import Student
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


class MarkRequest(BaseModel):
    image: str           # base64-encoded JPEG or PNG
    classroom_id: str
    session_date: str    # YYYY-MM-DD


class PatchRequest(BaseModel):
    status: str
    note: str | None = None


@router.post("/mark")
def mark_attendance(
    body: MarkRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    # Decode and size-check image
    try:
        image_bytes = base64.b64decode(body.image)
    except Exception:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "Image must be valid base64."})
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 5 MB limit."})

    # Write to temp file, call vision.recognize(), delete temp file
    suffix = ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        vision_result = _call_vision(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if vision_result is None:
        raise HTTPException(status_code=400, detail={"code": "NO_FACE_DETECTED", "message": "No face detected in image."})

    student_id = vision_result.get("student_id")
    confidence = float(vision_result.get("confidence", 0.0))
    liveness_passed = bool(vision_result.get("liveness_passed", False))

    now = datetime.now(timezone.utc).isoformat()

    # Determine status and whether to write a row
    if not liveness_passed:
        status = "liveness_failed"
        att = Attendance(
            id=str(uuid.uuid4()),
            student_id=student_id,   # may be None
            classroom_id=body.classroom_id,
            session_date=body.session_date,
            timestamp=now,
            status=status,
            confidence=confidence,
            is_manual_override=False,
            created_at=now,
        )
        db.add(att)
        db.commit()
        db.refresh(att)
        return _mark_response(att, student_id, db, liveness_passed)

    if student_id is None:
        # Unrecognized — no row written
        return {
            "student_id": None,
            "student_name": None,
            "status": "unrecognized",
            "confidence": confidence,
            "liveness_passed": liveness_passed,
            "attendance_id": None,
            "marked_at": now,
        }

    status = "present"

    # Duplicate prevention: don't mark same student twice on same day
    existing = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id,
            Attendance.session_date == body.session_date,
            Attendance.status == "present",
        )
        .first()
    )
    if existing:
        return _mark_response(existing, student_id, db, liveness_passed)

    att = Attendance(
        id=str(uuid.uuid4()),
        student_id=student_id,
        classroom_id=body.classroom_id,
        session_date=body.session_date,
        timestamp=now,
        status=status,
        confidence=confidence,
        is_manual_override=False,
        created_at=now,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    response = _mark_response(att, student_id, db, liveness_passed)

    # Broadcast real-time update
    import asyncio
    try:
        from ..websocket import ws_manager
        asyncio.get_event_loop().create_task(
            ws_manager.broadcast({
                "type": "attendance_marked",
                "data": response,
            })
        )
    except Exception:
        pass

    return response


@router.post("/mark-batch")
def mark_attendance_batch(
    body: MarkRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Multi-face attendance: detect and recognize ALL faces in an image,
    write one attendance row per recognized student.
    """
    # Decode and size-check image
    try:
        image_bytes = base64.b64decode(body.image)
    except Exception:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "Image must be valid base64."})
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 5 MB limit."})

    # Write to temp file, call vision.recognize_all(), delete temp file
    suffix = ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        vision_results = _call_vision_all(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not vision_results:
        raise HTTPException(status_code=400, detail={"code": "NO_FACE_DETECTED", "message": "No faces detected in image."})

    now = datetime.now(timezone.utc).isoformat()
    response_results = []

    for vision_result in vision_results:
        student_id = vision_result.get("student_id")
        confidence = float(vision_result.get("confidence", 0.0))
        liveness_passed = bool(vision_result.get("liveness_passed", False))

        if not liveness_passed:
            status = "liveness_failed"
            att = Attendance(
                id=str(uuid.uuid4()),
                student_id=student_id,
                classroom_id=body.classroom_id,
                session_date=body.session_date,
                timestamp=now,
                status=status,
                confidence=confidence,
                is_manual_override=False,
                created_at=now,
            )
            db.add(att)
            db.commit()
            db.refresh(att)
            response_results.append(_mark_response(att, student_id, db, liveness_passed))
            continue

        if student_id is None:
            # Unrecognized face — no row written
            response_results.append({
                "student_id": None,
                "student_name": None,
                "status": "unrecognized",
                "confidence": confidence,
                "liveness_passed": liveness_passed,
                "attendance_id": None,
                "marked_at": now,
            })
            continue

        status = "present"
        att = Attendance(
            id=str(uuid.uuid4()),
            student_id=student_id,
            classroom_id=body.classroom_id,
            session_date=body.session_date,
            timestamp=now,
            status=status,
            confidence=confidence,
            is_manual_override=False,
            created_at=now,
        )
        db.add(att)
        db.commit()
        db.refresh(att)
        response_results.append(_mark_response(att, student_id, db, liveness_passed))

    return {"results": response_results, "faces_detected": len(vision_results)}


@router.get("/log")
def attendance_log(
    classroom_id: str,
    date: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    # All students in the classroom
    all_students = (
        db.query(Student)
        .filter(Student.classroom_id == classroom_id, Student.is_active == True)
        .all()
    )
    if not all_students:
        return {"classroom_id": classroom_id, "date": date, "records": [], "total": 0}

    # DB rows for this day
    att_rows = (
        db.query(Attendance)
        .filter(Attendance.classroom_id == classroom_id, Attendance.session_date == date)
        .all()
    )
    present_ids = {r.student_id: r for r in att_rows if r.student_id}

    records = []
    for s in all_students:
        if s.student_id in present_ids:
            row = present_ids[s.student_id]
            records.append({
                "attendance_id": row.id,
                "student_id": s.student_id,
                "student_name": s.name,
                "status": row.status,
                "confidence": row.confidence,
                "marked_at": row.timestamp,
                "is_manual_override": row.is_manual_override,
            })
        else:
            records.append({
                "attendance_id": None,
                "student_id": s.student_id,
                "student_name": s.name,
                "status": "absent",
                "confidence": None,
                "marked_at": None,
                "is_manual_override": False,
            })

    return {"classroom_id": classroom_id, "date": date, "records": records, "total": len(records)}


@router.patch("/{attendance_id}")
def patch_attendance(
    attendance_id: str,
    body: PatchRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    if body.status not in {"present", "absent"}:
        raise HTTPException(status_code=400, detail={"code": "INVALID_STATUS", "message": "status must be 'present' or 'absent'."})
    row = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not row:
        raise HTTPException(status_code=404, detail={"code": "ATTENDANCE_NOT_FOUND", "message": f"No attendance record with id {attendance_id}."})
    row.status = body.status
    row.is_manual_override = True
    row.override_note = body.note
    db.commit()
    db.refresh(row)
    student = db.query(Student).filter(Student.student_id == row.student_id).first()
    return {
        "attendance_id": row.id,
        "student_id": row.student_id,
        "student_name": student.name if student else None,
        "status": row.status,
        "confidence": row.confidence,
        "marked_at": row.timestamp,
        "is_manual_override": row.is_manual_override,
    }


# ---------------------------------------------------------------------------
# Vision integration
# ---------------------------------------------------------------------------

def _call_vision(image_path: str) -> dict | None:
    """
    Call vision.recognize(image_path) for face detection + recognition.

    Returns:
        dict with {student_id, confidence, liveness_passed} if a face was processed.
        None if no face was detected in the image.

    The vision module handles:
        - Face detection (SCRFD)
        - Embedding extraction (ArcFace R50)
        - Matching against enrolled students (cosine similarity)
        - Liveness check (heuristic-based)

    Falls back to a stub if InsightFace model is not available (first run / no model).
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from vista.vision.recognize import recognize
        result = recognize(image_path)

        # If confidence is 0 and no student matched, treat as no face detected
        if result["confidence"] == 0.0 and result["student_id"] is None and not result["liveness_passed"]:
            return None

        return result

    except ImportError:
        logger.warning("Vision module not available — using stub (no face recognition)")
        return {"student_id": None, "confidence": 0.0, "liveness_passed": False}

    except ValueError as exc:
        # Image could not be read
        logger.error(f"Vision error: {exc}")
        return None

    except Exception as exc:
        logger.error(f"Unexpected vision error: {exc}")
        return {"student_id": None, "confidence": 0.0, "liveness_passed": False}


def _call_vision_all(image_path: str) -> list[dict]:
    """
    Call vision.recognize_all(image_path) for multi-face detection + recognition.

    Returns:
        List of dicts with {student_id, confidence, liveness_passed} for each face.
        Empty list if no faces detected.

    Falls back to a stub if InsightFace model is not available.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from vista.vision.recognize import recognize_all
        results = recognize_all(image_path)
        return results

    except ImportError:
        logger.warning("Vision module not available — using stub (no face recognition)")
        return []

    except ValueError as exc:
        logger.error(f"Vision error: {exc}")
        return []

    except Exception as exc:
        logger.error(f"Unexpected vision error: {exc}")
        return []


def _mark_response(att: Attendance, student_id: str | None, db: Session, liveness_passed: bool) -> dict:
    student = db.query(Student).filter(Student.student_id == student_id).first() if student_id else None
    return {
        "student_id": student_id,
        "student_name": student.name if student else None,
        "status": att.status,
        "confidence": att.confidence,
        "liveness_passed": liveness_passed,
        "attendance_id": att.id,
        "marked_at": att.timestamp,
    }


@router.get("/stats")
def attendance_stats(
    classroom_id: str,
    from_date: str | None = None,
    to_date: str | None = None,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Get attendance statistics for a classroom.
    Returns overall, weekly, and per-student summary.
    """
    from collections import defaultdict

    # Default: last 30 days
    if not to_date:
        to_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not from_date:
        from datetime import timedelta
        d = datetime.now(timezone.utc) - timedelta(days=30)
        from_date = d.strftime("%Y-%m-%d")

    students = (
        db.query(Student)
        .filter(Student.classroom_id == classroom_id, Student.is_active == True)
        .all()
    )
    att_rows = (
        db.query(Attendance)
        .filter(
            Attendance.classroom_id == classroom_id,
            Attendance.session_date >= from_date,
            Attendance.session_date <= to_date,
        )
        .all()
    )

    # Unique session dates = total sessions held
    session_dates = sorted({r.session_date for r in att_rows})
    total_sessions = len(session_dates)

    # Per-student attendance count
    student_present: dict[str, int] = defaultdict(int)
    for r in att_rows:
        if r.student_id and r.status == "present":
            student_present[r.student_id] += 1

    # Weekly breakdown
    week_data: dict[str, dict] = defaultdict(lambda: {"sessions": 0, "present_total": 0})
    for d_str in session_dates:
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
            week_key = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
            week_data[week_key]["sessions"] += 1
        except ValueError:
            pass

    for r in att_rows:
        if r.status == "present":
            try:
                d = datetime.strptime(r.session_date, "%Y-%m-%d").date()
                week_key = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
                week_data[week_key]["present_total"] += 1
            except ValueError:
                pass

    weekly_summary = []
    for week in sorted(week_data.keys()):
        info = week_data[week]
        expected = info["sessions"] * len(students)
        avg_pct = (info["present_total"] / expected * 100) if expected > 0 else 0
        weekly_summary.append({
            "week": week,
            "sessions": info["sessions"],
            "avg_attendance_pct": round(avg_pct, 1),
        })

    # Per-student summary
    student_summary = []
    for s in students:
        present = student_present.get(s.student_id, 0)
        pct = (present / total_sessions * 100) if total_sessions > 0 else 0
        student_summary.append({
            "student_id": s.student_id,
            "name": s.name,
            "sessions_attended": present,
            "total_sessions": total_sessions,
            "attendance_pct": round(pct, 1),
        })

    student_summary.sort(key=lambda x: x["attendance_pct"])

    # Overall
    total_expected = total_sessions * len(students)
    total_present = sum(student_present.values())
    overall_pct = (total_present / total_expected * 100) if total_expected > 0 else 0

    return {
        "classroom_id": classroom_id,
        "from_date": from_date,
        "to_date": to_date,
        "total_sessions": total_sessions,
        "total_students": len(students),
        "overall_attendance_pct": round(overall_pct, 1),
        "weekly_summary": weekly_summary,
        "student_summary": student_summary,
    }


@router.post("/mark-video")
async def mark_attendance_video(
    body: MarkRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Process a video frame sequence for multi-face tracked attendance.
    Accepts a single frame (same as mark-batch) but integrates with
    the ByteTrack-style tracker for temporal consistency.

    For true video streaming, use the WebSocket endpoint /ws/attendance-stream.
    This endpoint provides a simpler request/response model.
    """
    # Decode image
    try:
        image_bytes = base64.b64decode(body.image)
    except Exception:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "Image must be valid base64."})
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 5 MB limit."})

    suffix = ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        # Use recognize_all for multi-face
        vision_results = _call_vision_all(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not vision_results:
        raise HTTPException(status_code=400, detail={"code": "NO_FACE_DETECTED", "message": "No faces detected."})

    # Feed to tracker for temporal consistency
    try:
        from vista.vision.tracker import FaceTracker
        tracker = FaceTracker(confirmation_frames=1)  # Single frame = immediate
        tracker.update(vision_results)
        confirmed = tracker.get_confirmed_attendees()
    except ImportError:
        # Fallback: use raw results
        confirmed = [
            {"student_id": r["student_id"], "confidence": r["confidence"]}
            for r in vision_results
            if r.get("student_id") and r.get("liveness_passed", True)
        ]

    # Write attendance for confirmed students
    now = datetime.now(timezone.utc).isoformat()
    marked = []
    for entry in confirmed:
        student_id = entry["student_id"]
        if not student_id:
            continue
        # Skip if already marked today
        existing = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.session_date == body.session_date,
                Attendance.status == "present",
            )
            .first()
        )
        if existing:
            continue

        att = Attendance(
            id=str(uuid.uuid4()),
            student_id=student_id,
            classroom_id=body.classroom_id,
            session_date=body.session_date,
            timestamp=now,
            status="present",
            confidence=entry["confidence"],
            is_manual_override=False,
            created_at=now,
        )
        db.add(att)
        marked.append({"student_id": student_id, "confidence": entry["confidence"]})

    db.commit()

    # Broadcast via WebSocket
    try:
        import asyncio
        from ..websocket import ws_manager
        asyncio.get_event_loop().create_task(
            ws_manager.broadcast({
                "type": "batch_attendance",
                "data": {"marked": marked, "total_faces": len(vision_results)},
            })
        )
    except Exception:
        pass

    return {
        "faces_detected": len(vision_results),
        "students_marked": len(marked),
        "marked": marked,
        "duplicates_skipped": len(confirmed) - len(marked),
    }
