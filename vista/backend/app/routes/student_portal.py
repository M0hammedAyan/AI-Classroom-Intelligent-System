"""
Student Portal API — Students view their own data only.
Features:
- Dashboard (attendance, scores, risk)
- Per-subject attendance breakdown
- Marks by subject with semester results
- Extracurricular activities
- Profile edit (name editable, USN editable ONCE)
- Subject list (what subjects are in my class)
- Theme preference
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Attendance, RiskFlag, Score
from ..models.organization import ClassSection, Subject, TeacherSubjectAssignment
from ..models.student import Student
from ..models.user import User
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/student-portal", tags=["student-portal"])


def _get_student_id(user: User) -> str:
    """Extract student_id from user. Student user IDs are 'student-{student_id}'."""
    if user.id.startswith("student-"):
        return user.id.replace("student-", "")
    raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Not a student account."})


def _require_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Student access only."})
    return current_user


@router.get("/dashboard")
def student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Student's personal dashboard — own attendance, scores, risk."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND"})

    # Total sessions in the classroom
    all_sessions = (
        db.query(Attendance.session_date)
        .filter(Attendance.classroom_id == student.classroom_id)
        .distinct()
        .all()
    )
    total_sessions = len(all_sessions)

    # Attendance stats
    att_rows = db.query(Attendance).filter(Attendance.student_id == sid).all()
    total_present = sum(1 for a in att_rows if a.status == "present")
    attendance_pct = round(total_present / max(total_sessions, 1) * 100, 1)

    # Scores
    score_rows = db.query(Score).filter(Score.student_id == sid).order_by(Score.date.desc()).all()
    avg_score = 0
    if score_rows:
        avg_score = round(sum(s.score / s.max_score * 100 for s in score_rows) / len(score_rows), 1)

    # Risk
    risk = db.query(RiskFlag).filter(RiskFlag.student_id == sid).order_by(RiskFlag.calculated_at.desc()).first()

    return {
        "student_id": sid,
        "name": student.name,
        "usn": student.usn,
        "class": student.class_,
        "total_present": total_present,
        "total_sessions": total_sessions,
        "attendance_pct": attendance_pct,
        "avg_score": avg_score,
        "assessments": len(score_rows),
        "risk_level": risk.risk_level if risk else "unknown",
        "risk_reasons": json.loads(risk.reasons) if risk else [],
        "risk_confidence": risk.confidence if risk else None,
    }


@router.get("/attendance")
def student_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Student views their own attendance history."""
    sid = _get_student_id(current_user)
    rows = db.query(Attendance).filter(Attendance.student_id == sid).order_by(Attendance.session_date.desc()).limit(90).all()
    return {
        "records": [
            {"date": r.session_date, "status": r.status, "confidence": r.confidence, "subject_id": r.subject_id}
            for r in rows
        ],
        "total": len(rows),
    }


