from __future__ import annotations

import base64
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
import hashlib
from ..models.attendance import Attendance
from ..models.timetable import TimetableSlot
from ..models.capture import CaptureEvent
from ..time_utils import (
    get_current_ist_datetime,
    get_ist_day_of_week,
    get_ist_time_str,
    time_to_minutes,
)
from ..models.student import Student
from ..models.organization import TeacherSubjectAssignment, Subject, ClassSection
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])

MAX_IMAGE_BYTES = 30 * 1024 * 1024  # 30 MB


class MarkRequest(BaseModel):
    image: str           # base64-encoded JPEG or PNG
    classroom_id: str
    session_date: str    # YYYY-MM-DD
    subject_id: str | None = None  # Optional: for per-subject attendance
    slot_id: str | None = None
    is_extra_class: bool = False
    extra_class_reason: str | None = None
    source: str = "camera"  # 'camera' | 'upload'


class PatchRequest(BaseModel):
    status: str
    note: str | None = None


class ManualAttendanceRequest(BaseModel):
    student_id: str
    classroom_id: str
    session_date: str
    subject_id: str | None = None
    status: str
    note: str | None = None
    slot_id: str | None = None
    period_label: str | None = None



def _resolve_active_slot_for_capture(
    db: Session,
    current_user,
    classroom_id: str,
    subject_id: str | None,
    grace_minutes: int = 10,
) -> tuple[TimetableSlot | None, bool]:
    """
    Auto-resolves current active timetable slot for caller using server IST time.
    Returns (matched_slot, is_within_grace).
    """
    ist_now = get_current_ist_datetime()
    dow = get_ist_day_of_week(ist_now)
    time_str = get_ist_time_str(ist_now)
    curr_min = time_to_minutes(time_str)

    cs = db.query(ClassSection).filter(
        (ClassSection.id == classroom_id) | (ClassSection.code == classroom_id) | (ClassSection.name == classroom_id)
    ).first()
    cid = cs.id if cs else classroom_id

    query = db.query(TimetableSlot).filter(
        TimetableSlot.class_section_id == cid,
        TimetableSlot.day_of_week == dow,
        TimetableSlot.is_active == True,
    )
    if current_user.role == "teacher":
        query = query.filter((TimetableSlot.teacher_id == current_user.id) | (TimetableSlot.teacher_id == None))
    if subject_id:
        query = query.filter((TimetableSlot.subject_id == subject_id) | (TimetableSlot.subject_id == None))

    slots = query.all()

    # Exact active period match
    for s in slots:
        st_m = time_to_minutes(s.start_time)
        et_m = time_to_minutes(s.end_time)
        if st_m <= curr_min <= et_m:
            return s, False

    # Within grace window (+/- 10 mins)
    for s in slots:
        st_m = time_to_minutes(s.start_time)
        et_m = time_to_minutes(s.end_time)
        if (st_m - grace_minutes <= curr_min < st_m) or (et_m < curr_min <= et_m + grace_minutes):
            return s, True

    return None, False


