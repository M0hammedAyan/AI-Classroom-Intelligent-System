"""
Student Portal API — Students view their own data only.
Features:
- Dashboard (attendance, scores, risk)
- Per-subject attendance breakdown
- Subject drill-down (date-wise history with source badges, CIE 1 & 2 marks)
- Marks by subject with CIE totals (/50)
- Extracurricular activities
- Profile edit (name editable, USN editable ONCE)
- Subject list (active subjects in my class)
- Theme preference
"""
from __future__ import annotations

import json
from collections import defaultdict
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
    """Enforce backend authorization: student accounts only."""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Student access only."})
    return current_user


def _get_student_class_section(db: Session, student: Student) -> ClassSection | None:
    """Resolve student's class section robustly by classroom_id, code, or name."""
    cs = db.query(ClassSection).filter(
        (ClassSection.id == student.classroom_id) |
        (ClassSection.code == student.classroom_id) |
        (ClassSection.code == student.class_) |
        (ClassSection.name == student.class_) |
        (ClassSection.id == "class-aiml-4a")
    ).first()
    return cs


def _get_class_subjects(db: Session, class_section: ClassSection | None) -> list[Subject]:
    """Get active subjects assigned to the class section."""
    subjects = []
    if class_section:
        assignments = (
            db.query(TeacherSubjectAssignment)
            .filter(TeacherSubjectAssignment.class_section_id == class_section.id, TeacherSubjectAssignment.is_active == True)
            .all()
        )
        subject_ids = list(set(a.subject_id for a in assignments))
        if subject_ids:
            subjects = db.query(Subject).filter(Subject.id.in_(subject_ids), Subject.is_active == True).order_by(Subject.code).all()

    if not subjects:
        dept_id = class_section.department_id if class_section else "dept-aiml"
        subjects = db.query(Subject).filter(Subject.department_id == dept_id, Subject.is_active == True).order_by(Subject.code).all()

    return subjects


@router.get("/dashboard")
def student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """
    Student's personal dashboard — own attendance, scores, risk.
    - Attendance percentage strictly between 0 and 100, formatted with at most 1 decimal.
    - Handles zero sessions gracefully with 'No sessions yet'.
    """
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": "Student record not found."})

    # Attendance stats for this student
    att_rows = db.query(Attendance).filter(Attendance.student_id == sid).all()
    total_present = sum(1 for a in att_rows if a.status == "present")
    total_sessions = len(att_rows)

    if total_sessions == 0:
        attendance_pct = None
        display_attendance = "No sessions yet"
    else:
        # Strict calculation bounded between 0 and 100 with at most 1 decimal
        attendance_pct = min(100.0, max(0.0, round((total_present / total_sessions) * 100, 1)))
        display_attendance = f"{attendance_pct}%"

    # Scores
    score_rows = db.query(Score).filter(Score.student_id == sid).order_by(Score.date.desc()).all()
    avg_score = 0.0
    if score_rows:
        valid_scores = [s.score / s.max_score * 100 for s in score_rows if s.max_score > 0]
        if valid_scores:
            avg_score = round(sum(valid_scores) / len(valid_scores), 1)

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
        "display_attendance": display_attendance,
        "avg_score": avg_score,
        "assessments": len(score_rows),
        "risk_level": risk.risk_level if risk else "unknown",
        "risk_reasons": json.loads(risk.reasons) if risk and risk.reasons else [],
        "risk_confidence": risk.confidence if risk else None,
    }


