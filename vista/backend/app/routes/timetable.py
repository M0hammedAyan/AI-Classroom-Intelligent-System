"""
Timetable API
=============
Provides role-scoped endpoints for viewing and managing class schedules:
- Student: read-only weekly grid for their class, highlighting today and current period.
- Teacher: their assigned slots + 'Today' schedule card with real-time status and attendance gating.
- Admin: full CRUD timetable manager with double-booking validation and audit logging.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Attendance
from ..models.audit import AuditLog
from ..models.organization import ClassSection, Subject, TeacherSubjectAssignment
from ..models.student import Student
from ..models.timetable import TimetableSlot
from ..models.user import User
from ..routes.auth import get_current_user, require_admin
from ..time_utils import (
    get_current_ist_datetime,
    get_ist_date_str,
    get_ist_day_of_week,
    get_ist_time_str,
    time_to_minutes,
)

router = APIRouter(prefix="/api/v1/timetable", tags=["timetable"])

GRACE_MINUTES = 10


def _get_student_id_from_user(user: User) -> str:
    if user.id.startswith("student-"):
        return user.id.replace("student-", "")
    return user.email.split("@")[0].upper()


def _format_slot(slot: TimetableSlot, db: Session) -> dict[str, Any]:
    subject = db.query(Subject).filter(Subject.id == slot.subject_id).first() if slot.subject_id else None
    teacher = db.query(User).filter(User.id == slot.teacher_id).first() if slot.teacher_id else None
    cs = db.query(ClassSection).filter(ClassSection.id == slot.class_section_id).first() if slot.class_section_id else None

    return {
        "id": slot.id,
        "class_section_id": slot.class_section_id,
        "class_name": cs.name if cs else None,
        "class_code": cs.code if cs else None,
        "subject_id": slot.subject_id,
        "subject_name": subject.name if subject else ("Free" if slot.slot_type == "free" else ("Break" if slot.slot_type == "break" else "Non-Teaching")),
        "subject_code": subject.code if subject else None,
        "teacher_id": slot.teacher_id,
        "teacher_name": teacher.name if teacher else None,
        "day_of_week": slot.day_of_week,
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "room": slot.room,
        "period_label": slot.period_label,
        "slot_type": slot.slot_type,
        "batch": slot.batch,
        "is_unconfirmed": bool(slot.is_unconfirmed),
        "effective_from": slot.effective_from,
        "is_active": slot.is_active,
    }


# ===========================================================================
# 1. Student View
# ===========================================================================

@router.get("/student")
def get_student_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Read-only weekly timetable for the authenticated student's class section.
    Highlights today's column and current period based on server IST clock.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student role required.")

    sid = _get_student_id_from_user(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")

    # Resolve class section
    class_section = None
    if student.classroom_id:
        class_section = db.query(ClassSection).filter(
            (ClassSection.id == student.classroom_id) | (ClassSection.code == student.classroom_id)
        ).first()
    if not class_section and student.class_:
        class_section = db.query(ClassSection).filter(
            (ClassSection.code == student.class_) | (ClassSection.id == student.class_)
        ).first()

    if not class_section:
        raise HTTPException(status_code=404, detail="Student class section not found.")

    ist_now = get_current_ist_datetime()
    current_dow = get_ist_day_of_week(ist_now)
    current_time_str = get_ist_time_str(ist_now)
    current_minutes = time_to_minutes(current_time_str)

    # Fetch active slots for this class section
    slots = (
        db.query(TimetableSlot)
        .filter(
            TimetableSlot.class_section_id == class_section.id,
            TimetableSlot.is_active == True,
        )
        .order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc())
        .all()
    )

    current_slot_id = None
    formatted_slots = []
    for s in slots:
        fmt = _format_slot(s, db)
        is_today = (s.day_of_week == current_dow)
        s_start = time_to_minutes(s.start_time)
        s_end = time_to_minutes(s.end_time)

        is_current = is_today and (s_start <= current_minutes <= s_end)
        if is_current:
            current_slot_id = s.id

        fmt["is_today"] = is_today
        fmt["is_current"] = is_current
        # Filter for student batch if assigned; if not assigned, show all lab slots
        if student.batch and s.batch and s.batch != student.batch:
            fmt["for_other_batch"] = True
        else:
            fmt["for_other_batch"] = False

        formatted_slots.append(fmt)

    return {
        "student": {
            "student_id": student.student_id,
            "name": student.name,
            "class_section_id": class_section.id,
            "class_code": class_section.code,
            "batch": student.batch,
        },
        "server_time_ist": {
            "day_of_week": current_dow,
            "time": current_time_str,
            "date": get_ist_date_str(ist_now),
        },
        "current_slot_id": current_slot_id,
        "slots": formatted_slots,
    }


# ===========================================================================
# 2. Teacher View
# ===========================================================================

@router.get("/teacher")
def get_teacher_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Teacher's weekly schedule (assigned faculty slots only) + Today's real-time classes.
    """
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teacher role required.")

    ist_now = get_current_ist_datetime()
    current_dow = get_ist_day_of_week(ist_now)
    current_time_str = get_ist_time_str(ist_now)
    current_date_str = get_ist_date_str(ist_now)
    current_minutes = time_to_minutes(current_time_str)

    slots = (
        db.query(TimetableSlot)
        .filter(
            TimetableSlot.teacher_id == current_user.id,
            TimetableSlot.is_active == True,
        )
        .order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc())
        .all()
    )

    formatted_slots = [_format_slot(s, db) for s in slots]

    # Today's classes
    today_slots = [s for s in slots if s.day_of_week == current_dow]
    today_classes = []
    active_slot_now = None

    for s in today_slots:
        s_start = time_to_minutes(s.start_time)
        s_end = time_to_minutes(s.end_time)

        # Check if attendance was recorded for this slot today
        att_count = (
            db.query(Attendance)
            .filter(
                Attendance.session_date == current_date_str,
                Attendance.subject_id == s.subject_id,
            )
            .count()
        )
        attendance_taken = att_count > 0

        # Check status
        # Grace rule: active period wins. Grace window applies only when no active period.
        is_active_now = (s_start <= current_minutes <= s_end)
        is_grace = False
        if not is_active_now:
            # Check within 10-minute grace window
            is_grace = (
                (s_start - GRACE_MINUTES <= current_minutes < s_start) or
                (s_end < current_minutes <= s_end + GRACE_MINUTES)
            )

        if attendance_taken:
            slot_status = "attendance_taken"
        elif is_active_now or is_grace:
            slot_status = "now"
            active_slot_now = s.id
        elif current_minutes < s_start:
            slot_status = "upcoming"
        else:
            slot_status = "missed"

        today_classes.append({
            "slot": _format_slot(s, db),
            "status": slot_status,
            "attendance_taken": attendance_taken,
            "take_attendance_enabled": (slot_status == "now" and not attendance_taken),
        })

    return {
        "teacher_id": current_user.id,
        "teacher_name": current_user.name,
        "server_time_ist": {
            "day_of_week": current_dow,
            "time": current_time_str,
            "date": current_date_str,
        },
        "current_active_slot_id": active_slot_now,
        "today_classes": today_classes,
        "weekly_slots": formatted_slots,
    }