def _check_attendance_scope(db: Session, current_user, classroom_id: str, subject_id: str | None):
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail={"code": "READ_ONLY", "message": "Student accounts cannot edit attendance."})
    if current_user.role != "teacher":
        return
    assignment = (
        db.query(TeacherSubjectAssignment)
        .join(Subject, Subject.id == TeacherSubjectAssignment.subject_id)
        .join(ClassSection, ClassSection.id == TeacherSubjectAssignment.class_section_id)
        .filter(
            TeacherSubjectAssignment.teacher_id == current_user.id,
            TeacherSubjectAssignment.is_active == True,
            (Subject.code == subject_id) | (Subject.id == subject_id),
            (ClassSection.code == classroom_id) | (ClassSection.id == classroom_id) | (ClassSection.name == classroom_id),
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=403, detail={"code": "SUBJECT_SCOPE", "message": "Teachers can only edit attendance for their assigned subject and class."})


def _normalize_subject_id(db: Session, subject_id: str | None) -> str | None:
    if not subject_id:
        return None
    subject = db.query(Subject).filter((Subject.id == subject_id) | (Subject.code == subject_id)).first()
    if not subject:
        raise HTTPException(status_code=404, detail={"code": "SUBJECT_NOT_FOUND", "message": f"No subject with id or code {subject_id}."})
    return subject.id


@router.post("/mark")
def mark_attendance(
    body: MarkRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    _check_attendance_scope(db, _current_user, body.classroom_id, body.subject_id)
    body.subject_id = _normalize_subject_id(db, body.subject_id)
    # Decode and size-check image
    try:
        image_bytes = base64.b64decode(body.image)
    except Exception:
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "Image must be valid base64."})
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 30 MB limit."})

    # Validate file magic bytes (JPEG or PNG only)
    JPEG_MAGIC = b'\xff\xd8\xff'
    PNG_MAGIC = b'\x89PNG'
    if not (image_bytes[:3] == JPEG_MAGIC or image_bytes[:4] == PNG_MAGIC):
        raise HTTPException(status_code=400, detail={"code": "INVALID_IMAGE", "message": "File must be JPEG or PNG (invalid magic bytes)."})

    # Write to temp file, call vision.recognize(), delete temp file
    suffix = ".jpg" if image_bytes[:3] == JPEG_MAGIC else ".png"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        vision_result = _call_vision(tmp_path, skip_liveness=True)
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
            subject_id=body.subject_id,
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
        subject_id=body.subject_id,
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
    _check_attendance_scope(db, _current_user, body.classroom_id, body.subject_id)
    body.subject_id = _normalize_subject_id(db, body.subject_id)
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
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 30 MB limit."})

    # Compute cryptographic hash of image bytes (NO RAW IMAGES OR EMBEDDINGS STORED)
    image_sha256 = hashlib.sha256(image_bytes).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    # Part 2: Resolve timetable slot and scheduled period gating
    active_slot = None
    is_extra = body.is_extra_class
    extra_reason = body.extra_class_reason

    if body.slot_id:
        active_slot = db.query(TimetableSlot).filter(TimetableSlot.id == body.slot_id, TimetableSlot.is_active == True).first()
    if not active_slot:
        active_slot, _ = _resolve_active_slot_for_capture(db, _current_user, body.classroom_id, body.subject_id)

    if not active_slot and _current_user.role == "teacher" and not is_extra:
        # Teacher capture outside scheduled period without extra class declaration
        failed_event = CaptureEvent(
            id=f"cap-{uuid.uuid4().hex[:12]}",
            teacher_id=_current_user.id,
            subject_id=body.subject_id,
            class_id=body.classroom_id,
            slot_id=None,
            captured_at=now,
            source=body.source or "camera",
            faces_detected=0,
            recognized_count=0,
            unrecognized_count=0,
            liveness_rejected_count=0,
            duplicates_skipped=0,
            status="failed",
            is_extra_class=False,
            reason="Outside scheduled period without extra class declaration.",
            image_sha256=image_sha256,
        )
        db.add(failed_event)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail={
                "code": "OUTSIDE_SCHEDULED_PERIOD",
                "message": "Capture is outside your scheduled period. Please mark as an 'Extra / make-up class' with a reason.",
            },
        )

    resolved_slot_id = active_slot.id if active_slot else None
    resolved_period = active_slot.period_label if active_slot else None

    # Write to temp file, call vision.recognize_all(), delete temp file
    suffix = ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        vision_results = _call_vision_all(tmp_path, skip_liveness=True)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not vision_results:
        # Record failed capture event
        fail_event = CaptureEvent(
            id=f"cap-{uuid.uuid4().hex[:12]}",
            teacher_id=_current_user.id,
            subject_id=body.subject_id,
            class_id=body.classroom_id,
            slot_id=resolved_slot_id,
            captured_at=now,
            source=body.source or "camera",
            faces_detected=0,
            recognized_count=0,
            unrecognized_count=0,
            liveness_rejected_count=0,
            duplicates_skipped=0,
            status="failed",
            is_extra_class=is_extra,
            reason="No faces detected in image.",
            image_sha256=image_sha256,
        )
        db.add(fail_event)
        db.commit()
        raise HTTPException(status_code=400, detail={"code": "NO_FACE_DETECTED", "message": "No faces detected in image."})

    response_results = []
    recognized_count = 0
    unrecognized_count = 0
    liveness_rejected_count = 0
    duplicates_skipped = 0

    for vision_result in vision_results:
        student_id = vision_result.get("student_id")
        confidence = float(vision_result.get("confidence", 0.0))
        liveness_passed = bool(vision_result.get("liveness_passed", False))

        if not liveness_passed:
            liveness_rejected_count += 1
            status = "liveness_failed"
            att = Attendance(
                id=str(uuid.uuid4()),
                student_id=student_id,
                classroom_id=body.classroom_id,
                subject_id=body.subject_id,
                session_date=body.session_date,
                slot_id=resolved_slot_id,
                period_label=resolved_period,
                is_extra_class=is_extra,
                extra_class_reason=extra_reason,
                timestamp=now,
                status=status,
                confidence=confidence,
                is_manual_override=False,
                source="face",
                created_at=now,
            )
            db.add(att)
            db.commit()
            db.refresh(att)
            response_results.append(_mark_response(att, student_id, db, liveness_passed))
            continue

        if student_id is None:
            unrecognized_count += 1
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
        recognized_count += 1

        # Check existing attendance in the same slot / date
        existing_query = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.classroom_id == body.classroom_id,
            Attendance.session_date == body.session_date,
            Attendance.subject_id == body.subject_id,
            Attendance.status == status,
        )
        if resolved_slot_id:
            existing_query = existing_query.filter(Attendance.slot_id == resolved_slot_id)

        existing = existing_query.first()
        if existing:
            duplicates_skipped += 1
            response_results.append(_mark_response(existing, student_id, db, liveness_passed))
            continue

        att = Attendance(
            id=str(uuid.uuid4()),
            student_id=student_id,
            classroom_id=body.classroom_id,
            subject_id=body.subject_id,
            session_date=body.session_date,
            slot_id=resolved_slot_id,
            period_label=resolved_period,
            is_extra_class=is_extra,
            extra_class_reason=extra_reason,
            timestamp=now,
            status=status,
            confidence=confidence,
            is_manual_override=False,
            source="face",
            created_at=now,
        )
        db.add(att)
        db.commit()
        db.refresh(att)
        response_results.append(_mark_response(att, student_id, db, liveness_passed))

    # Log successful CaptureEvent audit row
    cap_event = CaptureEvent(
        id=f"cap-{uuid.uuid4().hex[:12]}",
        teacher_id=_current_user.id,
        subject_id=body.subject_id,
        class_id=body.classroom_id,
        slot_id=resolved_slot_id,
        captured_at=now,
        source=body.source or "camera",
        faces_detected=len(vision_results),
        recognized_count=recognized_count,
        unrecognized_count=unrecognized_count,
        liveness_rejected_count=liveness_rejected_count,
        duplicates_skipped=duplicates_skipped,
        status="completed",
        is_extra_class=is_extra,
        reason=extra_reason if is_extra else None,
        image_sha256=image_sha256,
    )
    db.add(cap_event)
    db.commit()

    return {
        "results": response_results,
        "faces_detected": len(vision_results),
        "recognized_count": recognized_count,
        "duplicates_skipped": duplicates_skipped,
        "slot_id": resolved_slot_id,
        "period_label": resolved_period,
        "is_extra_class": is_extra,
        "capture_event_id": cap_event.id,
    }


