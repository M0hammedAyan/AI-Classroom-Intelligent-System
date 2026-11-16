"""
Central Authorization Policy Helpers (Part 5)
==============================================
Centralizes all object-level permission checks for VISTA.
Import and call these helpers from route handlers — never inline the logic.

Usage:
    from ..auth_policy import can_view_student, can_view_teacher, can_view_slot, require_admin
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models.user import User
from .models.student import Student
from .models.organization import TeacherSubjectAssignment, MentorAssignment
from .models.timetable import TimetableSlot


# ---------------------------------------------------------------------------
# Role helpers
# ---------------------------------------------------------------------------

def require_admin(current_user: User) -> None:
    """Raise 403 if user is not an admin."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")


def require_teacher_or_admin(current_user: User) -> None:
    """Raise 403 if user is neither teacher nor admin."""
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Teacher or Admin access required.")


def require_authenticated(current_user: User) -> None:
    """Raise 401 if user object is missing (should not normally be called; auth dependency handles this)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required.")


# ---------------------------------------------------------------------------
# Student object-level checks
# ---------------------------------------------------------------------------

def can_view_student(current_user: User, student_id: str, db: Session) -> Student:
    """
    Check whether current_user may view the given student's data.

    Rules:
    - Admin: always allowed.
    - Student: only their own record (user.id == "student-{student_id}").
    - Teacher: must be assigned to student's class section or be their mentor.

    Returns the Student on success; raises 403/404 on failure.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    if current_user.role == "admin":
        return student

    if current_user.role == "student":
        own_sid = current_user.id.replace("student-", "")
        if own_sid != student_id:
            raise HTTPException(
                status_code=403,
                detail="Students may only access their own data.",
            )
        return student

    if current_user.role == "teacher":
        assigned = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == current_user.id,
            TeacherSubjectAssignment.class_section_id == student.classroom_id,
            TeacherSubjectAssignment.is_active == True,
        ).first()
        is_mentor = db.query(MentorAssignment).filter(
            MentorAssignment.mentor_id == current_user.id,
            MentorAssignment.student_id == student_id,
            MentorAssignment.is_active == True,
        ).first()
        if not assigned and not is_mentor:
            raise HTTPException(
                status_code=403,
                detail="Teacher is not assigned to this student's class section.",
            )
        return student

    raise HTTPException(status_code=403, detail="Unauthorized role.")


# ---------------------------------------------------------------------------
# Teacher object-level checks
# ---------------------------------------------------------------------------

def can_view_teacher(current_user: User, teacher_id: str, db: Session) -> User:
    """
    Check whether current_user may view the given teacher's data.

    Rules:
    - Admin: always allowed.
    - Teacher: only their own record.
    - Student: forbidden.

    Returns the teacher User on success; raises 403/404 on failure.
    """
    teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    if current_user.role == "admin":
        return teacher

    if current_user.role == "teacher":
        if current_user.id != teacher_id:
            raise HTTPException(
                status_code=403,
                detail="Teachers may only view their own data.",
            )
        return teacher

    raise HTTPException(status_code=403, detail="Students cannot access teacher data.")


# ---------------------------------------------------------------------------
# Timetable slot object-level checks
# ---------------------------------------------------------------------------

def can_view_slot(current_user: User, slot_id: str, db: Session) -> TimetableSlot:
    """
    Check whether current_user may view a timetable slot.
    - Any authenticated user (admin, teacher, student) may read slots.
    - Returns slot or raises 404.
    """
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Timetable slot not found.")
    return slot


def can_mutate_slot(current_user: User, slot_id: str, db: Session) -> TimetableSlot:
    """
    Check whether current_user may create/edit/delete a timetable slot.

    Rules:
    - Admin: may mutate any slot.
    - Teacher: may only mutate their own slots.
    - Student: forbidden.

    Returns slot or raises 403/404.
    """
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Timetable slot not found.")

    if current_user.role == "admin":
        return slot

    if current_user.role == "teacher":
        if slot.teacher_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Teachers may only modify their own timetable slots.",
            )
        return slot

    raise HTTPException(status_code=403, detail="Students cannot modify timetable slots.")


# ---------------------------------------------------------------------------
# Attendance capture checks
# ---------------------------------------------------------------------------

def can_capture_for_slot(
    current_user: User,
    classroom_id: str,
    subject_id: str | None,
    slot_id: str | None,
    db: Session,
) -> bool:
    """
    Check whether teacher may run face-capture attendance for a slot/class.

    Rules:
    - Admin: always allowed.
    - Teacher: must be assigned to subject in that class section.
    - Student: forbidden.

    Returns True on success; raises 403 on failure.
    """
    if current_user.role == "admin":
        return True

    if current_user.role == "teacher":
        assigned = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == current_user.id,
            TeacherSubjectAssignment.class_section_id == classroom_id,
            TeacherSubjectAssignment.is_active == True,
        ).first()
        if not assigned:
            raise HTTPException(
                status_code=403,
                detail="Teacher is not assigned to any subject in this class section.",
            )
        return True

    raise HTTPException(status_code=403, detail="Students cannot initiate attendance capture.")