# ===========================================================================
# 3. Admin View & CRUD
# ===========================================================================

class CreateSlotRequest(BaseModel):
    class_section_id: str
    subject_id: str | None = None
    teacher_id: str | None = None
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    room: str | None = "A-302"
    period_label: str | None = None
    slot_type: str = "teaching"  # teaching | lab | free | break | non_teaching
    batch: str | None = None
    is_unconfirmed: bool = False
    effective_from: str | None = "2026-08-03"


class UpdateSlotRequest(BaseModel):
    class_section_id: str | None = None
    subject_id: str | None = None
    teacher_id: str | None = None
    day_of_week: int | None = Field(None, ge=0, le=6)
    start_time: str | None = None
    end_time: str | None = None
    room: str | None = None
    period_label: str | None = None
    slot_type: str | None = None
    batch: str | None = None
    is_unconfirmed: bool | None = None
    effective_from: str | None = None
    is_active: bool | None = None


@router.get("/admin")
def get_admin_timetable(
    class_section_id: str | None = None,
    teacher_id: str | None = None,
    day_of_week: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin view: inspect slots across all classes and faculty."""
    query = db.query(TimetableSlot).filter(TimetableSlot.is_active == True)
    if class_section_id:
        query = query.filter(TimetableSlot.class_section_id == class_section_id)
    if teacher_id:
        query = query.filter(TimetableSlot.teacher_id == teacher_id)
    if day_of_week is not None:
        query = query.filter(TimetableSlot.day_of_week == day_of_week)

    slots = query.order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc()).all()
    return {
        "total": len(slots),
        "slots": [_format_slot(s, db) for s in slots],
    }



@router.get("/class/{class_section_id}")
def get_class_timetable(
    class_section_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns weekly timetable for a given class section.
    Accessible to teachers and admins (and students belonging to that class).
    """
    cs = db.query(ClassSection).filter(
        (ClassSection.id == class_section_id) | (ClassSection.code == class_section_id)
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail=f"Class section '{class_section_id}' not found.")

    if current_user.role == "student":
        sid = _get_student_id_from_user(current_user)
        student = db.query(Student).filter(Student.student_id == sid).first()
        if not student or (student.classroom_id != cs.id and student.class_ != cs.code):
            raise HTTPException(status_code=403, detail="Students can only view their own class timetable.")

    slots = (
        db.query(TimetableSlot)
        .filter(
            TimetableSlot.class_section_id == cs.id,
            TimetableSlot.is_active == True,
        )
        .order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc())
        .all()
    )
    return {
        "class_section_id": cs.id,
        "class_name": cs.name,
        "class_code": cs.code,
        "semester": cs.semester,
        "total": len(slots),
        "slots": [_format_slot(s, db) for s in slots],
    }


