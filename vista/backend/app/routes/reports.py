"""Individual Student PDF Report — comprehensive academic + attendance + risk report."""
from __future__ import annotations

import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Attendance, Score, RiskFlag
from ..models.student import Student
from ..models.organization import MentorAssignment
from ..models.user import User
from ..routes.auth import get_current_user
from ..audit import log_action

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/student/{student_id}/pdf")
def student_report_pdf(
    student_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Generate a comprehensive PDF report for an individual student.
    Includes: personal info, attendance summary, score history, risk assessment, recommendations.
    Access: Admin, HOS, HOP, Mentor (assigned), Teacher (own class), Student (own report).
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Access control: students can only see their own report
    if current_user.role == "student" and current_user.id != f"student-{student_id}":
        raise HTTPException(status_code=403, detail="Access denied")

    # Gather data
    attendance_rows = (
        db.query(Attendance)
        .filter(Attendance.student_id == student_id)
        .order_by(Attendance.session_date)
        .all()
    )

    # Total sessions for the classroom
    total_sessions_q = (
        db.query(Attendance.session_date)
        .filter(Attendance.classroom_id == student.classroom_id)
        .distinct()
        .all()
    )
    total_sessions = len(total_sessions_q)
    sessions_present = sum(1 for a in attendance_rows if a.status == "present")
    att_pct = (sessions_present / total_sessions * 100) if total_sessions > 0 else 0

    scores = (
        db.query(Score)
        .filter(Score.student_id == student_id)
        .order_by(Score.date)
        .all()
    )

    latest_risk = (
        db.query(RiskFlag)
        .filter(RiskFlag.student_id == student_id)
        .order_by(RiskFlag.calculated_at.desc())
        .first()
    )

    # Mentor info
    mentor_assignment = (
        db.query(MentorAssignment)
        .filter(MentorAssignment.student_id == student_id, MentorAssignment.is_active == True)
        .first()
    )
    mentor_name = None
    if mentor_assignment:
        mentor_user = db.query(User).filter(User.id == mentor_assignment.mentor_id).first()
        mentor_name = mentor_user.name if mentor_user else None

    # Build PDF
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=18, spaceAfter=6, textColor=colors.HexColor("#1e1b4b"),
    )
    heading_style = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontSize=13, spaceAfter=8, spaceBefore=16,
        textColor=colors.HexColor("#312e81"),
    )
    normal = styles['Normal']

    elements = []

    # Header
    elements.append(Paragraph("VISTA — Student Academic Report", title_style))
    elements.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%d %B %Y, %H:%M UTC')}",
        ParagraphStyle('DateStyle', parent=normal, fontSize=9, textColor=colors.grey),
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e7ff")))
    elements.append(Spacer(1, 0.5*cm))

    # Student Info Section
    elements.append(Paragraph("Student Information", heading_style))
    info_data = [
        ["Student ID", student_id],
        ["Name", student.name],
        ["Class", student.class_ or "—"],
        ["Enrolled", student.enrolled_at or "—"],
        ["Status", "Active" if student.is_active else "Inactive"],
        ["Assigned Mentor", mentor_name or "Not assigned"],
    ]
    info_table = Table(info_data, colWidths=[4.5*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    # Attendance Section
    elements.append(Paragraph("Attendance Summary", heading_style))
    att_data = [
        ["Total Sessions", str(total_sessions)],
        ["Sessions Present", str(sessions_present)],
        ["Sessions Absent", str(total_sessions - sessions_present)],
        ["Attendance %", f"{att_pct:.1f}%"],
    ]
    att_table = Table(att_data, colWidths=[4.5*cm, 12*cm])
    att_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(att_table)

    # Color-coded attendance status
    if att_pct >= 75:
        att_status_color = "#16a34a"
        att_status = "✓ Above minimum requirement (75%)"
    elif att_pct >= 60:
        att_status_color = "#ca8a04"
        att_status = "⚠ Below 75% — shortage warning"
    else:
        att_status_color = "#dc2626"
        att_status = "✗ Critical attendance shortage"

    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        f'<font color="{att_status_color}"><b>{att_status}</b></font>', normal
    ))
    elements.append(Spacer(1, 0.5*cm))

    # Scores Section
    elements.append(Paragraph("Assessment Scores", heading_style))
    if scores:
        score_header = ["#", "Subject", "Score", "Max", "%", "Date"]
        score_data = [score_header]
        for i, s in enumerate(scores, 1):
            pct = (s.score / s.max_score * 100) if s.max_score > 0 else 0
            score_data.append([
                str(i), s.subject or "—",
                f"{s.score:.0f}", f"{s.max_score:.0f}",
                f"{pct:.0f}%", s.date or "—",
            ])

        score_table = Table(score_data, colWidths=[1*cm, 5*cm, 2*cm, 2*cm, 2*cm, 3*cm])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(score_table)

        # Average
        avg_score = sum(s.score for s in scores) / len(scores)
        avg_max = sum(s.max_score for s in scores) / len(scores)
        avg_pct = (avg_score / avg_max * 100) if avg_max > 0 else 0
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(f"<b>Average Score:</b> {avg_score:.1f}/{avg_max:.0f} ({avg_pct:.1f}%)", normal))
    else:
        elements.append(Paragraph("<i>No assessment scores recorded.</i>", normal))

    elements.append(Spacer(1, 0.5*cm))

    # Risk Assessment Section
    elements.append(Paragraph("Risk Assessment", heading_style))
    if latest_risk:
        risk_color = {"high": "#dc2626", "medium": "#ca8a04", "low": "#16a34a"}.get(
            latest_risk.risk_level, "#6b7280"
        )
        elements.append(Paragraph(
            f'<b>Current Risk Level:</b> <font color="{risk_color}"><b>{latest_risk.risk_level.upper()}</b></font>'
            f' (Confidence: {latest_risk.confidence})',
            normal,
        ))
        elements.append(Spacer(1, 3*mm))

        reasons = json.loads(latest_risk.reasons) if isinstance(latest_risk.reasons, str) else latest_risk.reasons
        if reasons:
            elements.append(Paragraph("<b>Risk Factors:</b>", normal))
            for r in reasons:
                elements.append(Paragraph(f"  • {r}", normal))

        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(f"<i>Last computed: {latest_risk.calculated_at}</i>",
            ParagraphStyle('SmallItalic', parent=normal, fontSize=8, textColor=colors.grey)))
    else:
        elements.append(Paragraph("<i>Risk has not been computed for this student.</i>", normal))

    elements.append(Spacer(1, 0.5*cm))

    # Recommendations
    elements.append(Paragraph("Recommendations", heading_style))
    recommendations = []
    if att_pct < 75:
        recommendations.append("Improve attendance — current rate below 75% minimum requirement.")
    if att_pct < 60:
        recommendations.append("URGENT: Meet with mentor to discuss attendance crisis.")
    if scores and avg_pct < 40:
        recommendations.append("Academic performance critically low — remedial classes recommended.")
    elif scores and avg_pct < 60:
        recommendations.append("Below-average academic performance — additional tutoring suggested.")
    if latest_risk and latest_risk.risk_level == "high":
        recommendations.append("HIGH risk flag active — intervention required from mentor/HOP.")
    if not recommendations:
        recommendations.append("Student is performing well. Continue current trajectory.")

    for r in recommendations:
        elements.append(Paragraph(f"→ {r}", normal))

    # Footer
    elements.append(Spacer(1, 1.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d1d5db")))
    elements.append(Paragraph(
        "VISTA — AI Classroom Intelligent System | Confidential Academic Report",
        ParagraphStyle('Footer', parent=normal, fontSize=8, textColor=colors.grey, alignment=TA_CENTER),
    ))

    doc.build(elements)
    buffer.seek(0)

    filename = f"VISTA_Report_{student_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ===========================================================================
# Part 4: Comprehensive Student and Teacher Reports
# ===========================================================================
from ..cie_policy import evaluate_cie
from ..models.organization import Subject, ClassSection, TeacherSubjectAssignment
from ..models.timetable import TimetableSlot
from ..models.capture import CaptureEvent
from ..services.coach_service import compute_missable_classes, compute_recovery_classes


def _authorize_student_report_access(student_id: str, current_user: User, db: Session) -> Student:
    """Central authorization helper for student reports. Returns Student or raises 403/404."""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    if current_user.role == "admin":
        return student

    if current_user.role == "student":
        # Extract student ID from user.id (e.g. "student-1DA24AI403" -> "1DA24AI403")
        current_sid = current_user.id.replace("student-", "")
        if current_sid != student_id:
            raise HTTPException(status_code=403, detail="Forbidden: You may only view your own academic report.")
        return student

    if current_user.role == "teacher":
        # Teacher must be assigned to student's class section or be student's mentor
        is_assigned = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == current_user.id,
            TeacherSubjectAssignment.class_section_id == student.classroom_id,
            TeacherSubjectAssignment.is_active == True,
        ).first()
        is_mentor = db.query(MentorAssignment).filter(
            MentorAssignment.mentor_id == current_user.id,
            MentorAssignment.student_id == student_id,
            MentorAssignment.is_active == True,
        ).first()
        if not is_assigned and not is_mentor:
            raise HTTPException(status_code=403, detail="Forbidden: Teacher is not assigned to this student's class section.")
        return student

    raise HTTPException(status_code=403, detail="Forbidden: Unauthorized role.")


def _authorize_teacher_report_access(teacher_id: str, current_user: User, db: Session) -> User:
    """Central authorization helper for teacher reports. Returns teacher User or raises 403/404."""
    teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    if current_user.role == "admin":
        return teacher

    if current_user.role == "teacher":
        if current_user.id != teacher_id:
            raise HTTPException(status_code=403, detail="Forbidden: Teachers may only view their own teaching report.")
        return teacher

    raise HTTPException(status_code=403, detail="Forbidden: Students cannot access teacher reports.")


def build_student_report_data(student: Student, db: Session) -> dict:
    """Builds comprehensive student report: attendance by subject/period, CIE 1/2/3, and risk evaluation."""
    att_rows = db.query(Attendance).filter(Attendance.student_id == student.student_id).all()
    total_sessions = len(att_rows)
    attended_sessions = sum(1 for a in att_rows if a.status == "present")
    att_pct = round((attended_sessions / total_sessions) * 100.0, 1) if total_sessions > 0 else 0.0
    att_pct = min(100.0, max(0.0, att_pct))

    missable = compute_missable_classes(attended_sessions, total_sessions)
    recovery = compute_recovery_classes(attended_sessions, total_sessions)

    overall_sources = {"face": 0, "manual": 0, "seed": 0}
    for a in att_rows:
        src = a.source or ("manual" if a.is_manual_override else "face")
        if src in overall_sources:
            overall_sources[src] += 1
        else:
            overall_sources[src] = 1

    # Active subjects (excluding placeholder IDE-UNCONFIRMED per project decision)
    subjects = db.query(Subject).filter(
        Subject.is_active == True,
        Subject.code != "IDE-UNCONFIRMED",
    ).all()

    subject_reports = []
    for s in subjects:
        subj_att = [a for a in att_rows if a.subject_id in (s.id, s.code) or (a.subject_id and s.code.lower() in a.subject_id.lower())]
        s_total = len(subj_att)
        s_attended = sum(1 for a in subj_att if a.status == "present")
        s_pct = round((s_attended / s_total) * 100.0, 1) if s_total > 0 else None

        # Period breakdown
        period_data = {}
        for p in ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
            p_rows = [a for a in subj_att if a.period_label == p]
            p_tot = len(p_rows)
            p_att = sum(1 for a in p_rows if a.status == "present")
            period_data[p] = {
                "total": p_tot,
                "attended": p_att,
                "percentage": round((p_att / p_tot) * 100.0, 1) if p_tot > 0 else None,
            }

        s_sources = {"face": 0, "manual": 0, "seed": 0}
        for a in subj_att:
            src = a.source or ("manual" if a.is_manual_override else "face")
            s_sources[src] = s_sources.get(src, 0) + 1

        cie_eval = evaluate_cie(student_id=student.student_id, subject=s.name, db=db)

        subject_reports.append({
            "subject_id": s.id,
            "subject_code": s.code,
            "subject_name": s.name,
            "credits": s.credits or 4.0,
            "attendance": {
                "total": s_total,
                "attended": s_attended,
                "percentage": s_pct,
                "periods": period_data,
                "by_source": s_sources,
            },
            "cie": cie_eval,
        })

    # Risk evaluation
    latest_risk = (
        db.query(RiskFlag)
        .filter(RiskFlag.student_id == student.student_id)
        .order_by(RiskFlag.calculated_at.desc())
        .first()
    )
    risk_info = None
    if latest_risk:
        try:
            reasons = json.loads(latest_risk.reasons) if isinstance(latest_risk.reasons, str) else latest_risk.reasons
        except Exception:
            reasons = []
        risk_info = {
            "level": latest_risk.risk_level.upper(),
            "confidence": latest_risk.confidence,
            "reasons": reasons,
            "calculated_at": latest_risk.calculated_at,
        }

    class_sec = db.query(ClassSection).filter(ClassSection.id == student.classroom_id).first()
    class_code = class_sec.code if class_sec else (student.class_ or "AIML-4A")

    return {
        "student": {
            "student_id": student.student_id,
            "name": student.name,
            "classroom_id": student.classroom_id,
            "class_code": class_code,
            "batch": student.batch,
            "enrolled_at": student.enrolled_at,
            "is_active": student.is_active,
        },
        "overall_attendance": {
            "total_sessions": total_sessions,
            "attended_sessions": attended_sessions,
            "percentage": att_pct,
            "missable_classes": missable,
            "recovery_classes_needed": recovery,
            "by_source": overall_sources,
        },
        "subjects": subject_reports,
        "academic_risk": risk_info,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_teacher_report_data(teacher: User, db: Session) -> dict:
    """Builds comprehensive teacher report: scheduled vs held, extra classes, average attendance."""
    assignments = db.query(TeacherSubjectAssignment).filter(
        TeacherSubjectAssignment.teacher_id == teacher.id,
        TeacherSubjectAssignment.is_active == True,
    ).all()
    subject_ids = [a.subject_id for a in assignments]
    subjects = db.query(Subject).filter(Subject.id.in_(subject_ids)).all() if subject_ids else []
    subj_map = {s.id: s for s in subjects}

    # Weekly scheduled slots
    slots = db.query(TimetableSlot).filter(
        TimetableSlot.teacher_id == teacher.id,
        TimetableSlot.is_active == True,
    ).all()
    scheduled_weekly_count = len(slots)

    # Attendance records
    att_records = db.query(Attendance).filter(
        Attendance.subject_id.in_(subject_ids)
    ).all() if subject_ids else []

    # Group sessions by (session_date, subject_id, period_label)
    sessions_dict = {}
    for a in att_records:
        k = (a.session_date, a.subject_id, a.period_label or "S1")
        if k not in sessions_dict:
            sessions_dict[k] = {
                "date": a.session_date,
                "subject_id": a.subject_id,
                "period_label": a.period_label or "S1",
                "present_count": 0,
                "absent_count": 0,
                "is_extra_class": bool(getattr(a, "is_extra_class", False)),
                "extra_class_reason": getattr(a, "extra_class_reason", None),
                "sources": set(),
            }
        if a.status == "present":
            sessions_dict[k]["present_count"] += 1
        else:
            sessions_dict[k]["absent_count"] += 1
        if a.source:
            sessions_dict[k]["sources"].add(a.source)

    held_sessions = list(sessions_dict.values())
    held_count = len(held_sessions)
    extra_count = sum(1 for s in held_sessions if s["is_extra_class"])
    manual_count = sum(1 for a in att_records if a.is_manual_override)

    # Face captures
    captures = db.query(CaptureEvent).filter(CaptureEvent.teacher_id == teacher.id).all()
    captures_count = len(captures)

    # Subject summaries
    subject_summaries = []
    for s in subjects:
        s_sess = [sess for sess in held_sessions if sess["subject_id"] == s.id]
        pcts = []
        for sess in s_sess:
            tot = sess["present_count"] + sess["absent_count"]
            if tot > 0:
                pcts.append((sess["present_count"] / tot) * 100.0)
        avg_pct = round(sum(pcts) / len(pcts), 1) if pcts else None
        subject_summaries.append({
            "subject_id": s.id,
            "subject_code": s.code,
            "subject_name": s.name,
            "classes_held": len(s_sess),
            "average_attendance_pct": avg_pct,
        })

    # Recent 50 daily sessions
    recent_sessions = []
    for sess in sorted(held_sessions, key=lambda x: x["date"], reverse=True)[:50]:
        s = subj_map.get(sess["subject_id"])
        recent_sessions.append({
            "date": sess["date"],
            "subject_code": s.code if s else "N/A",
            "subject_name": s.name if s else "N/A",
            "period_label": sess["period_label"],
            "present_count": sess["present_count"],
            "absent_count": sess["absent_count"],
            "is_extra_class": sess["is_extra_class"],
            "extra_class_reason": sess["extra_class_reason"],
            "sources": list(sess["sources"]),
        })

    return {
        "teacher": {
            "teacher_id": teacher.id,
            "name": teacher.name,
            "email": teacher.email,
            "department_id": teacher.department_id,
        },
        "summary": {
            "scheduled_slots_per_week": scheduled_weekly_count,
            "held_sessions_count": held_count,
            "extra_classes_count": extra_count,
            "captures_count": captures_count,
            "manual_corrections_count": manual_count,
        },
        "subjects": subject_summaries,
        "recent_sessions": recent_sessions,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/student/me")
def get_my_student_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns authenticated student's academic report (attendance by subject/period, CIE 1/2/3, risk)."""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can call /reports/student/me.")
    student_id = current_user.id.replace("student-", "")
    student = _authorize_student_report_access(student_id, current_user, db)
    result = build_student_report_data(student, db)
    log_action(db, user_id=current_user.id, action="generate_student_report",
               target_type="student_report", target_id=student_id,
               details='{{"student_id":"{}","format":"json"}}'.format(student_id))
    db.commit()
    return result


@router.get("/student/{student_id}")
def get_student_report_by_id(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns student's report with central authorization (Admin, Teacher, or self)."""
    student = _authorize_student_report_access(student_id, current_user, db)
    result = build_student_report_data(student, db)
    log_action(db, user_id=current_user.id, action="generate_student_report",
               target_type="student_report", target_id=student_id,
               details='{{"student_id":"{}","format":"json","by":"{}"}}'.format(student_id, current_user.role))
    db.commit()
    return result


@router.get("/teacher/me")
def get_my_teacher_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns authenticated teacher's report (scheduled vs held, extra classes, captures, average attendance)."""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can call /reports/teacher/me.")
    teacher = _authorize_teacher_report_access(current_user.id, current_user, db)
    result = build_teacher_report_data(teacher, db)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=current_user.id,
               details='{{"teacher_id":"{}","format":"json"}}'.format(current_user.id))
    db.commit()
    return result


@router.get("/teacher/{teacher_id}")
def get_teacher_report_by_id(
    teacher_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns teacher's report with central authorization (Admin or self)."""
    teacher = _authorize_teacher_report_access(teacher_id, current_user, db)
    result = build_teacher_report_data(teacher, db)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=teacher_id,
               details='{{"teacher_id":"{}","format":"json","by":"{}"}}'.format(teacher_id, current_user.role))
    db.commit()
    return result


# ===========================================================================
# Part 4 (completion): CSV exports and Teacher PDF
# ===========================================================================

def _csv_escape(value) -> str:
    """Sanitize CSV cell to prevent formula injection (leading =, +, -, @, TAB, CR)."""
    s = str(value) if value is not None else ""
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        s = "'" + s
    return s


def _build_student_csv(student_data: dict) -> str:
    """Build a CSV string from student report data dict."""
    import csv as _csv
    output = io.StringIO()
    w = _csv.writer(output)

    s = student_data["student"]
    oa = student_data["overall_attendance"]
    risk = student_data.get("academic_risk") or {}

    w.writerow(["VISTA Student Academic Report"])
    w.writerow(["Generated", _csv_escape(student_data.get("generated_at", ""))])
    w.writerow([])
    w.writerow(["Student ID", _csv_escape(s["student_id"])])
    w.writerow(["Name", _csv_escape(s["name"])])
    w.writerow(["Class", _csv_escape(s.get("class_code", ""))])
    w.writerow(["Batch", _csv_escape(s.get("batch", ""))])
    w.writerow(["Enrolled At", _csv_escape(s.get("enrolled_at", ""))])
    w.writerow(["Status", "Active" if s.get("is_active") else "Inactive"])
    w.writerow([])
    w.writerow(["--- Overall Attendance ---"])
    w.writerow(["Total Sessions", oa["total_sessions"]])
    w.writerow(["Attended", oa["attended_sessions"]])
    w.writerow(["Percentage", "{:.1f}%".format(oa["percentage"])])
    w.writerow(["Missable Classes Remaining", oa.get("missable_classes", "N/A")])
    w.writerow(["Recovery Classes Needed", oa.get("recovery_classes_needed", "N/A")])
    w.writerow([])
    w.writerow(["--- Subject-Wise Report ---"])
    w.writerow([
        "Subject Code", "Subject Name", "Credits",
        "Total", "Attended", "Attendance %",
        "CIE-1", "CIE-2", "CIE-3", "Eligible",
        "S1-tot", "S1-att", "S2-tot", "S2-att",
        "S3-tot", "S3-att", "S4-tot", "S4-att",
        "S5-tot", "S5-att", "S6-tot", "S6-att",
        "S7-tot", "S7-att",
    ])
    for subj in student_data.get("subjects", []):
        att = subj["attendance"]
        cie = subj.get("cie") or {}
        marks = cie.get("marks") or {}
        periods = att.get("periods") or {}

        def p(label):
            pd = periods.get(label) or {}
            return [pd.get("total", 0), pd.get("attended", 0)]

        pct_str = "{:.1f}%".format(att["percentage"]) if att.get("percentage") is not None else "N/A"
        w.writerow([
            _csv_escape(subj["subject_code"]),
            _csv_escape(subj["subject_name"]),
            subj.get("credits", ""),
            att["total"], att["attended"],
            pct_str,
            marks.get("cie1", ""), marks.get("cie2", ""), marks.get("cie3", ""),
            "Yes" if cie.get("eligible") else "No",
            *p("S1"), *p("S2"), *p("S3"), *p("S4"), *p("S5"), *p("S6"), *p("S7"),
        ])

    w.writerow([])
    w.writerow(["--- Academic Risk ---"])
    if risk:
        w.writerow(["Risk Level", _csv_escape(risk.get("level", ""))])
        w.writerow(["Confidence", _csv_escape(risk.get("confidence", ""))])
        w.writerow(["Calculated At", _csv_escape(risk.get("calculated_at", ""))])
        for reason in (risk.get("reasons") or []):
            w.writerow(["Reason", _csv_escape(reason)])
    else:
        w.writerow(["Risk Level", "Not computed"])

    return output.getvalue()


def _build_teacher_csv(teacher_data: dict) -> str:
    """Build a CSV string from teacher report data dict."""
    import csv as _csv
    output = io.StringIO()
    w = _csv.writer(output)

    t = teacher_data["teacher"]
    s = teacher_data["summary"]

    w.writerow(["VISTA Teacher Teaching Report"])
    w.writerow(["Generated", _csv_escape(teacher_data.get("generated_at", ""))])
    w.writerow([])
    w.writerow(["Teacher ID", _csv_escape(t["teacher_id"])])
    w.writerow(["Name", _csv_escape(t["name"])])
    w.writerow(["Email", _csv_escape(t["email"])])
    w.writerow([])
    w.writerow(["--- Teaching Summary ---"])
    w.writerow(["Scheduled Slots/Week", s["scheduled_slots_per_week"]])
    w.writerow(["Held Sessions", s["held_sessions_count"]])
    w.writerow(["Extra Classes", s["extra_classes_count"]])
    w.writerow(["Face Captures", s["captures_count"]])
    w.writerow(["Manual Corrections", s["manual_corrections_count"]])
    w.writerow([])
    w.writerow(["--- Subject Summary ---"])
    w.writerow(["Subject Code", "Subject Name", "Classes Held", "Avg Attendance %"])
    for subj in teacher_data.get("subjects", []):
        avg = subj.get("average_attendance_pct")
        w.writerow([
            _csv_escape(subj["subject_code"]),
            _csv_escape(subj["subject_name"]),
            subj["classes_held"],
            "{:.1f}%".format(avg) if avg is not None else "N/A",
        ])
    w.writerow([])
    w.writerow(["--- Recent Sessions (last 50) ---"])
    w.writerow(["Date", "Subject Code", "Subject Name", "Period", "Present", "Absent", "Extra Class", "Reason", "Sources"])
    for sess in teacher_data.get("recent_sessions", []):
        w.writerow([
            _csv_escape(sess["date"]),
            _csv_escape(sess["subject_code"]),
            _csv_escape(sess["subject_name"]),
            _csv_escape(sess["period_label"]),
            sess["present_count"],
            sess["absent_count"],
            "Yes" if sess["is_extra_class"] else "No",
            _csv_escape(sess.get("extra_class_reason") or ""),
            _csv_escape(",".join(sess.get("sources") or [])),
        ])

    return output.getvalue()


@router.get("/student/me/csv")
def get_my_student_report_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download authenticated student's report as CSV."""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can call /reports/student/me/csv.")
    student_id = current_user.id.replace("student-", "")
    student = _authorize_student_report_access(student_id, current_user, db)
    report_data = build_student_report_data(student, db)
    csv_content = _build_student_csv(report_data)
    log_action(db, user_id=current_user.id, action="generate_student_report",
               target_type="student_report", target_id=student_id,
               details='{{"student_id":"{}","format":"csv"}}'.format(student_id))
    db.commit()
    filename = "VISTA_Student_{}_{}.csv".format(student_id, datetime.now().strftime("%Y%m%d"))
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="{}"'.format(filename)},
    )


@router.get("/student/{student_id}/csv")
def get_student_report_csv(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download student report as CSV. Access: Admin, Teacher (assigned class), Student (own)."""
    student = _authorize_student_report_access(student_id, current_user, db)
    report_data = build_student_report_data(student, db)
    csv_content = _build_student_csv(report_data)
    log_action(db, user_id=current_user.id, action="generate_student_report",
               target_type="student_report", target_id=student_id,
               details='{{"student_id":"{}","format":"csv","by":"{}"}}'.format(student_id, current_user.role))
    db.commit()
    filename = "VISTA_Student_{}_{}.csv".format(student_id, datetime.now().strftime("%Y%m%d"))
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="{}"'.format(filename)},
    )


@router.get("/teacher/me/csv")
def get_my_teacher_report_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download authenticated teacher's report as CSV."""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can call /reports/teacher/me/csv.")
    teacher = _authorize_teacher_report_access(current_user.id, current_user, db)
    report_data = build_teacher_report_data(teacher, db)
    csv_content = _build_teacher_csv(report_data)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=current_user.id,
               details='{{"teacher_id":"{}","format":"csv"}}'.format(current_user.id))
    db.commit()
    filename = "VISTA_Teacher_{}_{}.csv".format(current_user.id, datetime.now().strftime("%Y%m%d"))
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="{}"'.format(filename)},
    )


@router.get("/teacher/{teacher_id}/csv")
def get_teacher_report_csv(
    teacher_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download teacher report as CSV. Access: Admin or teacher (own)."""
    teacher = _authorize_teacher_report_access(teacher_id, current_user, db)
    report_data = build_teacher_report_data(teacher, db)
    csv_content = _build_teacher_csv(report_data)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=teacher_id,
               details='{{"teacher_id":"{}","format":"csv","by":"{}"}}'.format(teacher_id, current_user.role))
    db.commit()
    filename = "VISTA_Teacher_{}_{}.csv".format(teacher_id, datetime.now().strftime("%Y%m%d"))
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="{}"'.format(filename)},
    )


@router.get("/teacher/me/pdf")
def get_my_teacher_report_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download authenticated teacher's teaching report as PDF."""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can call /reports/teacher/me/pdf.")
    teacher = _authorize_teacher_report_access(current_user.id, current_user, db)
    result = _build_teacher_pdf(teacher, db)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=current_user.id,
               details='{{"teacher_id":"{}","format":"pdf"}}'.format(current_user.id))
    db.commit()
    return result


@router.get("/teacher/{teacher_id}/pdf")
def get_teacher_report_pdf(
    teacher_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download teacher report as PDF. Access: Admin or teacher (own)."""
    teacher = _authorize_teacher_report_access(teacher_id, current_user, db)
    result = _build_teacher_pdf(teacher, db)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=teacher_id,
               details='{{"teacher_id":"{}","format":"pdf","by":"{}"}}'.format(teacher_id, current_user.role))
    db.commit()
    return result


def _build_teacher_pdf(teacher: User, db: Session) -> StreamingResponse:
    """Generate a comprehensive PDF report for a teacher."""
    report_data = build_teacher_report_data(teacher, db)
    t = report_data["teacher"]
    s = report_data["summary"]

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=18, spaceAfter=6, textColor=colors.HexColor("#1e1b4b"),
    )
    heading_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"],
        fontSize=13, spaceAfter=8, spaceBefore=16,
        textColor=colors.HexColor("#312e81"),
    )
    normal = styles["Normal"]

    elements = []
    elements.append(Paragraph("VISTA -- Teacher Teaching Report", title_style))
    elements.append(Paragraph(
        "Generated: {}".format(datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")),
        ParagraphStyle("DateStyle", parent=normal, fontSize=9, textColor=colors.grey),
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e7ff")))
    elements.append(Spacer(1, 0.5*cm))

    # Teacher Info
    elements.append(Paragraph("Teacher Information", heading_style))
    info_data = [
        ["Teacher ID", t["teacher_id"]],
        ["Name", t["name"]],
        ["Email", t["email"]],
        ["Department ID", t.get("department_id") or "N/A"],
    ]
    info_table = Table(info_data, colWidths=[4.5*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5*cm))

    # Teaching Summary
    elements.append(Paragraph("Teaching Summary", heading_style))
    summary_data = [
        ["Scheduled Slots/Week", str(s["scheduled_slots_per_week"])],
        ["Held Sessions (All Time)", str(s["held_sessions_count"])],
        ["Extra Classes Taken", str(s["extra_classes_count"])],
        ["Face Capture Events", str(s["captures_count"])],
        ["Manual Attendance Corrections", str(s["manual_corrections_count"])],
    ]
    summary_table = Table(summary_data, colWidths=[6*cm, 10.5*cm])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # Subject Summary
    elements.append(Paragraph("Subject-Wise Performance", heading_style))
    if report_data.get("subjects"):
        subj_header = ["Subject Code", "Subject Name", "Classes Held", "Avg Attendance %"]
        subj_data = [subj_header]
        for subj in report_data["subjects"]:
            avg = subj.get("average_attendance_pct")
            subj_data.append([
                subj["subject_code"],
                subj["subject_name"],
                str(subj["classes_held"]),
                "{:.1f}%".format(avg) if avg is not None else "N/A",
            ])
        subj_table = Table(subj_data, colWidths=[3.5*cm, 6.5*cm, 3*cm, 3.5*cm])
        subj_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(subj_table)
    else:
        elements.append(Paragraph("<i>No subject assignments found.</i>", normal))

    elements.append(Spacer(1, 0.5*cm))

    # Recent Sessions
    elements.append(Paragraph("Recent Sessions (last 50)", heading_style))
    if report_data.get("recent_sessions"):
        sess_header = ["Date", "Subject", "Period", "Present", "Absent", "Extra"]
        sess_data = [sess_header]
        for sess in report_data["recent_sessions"]:
            sess_data.append([
                sess["date"],
                sess["subject_code"],
                sess["period_label"],
                str(sess["present_count"]),
                str(sess["absent_count"]),
                "Yes" if sess["is_extra_class"] else "No",
            ])
        sess_table = Table(sess_data, colWidths=[2.5*cm, 2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm])
        sess_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(sess_table)
    else:
        elements.append(Paragraph("<i>No sessions recorded yet.</i>", normal))

    # Footer
    elements.append(Spacer(1, 1.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d1d5db")))
    elements.append(Paragraph(
        "VISTA -- AI Classroom Intelligent System | Confidential Teaching Report",
        ParagraphStyle("Footer", parent=normal, fontSize=8, textColor=colors.grey, alignment=TA_CENTER),
    ))

    doc.build(elements)
    buffer.seek(0)
    filename = "VISTA_Teacher_{}_{}.pdf".format(t["teacher_id"], datetime.now().strftime("%Y%m%d"))
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="{}"'.format(filename)},
    )