@router.get("/attendance/by-subject")
def student_attendance_by_subject(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Per-subject attendance breakdown + overall average."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Overall attendance
    all_sessions = (
        db.query(Attendance.session_date)
        .filter(Attendance.classroom_id == student.classroom_id)
        .distinct()
        .all()
    )
    total_sessions = len(all_sessions)
    att_rows = db.query(Attendance).filter(Attendance.student_id == sid).all()
    total_present = sum(1 for a in att_rows if a.status == "present")
    overall_pct = round(total_present / max(total_sessions, 1) * 100, 1)

    # Find subjects for student's class
    class_section = db.query(ClassSection).filter(ClassSection.code == student.class_).first()
    subjects = []
    if class_section:
        assignments = (
            db.query(TeacherSubjectAssignment)
            .filter(TeacherSubjectAssignment.class_section_id == class_section.id, TeacherSubjectAssignment.is_active == True)
            .all()
        )
        subject_ids = list(set(a.subject_id for a in assignments))
        if subject_ids:
            subjects = db.query(Subject).filter(Subject.id.in_(subject_ids)).all()

    # Per-subject attendance (from records with subject_id)
    from collections import defaultdict
    subject_att = defaultdict(lambda: {"present": 0, "total": 0})
    subject_sessions = defaultdict(set)

    att_with_subject = [a for a in att_rows if a.subject_id]
    for a in att_with_subject:
        subject_sessions[a.subject_id].add(a.session_date)
        if a.status == "present":
            subject_att[a.subject_id]["present"] += 1

    breakdown = []
    for subj in subjects:
        total = len(subject_sessions.get(subj.id, set()))
        present = subject_att[subj.id]["present"]
        pct = round(present / total * 100, 1) if total > 0 else None
        breakdown.append({
            "subject_id": subj.id,
            "subject_name": subj.name,
            "subject_code": subj.code,
            "sessions_attended": present,
            "total_sessions": total,
            "attendance_pct": pct,
        })

    return {
        "overall": {"sessions_attended": total_present, "total_sessions": total_sessions, "attendance_pct": overall_pct},
        "by_subject": breakdown,
    }


@router.get("/scores")
def student_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Student views their own academic scores grouped by subject."""
    sid = _get_student_id(current_user)
    rows = db.query(Score).filter(Score.student_id == sid).order_by(Score.date.desc()).all()

    # Group by subject
    from collections import defaultdict
    by_subject = defaultdict(list)
    for r in rows:
        by_subject[r.subject].append({
            "score": r.score,
            "max_score": r.max_score,
            "date": r.date,
            "pct": round(r.score / r.max_score * 100, 1),
        })

    # Compute per-subject averages
    subjects_summary = []
    for subj, scores in by_subject.items():
        avg = round(sum(s["pct"] for s in scores) / len(scores), 1) if scores else 0
        subjects_summary.append({
            "subject": subj,
            "scores": scores,
            "average_pct": avg,
            "assessments": len(scores),
        })

    # Overall average
    all_pcts = [r.score / r.max_score * 100 for r in rows] if rows else []
    overall_avg = round(sum(all_pcts) / len(all_pcts), 1) if all_pcts else 0

    return {
        "overall_average": overall_avg,
        "total_assessments": len(rows),
        "by_subject": subjects_summary,
    }


@router.get("/risk")
def student_risk(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Student views their own risk assessment with explanation."""
    sid = _get_student_id(current_user)
    risk = db.query(RiskFlag).filter(RiskFlag.student_id == sid).order_by(RiskFlag.calculated_at.desc()).first()
    if not risk:
        return {"risk_level": "unknown", "reasons": [], "message": "No risk assessment computed yet."}

    return {
        "risk_level": risk.risk_level,
        "reasons": json.loads(risk.reasons) if risk.reasons else [],
        "confidence": risk.confidence,
        "computed_at": risk.calculated_at,
    }


@router.get("/subjects")
def student_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """List all subjects available for this student's class with teacher names."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_section = db.query(ClassSection).filter(ClassSection.code == student.class_).first()
    if not class_section:
        return {"subjects": [], "class": student.class_}

    assignments = (
        db.query(TeacherSubjectAssignment)
        .filter(TeacherSubjectAssignment.class_section_id == class_section.id, TeacherSubjectAssignment.is_active == True)
        .all()
    )

    subjects = []
    for a in assignments:
        subj = db.query(Subject).filter(Subject.id == a.subject_id).first()
        teacher = db.query(User).filter(User.id == a.teacher_id).first()
        if subj:
            subjects.append({
                "subject_id": subj.id,
                "subject_name": subj.name,
                "subject_code": subj.code,
                "semester": subj.semester,
                "teacher_name": teacher.name if teacher else "TBA",
                "teacher_email": teacher.email if teacher else None,
            })

    return {"subjects": subjects, "class": student.class_, "semester": class_section.semester}


@router.get("/extracurricular")
def student_extracurricular(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Get student's extracurricular activities."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    activities = json.loads(student.extracurricular) if student.extracurricular else []
    return {"activities": activities, "student_id": sid}


class UpdateExtracurricularRequest(BaseModel):
    activities: list[dict]  # [{"name": "...", "type": "...", "year": "...", "achievement": "..."}]


@router.put("/extracurricular")
def update_extracurricular(
    body: UpdateExtracurricularRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Update student's extracurricular activities."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.extracurricular = json.dumps(body.activities)
    db.commit()
    return {"status": "ok", "activities": body.activities}


# ---------------------------------------------------------------------------
# Profile Edit — Name always editable, USN editable ONCE only
# ---------------------------------------------------------------------------

class UpdateProfileRequest(BaseModel):
    name: str | None = None
    usn: str | None = None
    phone: str | None = None


@router.patch("/profile")
def update_student_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """
    Update student profile.
    - name: always editable
    - usn: editable ONLY ONCE (University Seat Number)
    - phone: always editable
    """
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if body.name is not None:
        student.name = body.name.strip()
        # Also update user record
        current_user.name = body.name.strip()

    if body.usn is not None:
        if student.usn_updated:
            raise HTTPException(status_code=400, detail={
                "code": "USN_ALREADY_SET",
                "message": "USN can only be updated once. Contact admin to change.",
            })
        student.usn = body.usn.strip().upper()
        student.usn_updated = True

    if body.phone is not None:
        student.phone = body.phone.strip()

    db.commit()

    return {
        "student_id": sid,
        "name": student.name,
        "usn": student.usn,
        "usn_locked": student.usn_updated,
        "phone": student.phone,
    }


@router.get("/profile")
def get_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Get full student profile."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    activities = json.loads(student.extracurricular) if student.extracurricular else []

    return {
        "student_id": sid,
        "name": student.name,
        "usn": student.usn,
        "usn_locked": student.usn_updated,
        "phone": student.phone,
        "class": student.class_,
        "enrolled_at": student.enrolled_at,
        "is_active": student.is_active,
        "extracurricular": activities,
        "theme": current_user.theme_preference or "light",
    }
