"""
Role-Specific Dashboard Data APIs
===================================
Each role gets scoped data for their dashboard.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Attendance, RiskFlag, Score
from ..models.student import Student
from ..models.user import User
from ..models.organization import Department, MentorAssignment, TeacherSubjectAssignment, Subject
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboards"])


@router.get("/admin")
def admin_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Admin: institution-wide stats."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    students = db.query(Student).filter(Student.is_active == True).count()
    teachers = db.query(User).filter(User.role == "teacher", User.is_active == True).count()
    mentors = db.query(User).filter(User.role == "mentor", User.is_active == True).count()

    flags = db.query(RiskFlag).all()
    # Get latest per student
    latest_flags = {}
    for f in flags:
        if f.student_id not in latest_flags or f.calculated_at > latest_flags[f.student_id].calculated_at:
            latest_flags[f.student_id] = f

    high = sum(1 for f in latest_flags.values() if f.risk_level == "high")
    medium = sum(1 for f in latest_flags.values() if f.risk_level == "medium")
    low = sum(1 for f in latest_flags.values() if f.risk_level == "low")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    present_today = db.query(Attendance).filter(Attendance.session_date == today, Attendance.status == "present").count()

    return {
        "students": students,
        "teachers": teachers,
        "mentors": mentors,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "present_today": present_today,
    }


@router.get("/hos")
def hos_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """HOS: school-scoped stats."""
    if current_user.role not in ("hos", "admin"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    school_id = current_user.school_id
    depts = db.query(Department).filter(Department.school_id == school_id, Department.is_active == True).all() if school_id else []
    dept_ids = [d.id for d in depts]

    teachers = db.query(User).filter(User.role == "teacher", User.department_id.in_(dept_ids)).count() if dept_ids else 0
    # Count students in the school (simplified — by classroom matching)
    students = db.query(Student).filter(Student.is_active == True).count()

    return {
        "departments": len(depts),
        "teachers": teachers,
        "students": students,
        "school_id": school_id,
    }


@router.get("/hop")
def hop_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """HOP: department-scoped stats."""
    if current_user.role not in ("hop", "admin", "hos"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    dept_id = current_user.department_id
    teachers = db.query(User).filter(User.role == "teacher", User.department_id == dept_id).count() if dept_id else 0
    subjects = db.query(Subject).filter(Subject.department_id == dept_id).count() if dept_id else 0
    students = db.query(Student).filter(Student.is_active == True).count()

    return {
        "teachers": teachers,
        "subjects": subjects,
        "students": students,
        "department_id": dept_id,
    }


@router.get("/teacher")
def teacher_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Teacher: classes + subjects they teach."""
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})

    assignments = (
        db.query(TeacherSubjectAssignment)
        .filter(TeacherSubjectAssignment.teacher_id == current_user.id, TeacherSubjectAssignment.is_active == True)
        .all()
    )

    subjects = set()
    classes = set()
    for a in assignments:
        subjects.add(a.subject_id)
        classes.add(a.class_section_id)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    present_today = db.query(Attendance).filter(Attendance.session_date == today, Attendance.status == "present").count()

    return {
        "my_subjects": len(subjects),
        "my_classes": len(classes),
        "present_today": present_today,
        "assignments": len(assignments),
    }


# ===========================================================================
# CHART DATA — For frontend visualizations
# ===========================================================================

@router.get("/charts/attendance-trend")
def attendance_trend(
    weeks: int = 8,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Weekly attendance trend for charts. Returns last N weeks of data."""
    from collections import defaultdict
    from datetime import timedelta

    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(weeks=weeks)

    rows = (
        db.query(Attendance)
        .filter(Attendance.session_date >= start_date.isoformat())
        .all()
    )

    # Group by week
    week_data = defaultdict(lambda: {"present": 0, "total": 0})
    for r in rows:
        try:
            d = datetime.strptime(r.session_date, "%Y-%m-%d").date()
            wk = f"W{d.isocalendar()[1]}"
            week_data[wk]["total"] += 1
            if r.status == "present":
                week_data[wk]["present"] += 1
        except ValueError:
            pass

    # Build sorted chart data
    chart = []
    for wk in sorted(week_data.keys()):
        d = week_data[wk]
        pct = round(d["present"] / d["total"] * 100, 1) if d["total"] > 0 else 0
        chart.append({"week": wk, "attendance_pct": pct, "sessions": d["total"]})

    return {"trend": chart, "weeks": weeks}


@router.get("/charts/risk-distribution")
def risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Risk level distribution for pie/donut chart."""
    from sqlalchemy import func

    # Latest risk per student
    subq = (
        db.query(RiskFlag.student_id, func.max(RiskFlag.calculated_at).label("latest"))
        .group_by(RiskFlag.student_id)
        .subquery()
    )
    flags = (
        db.query(RiskFlag)
        .join(subq, (RiskFlag.student_id == subq.c.student_id) & (RiskFlag.calculated_at == subq.c.latest))
        .all()
    )

    distribution = {"high": 0, "medium": 0, "low": 0}
    for f in flags:
        if f.risk_level in distribution:
            distribution[f.risk_level] += 1

    total = sum(distribution.values())
    return {
        "distribution": distribution,
        "total_students": total,
        "percentages": {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in distribution.items()},
    }


@router.get("/charts/subject-performance")
def subject_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Average score by subject for bar chart."""
    from collections import defaultdict

    scores = db.query(Score).all()
    subject_data = defaultdict(lambda: {"total": 0, "count": 0})

    for s in scores:
        pct = (s.score / s.max_score * 100) if s.max_score > 0 else 0
        subject_data[s.subject]["total"] += pct
        subject_data[s.subject]["count"] += 1

    chart = []
    for subj, data in subject_data.items():
        avg = round(data["total"] / data["count"], 1) if data["count"] > 0 else 0
        chart.append({"subject": subj, "average_pct": avg, "students": data["count"]})

    chart.sort(key=lambda x: x["average_pct"])
    return {"subjects": chart}
