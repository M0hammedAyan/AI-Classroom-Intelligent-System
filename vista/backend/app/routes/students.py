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

import base64
import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Attendance, RiskFlag, Score
from ..models.organization import ClassSection, Department, MentorAssignment, TeacherSubjectAssignment
from ..models.organization import Subject
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
        "students": [_student_dict(s, db) for s in students],
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

    return _student_dict(student, db)


@router.get("/{student_id}/academic-record")
def academic_record(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return scoped attendance, marks, subjects, and latest risk for a student."""
    student = db.query(Student).filter(Student.student_id == student_id, Student.is_active == True).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id} exists."})
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only admins and assigned teachers can view this record."})

    assignments = db.query(TeacherSubjectAssignment).filter(
        TeacherSubjectAssignment.is_active == True,
    )
    if current_user.role == "teacher":
        assignments = assignments.filter(TeacherSubjectAssignment.teacher_id == current_user.id)
    assignments = assignments.all()

    class_section = db.query(ClassSection).filter(ClassSection.code == student.class_).first()
    class_id = class_section.id if class_section else None
    assignments = [a for a in assignments if not class_id or a.class_section_id == class_id]
    subject_ids = {a.subject_id for a in assignments}
    subjects = db.query(Subject).filter(Subject.id.in_(subject_ids)).all() if subject_ids else []
    subject_by_id = {s.id: s for s in subjects}
    subject_names = {s.name for s in subjects}
    subject_codes = {s.code for s in subjects}

    attendance_query = db.query(Attendance).filter(Attendance.student_id == student_id)
    if current_user.role == "teacher":
        attendance_query = attendance_query.filter(Attendance.subject_id.in_(subject_ids)) if subject_ids else attendance_query.filter(False)
    attendance_rows = attendance_query.order_by(Attendance.session_date.desc()).all()

    score_query = db.query(Score).filter(Score.student_id == student_id)
    if current_user.role == "teacher":
        score_query = score_query.filter(Score.subject.in_(subject_names | subject_codes)) if subject_names or subject_codes else score_query.filter(False)
    score_rows = score_query.order_by(Score.date.desc()).all()

    attendance = []
    for row in attendance_rows:
        subject = subject_by_id.get(row.subject_id)
        attendance.append({
            "id": row.id,
            "date": row.session_date,
            "status": row.status,
            "confidence": row.confidence,
            "is_manual_override": row.is_manual_override,
            "subject_id": row.subject_id,
            "subject_name": subject.name if subject else "General attendance",
            "subject_code": subject.code if subject else None,
        })

    marks = [{
        "id": row.id,
        "subject": row.subject,
        "score": row.score,
        "max_score": row.max_score,
        "percentage": round(row.score / row.max_score * 100, 1) if row.max_score else 0,
        "date": row.date,
    } for row in score_rows]

    latest_risk = db.query(RiskFlag).filter(RiskFlag.student_id == student_id).order_by(RiskFlag.calculated_at.desc()).first()
    risk = None
    if latest_risk:
        risk = {
            "level": latest_risk.risk_level,
            "confidence": latest_risk.confidence,
            "reasons": json.loads(latest_risk.reasons) if isinstance(latest_risk.reasons, str) else latest_risk.reasons,
            "computed_at": latest_risk.calculated_at,
        }

    return {
        "student": _student_dict(student, db),
        "subjects": [{"id": s.id, "name": s.name, "code": s.code} for s in subjects],
        "attendance": attendance,
        "marks": marks,
        "risk": risk,
        "scope": "all subjects" if current_user.role == "admin" else "assigned subjects",
    }


def _student_dict(s: Student, db: Session | None = None) -> dict:
    import json
    activities = json.loads(s.extracurricular) if s.extracurricular else []
    result = {
        "student_id": s.student_id,
        "name": s.name,
        "class": s.class_,
        "usn": s.usn,
        "phone": s.phone,
        "enrolled_at": s.enrolled_at,
        "is_active": s.is_active,
        "extracurricular": activities,
    }
    if db is None:
        return result

    attendance = db.query(Attendance).filter(Attendance.student_id == s.student_id).all()
    session_dates = {row[0] for row in db.query(Attendance.session_date).filter(Attendance.classroom_id == s.classroom_id).distinct().all()}
    present = sum(1 for row in attendance if row.status == "present")
    scores = db.query(Score).filter(Score.student_id == s.student_id).all()
    percentages = [row.score / row.max_score * 100 for row in scores if row.max_score and row.score is not None]
    risk = db.query(RiskFlag).filter(RiskFlag.student_id == s.student_id).order_by(RiskFlag.calculated_at.desc()).first()
    result.update({
        "attendance_pct": min(100.0, round(present / len(session_dates) * 100, 1)) if session_dates else 0,
        "average_score": round(sum(percentages) / len(percentages), 1) if percentages else None,
        "risk_level": risk.risk_level if risk else None,
        "risk_confidence": risk.confidence if risk else None,
    })
    return result


# ---------------------------------------------------------------------------
# Enrollment images — return sample face images for a student by USN
# ---------------------------------------------------------------------------

# Root of augmented data folder (relative to project root)
_AUG_DATA_ROOT = Path(__file__).resolve().parents[4] / "agumented data"
# Also check Downloads/enrol folder
_ENROL_DATA_ROOT = Path.home() / "Downloads" / "enrol"


@router.get("/{student_id}/images")
def get_student_images(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return up to 5 enrollment face images for a student as base64-encoded JPEGs."""
    # Verify student exists
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."})

    images = []

    # 1. Check Downloads/enrol folder first (original enrollment photos)
    if _ENROL_DATA_ROOT.exists():
        for folder in _ENROL_DATA_ROOT.iterdir():
            if not folder.is_dir():
                continue
            # Folder name ends with the USN (handle typos: 1DA23A001 -> 1DA23AI001)
            folder_usn = folder.name.split("_")[-1].upper()
            import re
            fixed_usn = re.sub(r'(1DA\d+)A(\d{3}$)', r'\1AI\2', folder_usn)
            if fixed_usn == student_id or folder_usn == student_id:
                for img in sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg")) + sorted(folder.glob("*.png")):
                    if len(images) >= 5:
                        break
                    try:
                        with open(img, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                        images.append({"source": "enrollment", "data": b64})
                    except Exception:
                        pass
                break

    # 2. Fallback: check augmented data folder
    if len(images) < 5 and _AUG_DATA_ROOT.exists():
        student_folder = _AUG_DATA_ROOT / student_id
        if student_folder.exists():
            # Pick first 5 images from the first subfolder
            subfolders = sorted(student_folder.iterdir())
            for sub in subfolders:
                if len(images) >= 5:
                    break
                if not sub.is_dir():
                    continue
                for img in sorted(sub.glob("*.jpg")) + sorted(sub.glob("*.jpeg")) + sorted(sub.glob("*.png")):
                    if len(images) >= 5:
                        break
                    try:
                        with open(img, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                        images.append({"source": "augmented", "data": b64})
                    except Exception:
                        pass

    return {
        "student_id": student_id,
        "name": student.name,
        "has_embedding": bool(student.embedding),
        "enrolled_at": student.enrolled_at,
        "images": images,
        "total": len(images),
    }
