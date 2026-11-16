"""Append Part 4 CSV/PDF endpoints and audit-log patches to reports.py."""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

REPORTS_PATH = 'vista/backend/app/routes/reports.py'

with open(REPORTS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Patch audit log into /student/me
OLD_ME = '''    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can call /reports/student/me.")
    student_id = current_user.id.replace("student-", "")
    student = _authorize_student_report_access(student_id, current_user, db)
    return build_student_report_data(student, db)'''
NEW_ME = '''    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can call /reports/student/me.")
    student_id = current_user.id.replace("student-", "")
    student = _authorize_student_report_access(student_id, current_user, db)
    result = build_student_report_data(student, db)
    log_action(db, user_id=current_user.id, action="generate_student_report",
               target_type="student_report", target_id=student_id,
               details='{{"student_id":"{}","format":"json"}}'.format(student_id))
    db.commit()
    return result'''
if OLD_ME in content:
    content = content.replace(OLD_ME, NEW_ME)
    print('Patched /student/me audit log')

# Patch audit log into /student/{id}
OLD_SID = '''    student = _authorize_student_report_access(student_id, current_user, db)
    return build_student_report_data(student, db)'''
NEW_SID = '''    student = _authorize_student_report_access(student_id, current_user, db)
    result = build_student_report_data(student, db)
    log_action(db, user_id=current_user.id, action="generate_student_report",
               target_type="student_report", target_id=student_id,
               details='{{"student_id":"{}","format":"json","by":"{}"}}'.format(student_id, current_user.role))
    db.commit()
    return result'''
if OLD_SID in content:
    content = content.replace(OLD_SID, NEW_SID)
    print('Patched /student/{id} audit log')

# Patch audit log into /teacher/me
OLD_TME = '''    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can call /reports/teacher/me.")
    teacher = _authorize_teacher_report_access(current_user.id, current_user, db)
    return build_teacher_report_data(teacher, db)'''
NEW_TME = '''    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can call /reports/teacher/me.")
    teacher = _authorize_teacher_report_access(current_user.id, current_user, db)
    result = build_teacher_report_data(teacher, db)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=current_user.id,
               details='{{"teacher_id":"{}","format":"json"}}'.format(current_user.id))
    db.commit()
    return result'''
if OLD_TME in content:
    content = content.replace(OLD_TME, NEW_TME)
    print('Patched /teacher/me audit log')

# Patch audit log into /teacher/{id}
OLD_TID = '''    teacher = _authorize_teacher_report_access(teacher_id, current_user, db)
    return build_teacher_report_data(teacher, db)'''
NEW_TID = '''    teacher = _authorize_teacher_report_access(teacher_id, current_user, db)
    result = build_teacher_report_data(teacher, db)
    log_action(db, user_id=current_user.id, action="generate_teacher_report",
               target_type="teacher_report", target_id=teacher_id,
               details='{{"teacher_id":"{}","format":"json","by":"{}"}}'.format(teacher_id, current_user.role))
    db.commit()
    return result'''
if OLD_TID in content:
    content = content.replace(OLD_TID, NEW_TID)
    print('Patched /teacher/{id} audit log')

# Append new CSV/PDF endpoints
NEW_ENDPOINTS = r'''

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
'''

if 'def _build_student_csv' not in content:
    content = content.rstrip() + '\n' + NEW_ENDPOINTS
    print('Appended CSV/PDF endpoints')
else:
    print('CSV/PDF endpoints already present')

with open(REPORTS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print('Done patching reports.py')