@router.get("/log")
def attendance_log(
    classroom_id: str,
    date: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    if _current_user.role == "student":
        raise HTTPException(status_code=403, detail={"code": "READ_ONLY", "message": "Use the student portal for personal attendance."})
    # Resolve classroom: allow either section code (e.g. 'AIML-4A') or section id (e.g. 'class-aiml-4a')
    from ..models.organization import ClassSection
    cs = db.query(ClassSection).filter((ClassSection.code == classroom_id) | (ClassSection.id == classroom_id) | (ClassSection.name == classroom_id)).first()
    class_ids = {classroom_id}
    if cs:
        class_ids.update([cs.id, cs.code, cs.name])

    # All students in the classroom
    all_students = (
        db.query(Student)
        .filter(
            (Student.classroom_id.in_(class_ids)) | (Student.class_.in_(class_ids)),
            Student.is_active == True,
        )
        .all()
    )
    if not all_students:
        return {"classroom_id": classroom_id, "date": date, "records": [], "total": 0}

    # DB rows for this day
    att_rows = (
        db.query(Attendance)
        .filter(Attendance.classroom_id.in_(class_ids), Attendance.session_date == date)
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


@router.post("/manual")
def create_manual_attendance(
    body: ManualAttendanceRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Create or update a teacher/admin-corrected attendance row (upsert)."""
    if _current_user.role == "student":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Student accounts cannot edit attendance."})

    if body.status not in {"present", "absent"}:
        raise HTTPException(status_code=400, detail={"code": "INVALID_STATUS", "message": "status must be 'present' or 'absent'."})

    # Mandatory reason validation
    reason = (body.note or "").strip()
    if not reason:
        raise HTTPException(status_code=400, detail={"code": "REASON_REQUIRED", "message": "A reason is mandatory for manual attendance entry."})

    # Date validation: no future dates, no dates before semester start (03-Aug-2026) unless admin
    today_str = datetime.now(timezone.utc).date().isoformat()
    if body.session_date > today_str:
        raise HTTPException(status_code=400, detail={"code": "FUTURE_DATE", "message": "Cannot mark attendance for future dates."})
    if _current_user.role != "admin" and body.session_date < "2026-08-03":
        raise HTTPException(status_code=400, detail={"code": "DATE_OUT_OF_RANGE", "message": "Date cannot be before semester start (03-Aug-2026)."})

    _check_attendance_scope(db, _current_user, body.classroom_id, body.subject_id)
    body.subject_id = _normalize_subject_id(db, body.subject_id)
    student = db.query(Student).filter(Student.student_id == body.student_id, Student.is_active == True).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No active student with id {body.student_id}."})

    existing = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == body.student_id,
            Attendance.session_date == body.session_date,
            Attendance.subject_id == body.subject_id,
        )
        .first()
    )
    now = datetime.now(timezone.utc).isoformat()
    old_status = existing.status if existing else None
    if existing:
        existing.status = body.status
        existing.is_manual_override = True
        existing.source = "manual"
        existing.override_note = reason
        db.commit()
        db.refresh(existing)
        row = existing
    else:
        row = Attendance(
            id=str(uuid.uuid4()),
            student_id=body.student_id,
            classroom_id=body.classroom_id or student.classroom_id,
            subject_id=body.subject_id,
            session_date=body.session_date,
            timestamp=now,
            status=body.status,
            confidence=None,
            is_manual_override=True,
            source="manual",
            override_note=reason,
            created_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)

    # Write audit record
    from ..audit import log_action
    import json
    log_action(
        db,
        user_id=_current_user.id,
        action="manual_attendance_update",
        target_type="student",
        target_id=student.student_id,
        details=json.dumps({
            "subject_id": body.subject_id,
            "session_date": body.session_date,
            "old_status": old_status,
            "new_status": body.status,
            "reason": reason,
            "source": "manual",
        }),
    )
    db.commit()

    return {
        "attendance_id": row.id,
        "student_id": row.student_id,
        "student_name": student.name,
        "status": row.status,
        "confidence": row.confidence,
        "source": row.source,
        "marked_at": row.timestamp,
        "is_manual_override": row.is_manual_override,
        "is_update": old_status is not None,
    }


@router.get("/student/{student_id}")
def get_student_attendance_history(
    student_id: str,
    subject_id: str | None = None,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Fetch a student's attendance records for manual review / edit."""
    if _current_user.role == "student" and _current_user.id != f"student-{student_id}":
        raise HTTPException(status_code=403, detail="Forbidden")

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    if subject_id:
        query = query.filter((Attendance.subject_id == subject_id) | (Attendance.subject_id.like(f"%{subject_id.lower()}%")))
    records = query.order_by(Attendance.session_date.desc()).limit(100).all()

    return {
        "student_id": student.student_id,
        "student_name": student.name,
        "records": [
            {
                "id": r.id,
                "date": r.session_date,
                "status": r.status,
                "source": r.source or ("manual" if r.is_manual_override else "face"),
                "note": r.override_note,
                "confidence": r.confidence,
                "subject_id": r.subject_id,
            }
            for r in records
        ],
    }


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
    _check_attendance_scope(db, _current_user, row.classroom_id, row.subject_id)
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

def _call_vision(image_path: str, skip_liveness: bool = False) -> dict | None:
    """
    Call vision.recognize(image_path) for face detection + recognition.

    Returns:
        dict with {student_id, confidence, liveness_passed} if a face was processed.
        None if no face was detected in the image.

    The vision module handles:
        - Face detection (SCRFD)
        - Embedding extraction (ArcFace R50)
        - Matching against enrolled students (cosine similarity)
        - Liveness check (heuristic-based, skipped when skip_liveness=True)

    Falls back to a stub if InsightFace model is not available (first run / no model).
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from vista.vision.recognize import recognize
        result = recognize(image_path, skip_liveness=skip_liveness)

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


def _call_vision_all(image_path: str, skip_liveness: bool = False, dedupe: bool = True) -> list[dict]:
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
        results = recognize_all(image_path, skip_liveness=skip_liveness, dedupe=dedupe)
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
    student_sessions_count: dict[str, int] = defaultdict(int)
    for r in att_rows:
        if r.student_id:
            student_sessions_count[r.student_id] += 1

    student_summary = []
    for s in students:
        present = student_present.get(s.student_id, 0)
        s_total = student_sessions_count.get(s.student_id, 0)
        pct = (present / s_total * 100) if s_total > 0 else 0.0
        pct = min(100.0, max(0.0, round(pct, 1)))
        student_summary.append({
            "student_id": s.student_id,
            "name": s.name,
            "sessions_attended": present,
            "total_sessions": s_total,
            "attendance_pct": pct,
        })

    student_summary.sort(key=lambda x: x["attendance_pct"])

    # Overall
    total_expected = sum(student_sessions_count.values())
    total_present = sum(student_present.values())
    overall_pct = min(100.0, max(0.0, round((total_present / total_expected * 100), 1))) if total_expected > 0 else 0.0

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
        raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 30 MB limit."})

    suffix = ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        # Use recognize_all for multi-face — liveness ON (live webcam frames)
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


@router.get("/by-subject/{student_id}")
def attendance_by_subject(
    student_id: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Per-subject attendance breakdown for a student.
    Returns attendance percentage grouped by subject.
    If attendance rows don't have subject_id (legacy data), falls back to overall attendance.
    """
    from ..models.organization import Subject, TeacherSubjectAssignment, ClassSection

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get all subjects for the student's class
    class_section = (
        db.query(ClassSection)
        .filter(ClassSection.code == student.class_)
        .first()
    )

    subjects = []
    if class_section:
        # Find subjects assigned to this class section via teacher assignments
        assignments = (
            db.query(TeacherSubjectAssignment)
            .filter(TeacherSubjectAssignment.class_section_id == class_section.id, TeacherSubjectAssignment.is_active == True)
            .all()
        )
        subject_ids = list(set(a.subject_id for a in assignments))
        if subject_ids:
            subjects = db.query(Subject).filter(Subject.id.in_(subject_ids)).all()

    # Get attendance rows with subject_id for this student
    att_with_subject = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student_id,
            Attendance.subject_id.isnot(None),
        )
        .all()
    )

    # Get all attendance (for overall calculation)
    all_att = (
        db.query(Attendance)
        .filter(Attendance.student_id == student_id)
        .all()
    )

    # All session dates for overall
    all_sessions = (
        db.query(Attendance.session_date)
        .filter(Attendance.classroom_id == student.classroom_id)
        .distinct()
        .all()
    )
    total_sessions = len(all_sessions)
    total_present = sum(1 for a in all_att if a.status == "present")
    overall_pct = (total_present / total_sessions * 100) if total_sessions > 0 else 0

    # Group attendance by subject
    from collections import defaultdict
    subject_att = defaultdict(lambda: {"present": 0, "total": 0})

    # Count subject-specific attendance
    subject_sessions = defaultdict(set)  # subject_id -> set of session_dates
    for a in att_with_subject:
        subject_sessions[a.subject_id].add(a.session_date)
        if a.status == "present":
            subject_att[a.subject_id]["present"] += 1

    # Build per-subject breakdown
    breakdown = []
    for subj in subjects:
        total = len(subject_sessions.get(subj.id, set()))
        present = subject_att[subj.id]["present"]
        pct = (present / total * 100) if total > 0 else None  # None = no data yet

        breakdown.append({
            "subject_id": subj.id,
            "subject_name": subj.name,
            "subject_code": subj.code,
            "sessions_attended": present,
            "total_sessions": total,
            "attendance_pct": round(pct, 1) if pct is not None else None,
        })

    return {
        "student_id": student_id,
        "student_name": student.name,
        "overall": {
            "sessions_attended": total_present,
            "total_sessions": total_sessions,
            "attendance_pct": round(overall_pct, 1),
        },
        "by_subject": breakdown,
    }



# ===========================================================================
# Part 3: Attendance Capture History
# ===========================================================================
from ..models.capture import CaptureEvent


@router.get("/capture-history")
def get_capture_history(
    teacher_id: str | None = None,
    class_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve audit history of face attendance capture events.
    Access Control:
    - Admin: can view all captures or filter by teacher_id/class_id/status.
    - Teacher: can only view their own captures (forced to current_user.id).
    - Student: 403 Forbidden.
    STRICT PRIVACY: Returns only metadata and hash, never images or embeddings.
    """
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail="Forbidden: Students cannot access capture history.")

    query = db.query(CaptureEvent)

    if current_user.role == "teacher":
        query = query.filter(CaptureEvent.teacher_id == current_user.id)
    elif current_user.role == "admin" and teacher_id:
        query = query.filter(CaptureEvent.teacher_id == teacher_id)

    if class_id:
        query = query.filter(CaptureEvent.class_id == class_id)
    if status:
        query = query.filter(CaptureEvent.status == status)

    total = query.count()
    events = (
        query.order_by(CaptureEvent.captured_at.desc())
        .offset(max(0, offset))
        .limit(min(100, max(1, limit)))
        .all()
    )

    items = []
    for e in events:
        items.append({
            "id": e.id,
            "teacher_id": e.teacher_id,
            "subject_id": e.subject_id,
            "class_id": e.class_id,
            "slot_id": e.slot_id,
            "captured_at": e.captured_at,
            "source": e.source,
            "faces_detected": e.faces_detected,
            "recognized_count": e.recognized_count,
            "unrecognized_count": e.unrecognized_count,
            "liveness_rejected_count": e.liveness_rejected_count,
            "duplicates_skipped": e.duplicates_skipped,
            "status": e.status,
            "is_extra_class": e.is_extra_class,
            "reason": e.reason,
            "image_sha256": e.image_sha256,
        })

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "events": items,
    }


@router.post("/capture-history/cleanup")
def cleanup_capture_history(
    days: int = 365,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Purges capture audit metadata older than retention policy (default 365 days). Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required for capture retention cleanup.")

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    deleted_count = db.query(CaptureEvent).filter(CaptureEvent.captured_at < cutoff).delete()
    db.commit()
    return {
        "message": f"Successfully purged {deleted_count} capture records older than {days} days.",
        "deleted_count": deleted_count,
    }
