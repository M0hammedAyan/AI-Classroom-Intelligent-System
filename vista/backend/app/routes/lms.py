"""
LMS Integration — Score Ingestion
===================================
Import academic scores from Learning Management Systems (Moodle, Google Classroom).
Supports:
- Manual CSV upload of scores
- Moodle Web Services API integration (when configured)

Endpoints:
    POST /api/v1/lms/import-csv    — Upload CSV file with scores
    POST /api/v1/lms/sync-moodle   — Pull grades from Moodle (requires config)
"""
from __future__ import annotations

import csv
import io
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import Score
from ..models.student import Student
from ..routes.auth import require_admin

router = APIRouter(prefix="/api/v1/lms", tags=["lms"])


@router.get("/scores")
def list_scores(
    student_id: str | None = None,
    subject: str | None = None,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """List all scores, optionally filtered by student or subject."""
    query = db.query(Score)
    if student_id:
        query = query.filter(Score.student_id == student_id)
    if subject:
        query = query.filter(Score.subject == subject)
    rows = query.order_by(Score.date.desc()).limit(200).all()
    return {
        "scores": [
            {
                "student_id": r.student_id,
                "subject": r.subject,
                "score": r.score,
                "max_score": r.max_score,
                "date": r.date,
            }
            for r in rows
        ],
        "total": len(rows),
    }


@router.post("/add-score")
def add_score(
    body: dict,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Add a single score manually."""
    required = {"student_id", "subject", "score", "max_score", "date"}
    missing = required - set(body.keys())
    if missing:
        raise HTTPException(status_code=400, detail={"code": "MISSING_FIELDS", "message": f"Missing: {missing}"})

    student = db.query(Student).filter(Student.student_id == body["student_id"]).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"Student {body['student_id']} not found"})

    now = datetime.now(timezone.utc).isoformat()
    score = Score(
        id=str(uuid.uuid4()),
        student_id=body["student_id"],
        subject=body["subject"],
        score=float(body["score"]),
        max_score=float(body["max_score"]),
        date=body["date"],
        created_at=now,
    )
    db.add(score)
    db.commit()
    return {"added": True, "student_id": body["student_id"], "subject": body["subject"]}


@router.post("/import-csv")
async def import_scores_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Import scores from a CSV file.

    Expected CSV format:
        student_id,subject,score,max_score,date
        CS22B001,Data Structures,78,100,2026-06-15
        CS22B002,Data Structures,62,100,2026-06-15
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_FORMAT", "message": "File must be a .csv"})

    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    required_cols = {"student_id", "subject", "score", "max_score", "date"}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_COLUMNS", "message": f"CSV must have columns: {required_cols}"},
        )

    imported = 0
    errors = []
    now = datetime.now(timezone.utc).isoformat()

    for i, row in enumerate(reader, start=2):
        try:
            # Validate student exists
            student = db.query(Student).filter(Student.student_id == row["student_id"]).first()
            if not student:
                errors.append({"row": i, "error": f"Student {row['student_id']} not found"})
                continue

            score = Score(
                id=str(uuid.uuid4()),
                student_id=row["student_id"],
                subject=row["subject"],
                score=float(row["score"]),
                max_score=float(row["max_score"]),
                date=row["date"],
                created_at=now,
            )
            db.add(score)
            imported += 1
        except (ValueError, KeyError) as exc:
            errors.append({"row": i, "error": str(exc)})

    db.commit()

    return {
        "imported": imported,
        "errors": len(errors),
        "error_details": errors[:10],  # Return first 10 errors
    }


@router.post("/sync-moodle")
def sync_moodle(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Sync grades from Moodle Web Services API.

    Requires environment variables:
        MOODLE_URL: Base URL of Moodle instance
        MOODLE_TOKEN: Web service token
        MOODLE_COURSE_ID: Course ID to pull grades from
    """
    moodle_url = os.getenv("MOODLE_URL")
    moodle_token = os.getenv("MOODLE_TOKEN")
    course_id = os.getenv("MOODLE_COURSE_ID")

    if not all([moodle_url, moodle_token, course_id]):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "MOODLE_NOT_CONFIGURED",
                "message": "Set MOODLE_URL, MOODLE_TOKEN, and MOODLE_COURSE_ID environment variables.",
            },
        )

    try:
        import requests

        # Moodle web service: get grades
        params = {
            "wstoken": moodle_token,
            "moodlewsrestformat": "json",
            "wsfunction": "gradereport_user_get_grade_items",
            "courseid": course_id,
        }
        resp = requests.get(f"{moodle_url}/webservice/rest/server.php", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if "exception" in data:
            raise HTTPException(status_code=500, detail={"code": "MOODLE_ERROR", "message": data.get("message", "Moodle API error")})

        # Process grades
        imported = 0
        now = datetime.now(timezone.utc).isoformat()

        for user_grade in data.get("usergrades", []):
            # Map Moodle user to VISTA student (by username or idnumber)
            moodle_username = user_grade.get("useridnumber", "")
            student = db.query(Student).filter(Student.student_id == moodle_username).first()
            if not student:
                continue

            for item in user_grade.get("gradeitems", []):
                if item.get("graderaw") is None:
                    continue
                score = Score(
                    id=str(uuid.uuid4()),
                    student_id=student.student_id,
                    subject=item.get("itemname", "Unknown"),
                    score=float(item.get("graderaw", 0)),
                    max_score=float(item.get("grademax", 100)),
                    date=now[:10],
                    created_at=now,
                )
                db.add(score)
                imported += 1

        db.commit()
        return {"imported": imported, "source": "moodle", "course_id": course_id}

    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail={"code": "MOODLE_CONNECTION_ERROR", "message": str(exc)})