def _validate_slot_conflicts(
    db: Session,
    slot_id_to_exclude: str | None,
    class_section_id: str,
    teacher_id: str | None,
    day_of_week: int,
    start_time: str,
    end_time: str,
    slot_type: str,
    batch: str | None,
    subject_id: str | None,
):
    """
    Validates:
    1. No teacher double-booking during overlapping period.
    2. No class double-booking during overlapping period (unless lab with distinct batches).
    3. If teaching slot: faculty must be assigned to subject in teacher_subjects.
    """
    st_m = time_to_minutes(start_time)
    et_m = time_to_minutes(end_time)
    if st_m >= et_m:
        raise HTTPException(status_code=400, detail="start_time must be earlier than end_time.")

    # Check faculty subject assignment if teaching
    if slot_type in ("teaching", "lab") and teacher_id and subject_id:
        # Check if subject is IDE-UNCONFIRMED
        subj = db.query(Subject).filter(Subject.id == subject_id).first()
        if subj and subj.code != "IDE-UNCONFIRMED":
            assign = (
                db.query(TeacherSubjectAssignment)
                .filter(
                    TeacherSubjectAssignment.teacher_id == teacher_id,
                    TeacherSubjectAssignment.subject_id == subject_id,
                    TeacherSubjectAssignment.is_active == True,
                )
                .first()
            )
            if not assign:
                raise HTTPException(
                    status_code=400,
                    detail="Teacher is not assigned to this subject in teacher_subjects."
                )

    # Query active slots on same day
    day_slots = (
        db.query(TimetableSlot)
        .filter(
            TimetableSlot.day_of_week == day_of_week,
            TimetableSlot.is_active == True,
        )
    )
    if slot_id_to_exclude:
        day_slots = day_slots.filter(TimetableSlot.id != slot_id_to_exclude)

    for other in day_slots.all():
        o_st = time_to_minutes(other.start_time)
        o_et = time_to_minutes(other.end_time)
        # Check overlap
        overlaps = max(st_m, o_st) < min(et_m, o_et)
        if not overlaps:
            continue

        # 1. Teacher double-booking check
        if teacher_id and other.teacher_id == teacher_id:
            raise HTTPException(
                status_code=409,
                detail=f"Teacher double-booking: Faculty is already assigned to slot {other.period_label or other.start_time} in {other.room}."
            )

        # 2. Class double-booking check
        if other.class_section_id == class_section_id:
            # Exception: concurrent lab slots for different batches (e.g. B1 vs B2)
            if slot_type == "lab" and other.slot_type == "lab" and batch and other.batch and batch != other.batch:
                continue
            # Non-teaching / break exception
            if slot_type == "break" and other.slot_type == "break":
                continue
            raise HTTPException(
                status_code=409,
                detail=f"Class double-booking: Class section already has a slot ({other.period_label or other.start_time}) during this time."
            )



def _authorize_slot_mutation(slot: TimetableSlot | None, current_user: User, new_teacher_id: str | None = None):
    """
    Strict authorization:
    - Admin: can create, update, delete any slot.
    - Teacher: can only create slots for themselves, and can only edit/delete their own slots.
    - Student: 403 Forbidden.
    """
    if current_user.role == "admin":
        return
    if current_user.role == "teacher":
        if slot and slot.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Teachers can only modify their own assigned timetable slots.")
        if new_teacher_id and new_teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Teachers cannot assign slots to other faculty members.")
        return
    raise HTTPException(status_code=403, detail="Timetable slot modification requires teacher or admin role.")


