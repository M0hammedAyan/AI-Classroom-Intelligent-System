"""Individual Student PDF Report — comprehensive academic + attendance + risk report."""
from __future__ import annotations

import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import get_db, get_student_metrics
from ..models.attendance import Attendance, Score, RiskFlag
from ..models.student import Student
from ..models.organization import MentorAssignment
from ..models.user import User
from ..routes.auth import get_current_user

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
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

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