@router.get("/attendance")
def student_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Student views their own raw attendance history."""
    sid = _get_student_id(current_user)
    rows = db.query(Attendance).filter(Attendance.student_id == sid).order_by(Attendance.session_date.desc()).limit(150).all()
    return {
        "records": [
            {
                "date": r.session_date,
                "status": r.status,
                "confidence": r.confidence,
                "subject_id": r.subject_id,
                "source": r.source or ("manual" if r.is_manual_override else "face"),
            }
            for r in rows
        ],
        "total": len(rows),
    }


@router.get("/attendance/by-subject")
def student_attendance_by_subject(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Per-subject attendance breakdown + overall average for all class subjects."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_section = _get_student_class_section(db, student)
    subjects = _get_class_subjects(db, class_section)

    # Student attendance rows
    att_rows = db.query(Attendance).filter(Attendance.student_id == sid).all()

    breakdown = []
    total_present_all = 0
    total_sessions_all = 0

    for subj in subjects:
        subj_records = [
            a for a in att_rows
            if a.subject_id == subj.id or a.subject_id == subj.code or (a.subject_id and subj.code in a.subject_id)
        ]
        present_count = sum(1 for a in subj_records if a.status == "present")
        total_subj = len(subj_records)
        pct = min(100.0, max(0.0, round(present_count / total_subj * 100, 1))) if total_subj > 0 else None

        total_present_all += present_count
        total_sessions_all += total_subj

        breakdown.append({
            "subject_id": subj.id,
            "subject_name": subj.name,
            "subject_code": subj.code,
            "credits": subj.credits,
            "sessions_attended": present_count,
            "total_sessions": total_subj,
            "attendance_pct": pct,
        })

    overall_pct = min(100.0, max(0.0, round(total_present_all / total_sessions_all * 100, 1))) if total_sessions_all > 0 else None

    return {
        "overall": {
            "sessions_attended": total_present_all,
            "total_sessions": total_sessions_all,
            "attendance_pct": overall_pct,
        },
        "by_subject": breakdown,
    }


@router.get("/subjects/{subject_id}/detail")
def student_subject_detail(
    subject_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """
    Subject drill-down for student portal:
    - Subject metadata (name, code, credits, teacher)
    - Attendance summary: present / total sessions, percentage, and date-wise list with source badge (Face / Manual / Seed)
    - Marks: CIE 1 and CIE 2 (each out of 25), plus total out of 50
    """
    sid = _get_student_id(current_user)
    subj = db.query(Subject).filter((Subject.id == subject_id) | (Subject.code == subject_id)).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Attendance records
    att_records = db.query(Attendance).filter(
        Attendance.student_id == sid,
        (Attendance.subject_id == subj.id) | (Attendance.subject_id == subj.code) | (Attendance.subject_id.like(f"%{subj.code.lower()}%"))
    ).order_by(Attendance.session_date.desc()).all()

    present_count = sum(1 for a in att_records if a.status == "present")
    total_count = len(att_records)
    pct = min(100.0, max(0.0, round(present_count / total_count * 100, 1))) if total_count > 0 else None

    # Marks for this subject
    scores = db.query(Score).filter(
        Score.student_id == sid,
        (Score.subject == subj.name) | (Score.subject == subj.code) | (Score.subject == subj.id)
    ).order_by(Score.date.asc()).all()

    cie1 = next((s.score for s in scores if s.assessment_type == "CIE 1" or "CIE 1" in (s.subject or "")), None)
    cie2 = next((s.score for s in scores if s.assessment_type == "CIE 2" or "CIE 2" in (s.subject or "")), None)
    total_cie = None
    if cie1 is not None or cie2 is not None:
        total_cie = round((cie1 or 0.0) + (cie2 or 0.0), 1)

    # Teacher assignment
    assignment = db.query(TeacherSubjectAssignment).filter(
        TeacherSubjectAssignment.subject_id == subj.id,
        TeacherSubjectAssignment.is_active == True
    ).first()
    teacher = db.query(User).filter(User.id == assignment.teacher_id).first() if assignment else None

    return {
        "student": {"student_id": sid},
        "subject_id": subj.id,
        "subject_name": subj.name,
        "subject_code": subj.code,
        "credits": subj.credits,
        "teacher_name": teacher.name if teacher else "Faculty Assigned",
        "subject": {
            "id": subj.id,
            "name": subj.name,
            "code": subj.code,
            "credits": subj.credits or 4.0,
            "faculty": teacher.name if teacher else "Faculty Assigned",
        },
        "summary": {
            "total_sessions": total_count,
            "sessions_attended": present_count,
            "sessions_absent": total_count - present_count,
            "attendance_pct": pct,
        },
        "attendance": [
            {
                "date": a.session_date,
                "status": a.status,
                "source": a.source or ("manual" if a.is_manual_override else "face"),
                "confidence": a.confidence,
                "is_manual_override": a.is_manual_override,
                "note": a.override_note,
            }
            for a in att_records
        ],
        "marks": {
            "cie1": cie1,
            "cie2": cie2,
            "total": total_cie,
            "max_total": 50.0,
            "all_scores": [
                {
                    "assessment": s.assessment_type or "Assessment",
                    "score": s.score,
                    "max_score": s.max_score,
                    "date": s.date,
                    "source": s.source or "seed",
                }
                for s in scores
            ],
        },
    }


@router.get("/scores")
def student_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Student views their own academic scores grouped by subject with CIE 1 & CIE 2 breakdown."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_section = _get_student_class_section(db, student)
    subjects = _get_class_subjects(db, class_section)

    all_scores = db.query(Score).filter(Score.student_id == sid).order_by(Score.date.asc()).all()

    by_subject = defaultdict(list)
    for r in all_scores:
        by_subject[r.subject].append(r)

    subjects_summary = []
    all_pcts = []

    for subj in subjects:
        # Match scores for subject by name or code
        subj_scores = by_subject.get(subj.name, []) or by_subject.get(subj.code, [])
        score_dicts = [
            {
                "assessment": s.assessment_type or "CIE",
                "score": s.score,
                "max_score": s.max_score,
                "date": s.date,
                "source": s.source or "seed",
                "pct": round(s.score / s.max_score * 100, 1) if s.max_score > 0 else 0.0,
            }
            for s in subj_scores
        ]
        for s in score_dicts:
            all_pcts.append(s["pct"])

        cie1 = next((s["score"] for s in score_dicts if s["assessment"] == "CIE 1"), None)
        cie2 = next((s["score"] for s in score_dicts if s["assessment"] == "CIE 2"), None)
        total_cie = round((cie1 or 0.0) + (cie2 or 0.0), 1) if (cie1 is not None or cie2 is not None) else None
        avg_pct = round(sum(s["pct"] for s in score_dicts) / len(score_dicts), 1) if score_dicts else None

        subjects_summary.append({
            "subject_id": subj.id,
            "subject": subj.name,
            "subject_code": subj.code,
            "credits": subj.credits,
            "scores": score_dicts,
            "cie1": cie1,
            "cie2": cie2,
            "cie_total": total_cie,
            "max_cie_total": 50.0,
            "average_pct": avg_pct,
            "assessments": len(score_dicts),
        })

    overall_avg = round(sum(all_pcts) / len(all_pcts), 1) if all_pcts else 0.0

    return {
        "overall_average": overall_avg,
        "total_assessments": len(all_scores),
        "by_subject": subjects_summary,
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

    class_section = _get_student_class_section(db, student)
    subjects = _get_class_subjects(db, class_section)

    res = []
    for subj in subjects:
        assignment = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.subject_id == subj.id,
            TeacherSubjectAssignment.is_active == True
        ).first()
        teacher = db.query(User).filter(User.id == assignment.teacher_id).first() if assignment else None
        res.append({
            "subject_id": subj.id,
            "subject_name": subj.name,
            "subject_code": subj.code,
            "semester": subj.semester,
            "credits": subj.credits,
            "teacher_name": teacher.name if teacher else "Faculty Assigned",
            "teacher_email": teacher.email if teacher else None,
        })

    return {
        "subjects": res,
        "class": student.class_,
        "semester": class_section.semester if class_section else "7",
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
        return {"risk_level": "low", "reasons": [], "confidence": "high", "message": "No academic risk detected."}

    return {
        "risk_level": risk.risk_level,
        "reasons": json.loads(risk.reasons) if risk.reasons else [],
        "confidence": risk.confidence,
        "computed_at": risk.calculated_at,
    }


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
    activities: list[dict]


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
    """Update student profile."""
    sid = _get_student_id(current_user)
    student = db.query(Student).filter(Student.student_id == sid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if body.name is not None:
        student.name = body.name.strip()
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
