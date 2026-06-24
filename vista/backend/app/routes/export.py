from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Attendance
from ..models.student import Student
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/report")
def export_report(
    classroom_id: str,
    from_date: str,
    to_date: str,
    format: str = "csv",
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    if format not in {"csv", "pdf"}:
        raise HTTPException(status_code=400, detail={"code": "INVALID_FORMAT", "message": "format must be 'csv' or 'pdf'."})
    if from_date > to_date:
        raise HTTPException(status_code=400, detail={"code": "INVALID_DATE_RANGE", "message": "to_date must be >= from_date."})

    students = (
        db.query(Student)
        .filter(Student.classroom_id == classroom_id, Student.is_active == True)
        .order_by(Student.student_id)
        .all()
    )
    att_rows = (
        db.query(Attendance)
        .filter(
            Attendance.classroom_id == classroom_id,
            Attendance.session_date >= from_date,
            Attendance.session_date <= to_date,
        )
        .all()
    )

    if not students and not att_rows:
        raise HTTPException(status_code=404, detail={"code": "NO_DATA", "message": "No data found for the given parameters."})

    # Build {student_id: {date: status}} lookup
    lookup: dict[str, dict[str, str]] = {}
    for row in att_rows:
        if row.student_id:
            lookup.setdefault(row.student_id, {})[row.session_date] = row.status

    # Collect unique session dates in range
    dates_in_data = sorted({row.session_date for row in att_rows})

    if format == "csv":
        return _csv_response(students, lookup, dates_in_data, classroom_id, from_date, to_date)
    else:
        return _pdf_response(students, lookup, dates_in_data, classroom_id, from_date, to_date)


def _csv_response(students, lookup, dates, classroom_id, from_date, to_date):
    output = io.StringIO()
    fieldnames = ["student_id", "name"] + dates
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for s in students:
        row = {"student_id": s.student_id, "name": s.name}
        for d in dates:
            row[d] = lookup.get(s.student_id, {}).get(d, "absent")
        writer.writerow(row)

    filename = f"attendance_{classroom_id}_{from_date}_{to_date}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _pdf_response(students, lookup, dates, classroom_id, from_date, to_date):
    """Generate a PDF attendance report using ReportLab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Attendance Report — {classroom_id}", styles["Title"]))
    elements.append(Paragraph(f"Period: {from_date} to {to_date}", styles["Normal"]))
    elements.append(Spacer(1, 0.5*cm))

    # Build table data
    # Limit columns to avoid overflow — show max 10 dates per page
    display_dates = dates[:15] if len(dates) > 15 else dates
    header = ["ID", "Name"] + [d[5:] for d in display_dates]  # Show MM-DD only
    table_data = [header]

    for s in students:
        row = [s.student_id, s.name[:20]]
        for d in display_dates:
            status = lookup.get(s.student_id, {}).get(d, "absent")
            row.append("P" if status == "present" else "A" if status == "absent" else "L")
        table_data.append(row)

    # Create table
    col_widths = [2.5*cm, 4*cm] + [1.2*cm] * len(display_dates)
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
    ]))
    elements.append(table)

    # Summary
    elements.append(Spacer(1, 0.5*cm))
    total_sessions = len(display_dates)
    for s in students:
        present_count = sum(1 for d in display_dates if lookup.get(s.student_id, {}).get(d, "absent") == "present")
        pct = (present_count / total_sessions * 100) if total_sessions > 0 else 0
        elements.append(Paragraph(
            f"{s.student_id} {s.name}: {present_count}/{total_sessions} ({pct:.0f}%)",
            styles["Normal"]
        ))

    doc.build(elements)

    filename = f"attendance_{classroom_id}_{from_date}_{to_date}.pdf"
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