@router.post("/admin/slots", status_code=status.HTTP_201_CREATED)
@router.post("/slots", status_code=status.HTTP_201_CREATED)
def create_slot(
    body: CreateSlotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _authorize_slot_mutation(None, current_user, body.teacher_id)
    """Add a new timetable slot with strict conflict validation and audit logging."""
    _validate_slot_conflicts(
        db=db,
        slot_id_to_exclude=None,
        class_section_id=body.class_section_id,
        teacher_id=body.teacher_id,
        day_of_week=body.day_of_week,
        start_time=body.start_time,
        end_time=body.end_time,
        slot_type=body.slot_type,
        batch=body.batch,
        subject_id=body.subject_id,
    )

    slot_id = f"slot-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    new_slot = TimetableSlot(
        id=slot_id,
        class_section_id=body.class_section_id,
        subject_id=body.subject_id,
        teacher_id=body.teacher_id,
        day_of_week=body.day_of_week,
        start_time=body.start_time,
        end_time=body.end_time,
        room=body.room,
        period_label=body.period_label,
        slot_type=body.slot_type,
        batch=body.batch,
        is_unconfirmed=body.is_unconfirmed,
        effective_from=body.effective_from,
        is_active=True,
        created_at=now,
    )
    db.add(new_slot)

    # Audit log
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        action="create_timetable_slot",
        target_type="timetable_slot",
        target_id=slot_id,
        details=json.dumps({"new": body.model_dump()}),
        created_at=now,
    )
    db.add(audit)
    db.commit()
    db.refresh(new_slot)
    return _format_slot(new_slot, db)


@router.put("/admin/slots/{slot_id}")
@router.put("/slots/{slot_id}")
def update_slot(
    slot_id: str,
    body: UpdateSlotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")
    _authorize_slot_mutation(slot, current_user, body.teacher_id)
    """Edit an existing timetable slot with validation and audit logging."""
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")

    old_data = _format_slot(slot, db)
    updates = body.model_dump(exclude_unset=True)

    c_cid = updates.get("class_section_id", slot.class_section_id)
    c_tid = updates.get("teacher_id", slot.teacher_id)
    c_sub = updates.get("subject_id", slot.subject_id)
    c_dow = updates.get("day_of_week", slot.day_of_week)
    c_st = updates.get("start_time", slot.start_time)
    c_et = updates.get("end_time", slot.end_time)
    c_type = updates.get("slot_type", slot.slot_type)
    c_batch = updates.get("batch", slot.batch)

    _validate_slot_conflicts(
        db=db,
        slot_id_to_exclude=slot_id,
        class_section_id=c_cid,
        teacher_id=c_tid,
        day_of_week=c_dow,
        start_time=c_st,
        end_time=c_et,
        slot_type=c_type,
        batch=c_batch,
        subject_id=c_sub,
    )

    for k, v in updates.items():
        setattr(slot, k, v)

    now = datetime.now(timezone.utc).isoformat()
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        action="update_timetable_slot",
        target_type="timetable_slot",
        target_id=slot_id,
        details=json.dumps({"old": old_data, "new": updates}),
        created_at=now,
    )
    db.add(audit)
    db.commit()
    db.refresh(slot)
    return _format_slot(slot, db)


@router.delete("/admin/slots/{slot_id}")
@router.delete("/slots/{slot_id}")
def delete_slot(
    slot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")
    _authorize_slot_mutation(slot, current_user)
    """Soft-delete timetable slot with audit logging."""
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")

    slot.is_active = False
    now = datetime.now(timezone.utc).isoformat()
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        action="delete_timetable_slot",
        target_type="timetable_slot",
        target_id=slot_id,
        details=json.dumps({"deleted_slot": _format_slot(slot, db)}),
        created_at=now,
    )
    db.add(audit)
    db.commit()
    return {"message": "Slot deactivated successfully.", "slot_id": slot_id}


# ===========================================================================
# 4. Student Batch Assignment Endpoint
# ===========================================================================

class AssignBatchRequest(BaseModel):
    batch: str | None = Field(None, pattern=r"^(B1|B2|B3)?$")


@router.patch("/admin/students/{student_id}/batch")
def assign_student_batch(
    student_id: str,
    body: AssignBatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Assign or clear a student's lab batch (B1, B2, B3) with audit log."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    old_batch = student.batch
    student.batch = body.batch
    now = datetime.now(timezone.utc).isoformat()
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        action="assign_student_batch",
        target_type="student",
        target_id=student_id,
        details=json.dumps({"old_batch": old_batch, "new_batch": body.batch}),
        created_at=now,
    )
    db.add(audit)
    db.commit()
    return {
        "student_id": student.student_id,
        "name": student.name,
        "batch": student.batch,
        "message": f"Batch updated to {student.batch or 'None'}",
    }
