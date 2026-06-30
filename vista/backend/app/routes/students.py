"""
Students API — Scoped by role.
- Admin: sees all students
- HOS: sees students in their school's departments/classes
- HOP: sees students in their department's classes only
- Teacher: sees students in classes they teach
- Mentor: sees only assigned students
- Student: own profile only (via student-portal)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.organization import ClassSection, Department, MentorAssignment, TeacherSubjectAssignment
from ..models.student import Student
from ..models.user import User
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["students"])


def _get_scoped_student_query(db: Session, current_user: User):
    """Return a query for students scoped by the user's role and org assignment."""
    query = db.query(Student).filter(Student.is_active == True)

    if current_user.role == "admin":
        # Admin sees all
        return query

    elif current_user.role == "hos":
        # HOS sees students in all departments under their school
        dept_ids = [d.id for d in db.query(Department).filter(Department.school_id == current_user.school_id).all()]
        if dept_ids:
            class_codes = [c.code for c in db.query(ClassSection).filter(ClassSection.department_id.in_(dept_ids)).all()]
            if class_codes:
                return query.filter(Student.class_.in_(class_codes))
        return query.filter(False)  # No results

    elif current_user.role == "hop":
        # HOP sees students in their department's classes only
        class_codes = [c.code for c in db.query(ClassSection).filter(ClassSection.department_id == current_user.department_id).all()]
        if class_codes:
            return query.filter(Student.class_.in_(class_codes))
        return query.filter(False)

    elif current_user.role == "teacher":
        # Teacher sees students in classes they're assigned to teach
        assignments = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == current_user.id,
            TeacherSubjectAssignment.is_active == True,
        ).all()
        class_section_ids = list(set(a.class_section_id for a in assignments))
        if class_section_ids:
            class_codes = [c.code for c in db.query(ClassSection).filter(ClassSection.id.in_(class_section_ids)).all()]
            if class_codes:
                return query.filter(Student.class_.in_(class_codes))
        return query.filter(False)

    elif current_user.role == "mentor":
        # Mentor sees only their assigned students
        assigned_ids = [
            ma.student_id for ma in
            db.query(MentorAssignment).filter(MentorAssignment.mentor_id == current_user.id, MentorAssignment.is_active == True).all()
        ]
        if assigned_ids:
            return query.filter(Student.student_id.in_(assigned_ids))
        return query.filter(False)

    else:
        # Students shouldn't be accessing this endpoint directly
        return query.filter(False)


@router.get("")
def list_students(
    page: int = 1,
    page_size: int = 50,
    class_code: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List students scoped by role. Supports filtering by class and search."""
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    query = _get_scoped_student_query(db, current_user)

    if class_code:
        query = query.filter(Student.class_ == class_code)
    if search:
        query = query.filter(
            (Student.name.ilike(f"%{search}%")) | (Student.student_id.ilike(f"%{search}%"))
        )

    total = query.count()
    students = query.order_by(Student.name).offset(offset).limit(page_size).all()

    return {
        "students": [_student_dict(s) for s in students],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{student_id}")
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id} exists."},
        )

    # Access check: ensure user can see this student
    if current_user.role == "student":
        # Students can only see their own data
        if current_user.id != f"student-{student_id}":
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Cannot access other students' data."})
    elif current_user.role == "mentor":
        assigned = db.query(MentorAssignment).filter(
            MentorAssignment.mentor_id == current_user.id,
            MentorAssignment.student_id == student_id,
            MentorAssignment.is_active == True,
        ).first()
        if not assigned:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Student not assigned to you."})

    return _student_dict(student)


def _student_dict(s: Student) -> dict:
    import json
    activities = json.loads(s.extracurricular) if s.extracurricular else []
    return {
        "student_id": s.student_id,
        "name": s.name,
        "class": s.class_,
        "usn": s.usn,
        "phone": s.phone,
        "enrolled_at": s.enrolled_at,
        "is_active": s.is_active,
        "extracurricular": activities,
    }
