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
        raise HTTPException(status_code=400, detail={"code": "PDF_NOT_IMPLEMENTED", "message": "PDF export is not yet implemented. Use format=csv."})


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
