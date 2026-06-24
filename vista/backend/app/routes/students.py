from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.student import Student
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["students"])


@router.get("")
def list_students(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size
    total = db.query(Student).filter(Student.is_active == True).count()
    students = (
        db.query(Student)
        .filter(Student.is_active == True)
        .offset(offset)
        .limit(page_size)
        .all()
    )
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
    _current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id} exists."},
        )
    return _student_dict(student)


def _student_dict(s: Student) -> dict:
    return {
        "student_id": s.student_id,
        "name": s.name,
        "class": s.class_,
        "enrolled_at": s.enrolled_at,
        "is_active": s.is_active,
    }
