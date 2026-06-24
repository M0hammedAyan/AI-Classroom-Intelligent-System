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
    return _mark_response(att, student_id, db, liveness_passed)


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
# Vision integration shim
# ---------------------------------------------------------------------------

def _call_vision(image_path: str) -> dict | None:
    """
    Call vision.recognize(image_path) if the vision module is available.
    Falls back to a stub result so the backend runs independently during dev.
    """
    try:
        from vista.vision.recognize import recognize  # type: ignore
        return recognize(image_path)
    except ImportError:
        # Vision module not yet built — return a stub so the backend starts
        return {"student_id": None, "confidence": 0.0, "liveness_passed": False}


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
