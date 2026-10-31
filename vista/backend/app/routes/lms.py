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
from ..models.organization import ClassSection, Subject, TeacherSubjectAssignment
from ..models.student import Student
from ..routes.auth import get_current_user, require_admin
from ..cie_policy import evaluate_cie

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
    current_user=Depends(get_current_user),
):
    """
    Add or update a score manually (upsert).
    - Teachers may edit only their assigned subject and class.
    - Admins can edit any student and subject.
    - Students are strictly forbidden.
    - Reason is mandatory.
    - Validation: numeric marks, 0 <= score <= max_score (CIE max = 25).
    - Date: no future dates, no dates before 2026-08-03 unless admin.
    - Writes an audit log on every change with source='manual'.
    """
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Student accounts cannot add or edit marks."})
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only admins and assigned teachers can add marks."})

    if "student_id" not in body or "subject" not in body:
        raise HTTPException(status_code=400, detail={"code": "MISSING_FIELDS", "message": "Missing required fields: student_id and subject"})

    student = db.query(Student).filter(Student.student_id == body["student_id"]).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"Student {body['student_id']} not found."})

    status = str(body.get("status", "scored")).strip().lower()
    if status not in ("scored", "absent"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_STATUS", "message": "Status must be 'scored' or 'absent'."})

    assessment_type = str(body.get("assessment_type", "CIE 1")).strip()
    max_score = float(body.get("max_score", 25.0))
    if "CIE" in assessment_type.upper():
        max_score = 25.0

    score_val = None
    if status == "scored":
        if "score" not in body or body["score"] is None:
            raise HTTPException(status_code=400, detail={"code": "MISSING_SCORE", "message": "Score is required when status is 'scored'."})
        try:
            score_val = float(body["score"])
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail={"code": "INVALID_SCORE", "message": "Score must be a valid number."})
        if score_val < 0.0 or score_val > max_score:
            raise HTTPException(status_code=400, detail={
                "code": "SCORE_OUT_OF_RANGE",
                "message": f"Score must be between 0 and {max_score}.",
            })

    # Mandatory reason
    reason = str(body.get("reason", "") or body.get("note", "")).strip()
    if not reason:
        raise HTTPException(status_code=400, detail={
            "code": "REASON_REQUIRED",
            "message": "A reason is mandatory for manual marks entry.",
        })

    # Date validation: no future dates, no dates before 2026-08-03 unless admin
    today_str = datetime.now(timezone.utc).date().isoformat()
    score_date = str(body.get("date", today_str)).strip()
    if score_date > today_str:
        raise HTTPException(status_code=400, detail={"code": "FUTURE_DATE", "message": "Cannot record marks for future dates."})
    if current_user.role != "admin" and score_date < "2026-08-03":
        raise HTTPException(status_code=400, detail={"code": "DATE_OUT_OF_RANGE", "message": "Date cannot be before semester start (03-Aug-2026)."})

    # Subject matching
    subject = db.query(Subject).filter(
        (Subject.id == body["subject"]) | (Subject.code == body["subject"]) | (Subject.name == body["subject"])
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail={"code": "SUBJECT_NOT_FOUND", "message": f"Subject {body['subject']} not found."})

    # CIE 3 eligibility check
    if assessment_type == "CIE 3":
        cie_eval = evaluate_cie(student.student_id, subject.name, db)
        if not cie_eval["cie3_eligible"] and current_user.role != "admin":
            raise HTTPException(status_code=400, detail={
                "code": "CIE3_NOT_ELIGIBLE",
                "message": f"Student is not eligible for CIE 3 ({cie_eval['cie3_reason']}). Admin override required.",
            })

    # Scope validation for teacher
    if current_user.role == "teacher":
        class_section = db.query(ClassSection).filter(
            (ClassSection.id == student.classroom_id) |
            (ClassSection.code == student.classroom_id) |
            (ClassSection.code == student.class_) |
            (ClassSection.name == student.class_)
        ).first()

        allowed = class_section and db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == current_user.id,
            TeacherSubjectAssignment.subject_id == subject.id,
            TeacherSubjectAssignment.class_section_id == class_section.id,
            TeacherSubjectAssignment.is_active == True,
        ).first()
        if not allowed:
            raise HTTPException(status_code=403, detail={"code": "SUBJECT_SCOPE", "message": "Teachers can only add marks for their assigned subjects and class."})

    # Upsert score record
    existing = db.query(Score).filter(
        Score.student_id == student.student_id,
        (Score.subject == subject.name) | (Score.subject == subject.code),
        Score.assessment_type == assessment_type,
    ).first()

    now = datetime.now(timezone.utc).isoformat()
    old_score = existing.score if existing else None
    if existing:
        existing.score = score_val
        existing.status = status
        existing.max_score = max_score
        existing.date = score_date
        existing.source = "manual"
        db.commit()
        db.refresh(existing)
        row = existing
    else:
        row = Score(
            id=str(uuid.uuid4()),
            student_id=student.student_id,
            subject=subject.name,
            assessment_type=assessment_type,
            score=score_val,
            status=status,
            max_score=max_score,
            date=score_date,
            source="manual",
            created_at=now,
        )
        db.add(row)
        db.commit()
        db.refresh(row)

    # Write audit log
    from ..audit import log_action
    import json
    log_action(
        db,
        user_id=current_user.id,
        action="manual_marks_update",
        target_type="student",
        target_id=student.student_id,
        details=json.dumps({
            "subject": subject.name,
            "assessment_type": assessment_type,
            "old_score": old_score,
            "new_score": score_val,
            "max_score": max_score,
            "reason": reason,
            "source": "manual",
        }),
    )
    db.commit()

    return {
        "status": "ok",
        "score_id": row.id,
        "student_id": row.student_id,
        "subject": row.subject,
        "assessment_type": row.assessment_type,
        "score": row.score,
        "max_score": row.max_score,
        "source": row.source,
        "is_update": old_score is not None,
    }


@router.get("/student/{student_id}/marks")
def get_student_marks(
    student_id: str,
    subject: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch marks for a student and optional subject for review/manual entry."""
    if current_user.role == "student" and current_user.id != f"student-{student_id}":
        raise HTTPException(status_code=403, detail="Forbidden")

    query = db.query(Score).filter(Score.student_id == student_id)
    if subject:
        query = query.filter((Score.subject == subject) | (Score.subject.like(f"%{subject}%")))
    scores = query.order_by(Score.date.asc()).all()

    eval_res = None
    if subject:
        eval_res = evaluate_cie(student_id, subject, db)

    return {
        "student_id": student_id,
        "cie_evaluation": eval_res,
        "scores": [
            {
                "id": s.id,
                "subject": s.subject,
                "assessment_type": s.assessment_type or "Assessment",
                "score": s.score,
                "status": s.status or ("scored" if s.score is not None else "absent"),
                "max_score": s.max_score,
                "date": s.date,
                "source": s.source or "seed",
            }
            for s in scores
        ],
    }


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
