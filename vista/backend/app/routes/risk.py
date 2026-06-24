from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.attendance import RiskFlag
from ..models.student import Student
from ..routes.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/v1", tags=["risk"])


@router.get("/students/{student_id}/risk")
def get_student_risk(
    student_id: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."})
    flag = (
        db.query(RiskFlag)
        .filter(RiskFlag.student_id == student_id)
        .order_by(RiskFlag.calculated_at.desc())
        .first()
    )
    if not flag:
        raise HTTPException(status_code=404, detail={"code": "RISK_NOT_COMPUTED", "message": "Risk has not been computed for this student yet."})
    return _flag_dict(flag, student.name)


@router.get("/risk")
def list_risk(
    risk_level: str | None = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    # Latest flag per student via subquery approach
    from sqlalchemy import func
    subq = (
        db.query(RiskFlag.student_id, func.max(RiskFlag.calculated_at).label("latest"))
        .group_by(RiskFlag.student_id)
        .subquery()
    )
    query = (
        db.query(RiskFlag, Student.name)
        .join(subq, (RiskFlag.student_id == subq.c.student_id) & (RiskFlag.calculated_at == subq.c.latest))
        .join(Student, RiskFlag.student_id == Student.student_id)
    )
    if risk_level:
        query = query.filter(RiskFlag.risk_level == risk_level.lower())

    total = query.count()
    rows = query.offset(offset).limit(page_size).all()

    flags = [_flag_dict(flag, name) for flag, name in rows]
    return {"flags": flags, "total": total, "page": page, "page_size": page_size}


@router.post("/students/{student_id}/risk/recompute")
def recompute_risk(
    student_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."})

    try:
        from vista.ml.risk_engine import calculate_risk_from_metrics
        from ..db import get_student_metrics
        metrics = get_student_metrics(student_id, db)
        result = calculate_risk_from_metrics(metrics)
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"code": "RISK_COMPUTE_ERROR", "message": str(exc)})

    now = datetime.now(timezone.utc).isoformat()
    flag = RiskFlag(
        id=str(uuid.uuid4()),
        student_id=student_id,
        risk_level=result["risk_level"].lower(),
        reasons=json.dumps(result["reasons"]),
        confidence=result["confidence"],
        calculated_at=now,
        created_at=now,
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return _flag_dict(flag, student.name)


@router.post("/risk/recompute-all")
def recompute_all_risk(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Recompute risk for all active students. Admin only."""
    students = db.query(Student).filter(Student.is_active == True).all()
    if not students:
        return {"recomputed": 0, "results": []}

    from vista.ml.risk_engine import calculate_risk_from_metrics
    from ..db import get_student_metrics

    results = []
    errors = []
    now = datetime.now(timezone.utc).isoformat()

    for student in students:
        try:
            metrics = get_student_metrics(student.student_id, db)
            result = calculate_risk_from_metrics(metrics)
            flag = RiskFlag(
                id=str(uuid.uuid4()),
                student_id=student.student_id,
                risk_level=result["risk_level"].lower(),
                reasons=json.dumps(result["reasons"]),
                confidence=result["confidence"],
                calculated_at=now,
                created_at=now,
            )
            db.add(flag)
            results.append({"student_id": student.student_id, "risk_level": result["risk_level"]})
        except Exception as exc:
            errors.append({"student_id": student.student_id, "error": str(exc)})

    db.commit()
    return {"recomputed": len(results), "errors": len(errors), "results": results}


def _flag_dict(flag: RiskFlag, student_name: str) -> dict:
    reasons = json.loads(flag.reasons) if isinstance(flag.reasons, str) else flag.reasons
    return {
        "student_id": flag.student_id,
        "student_name": student_name,
        "risk_level": flag.risk_level,
        "reasons": reasons,
        "confidence": flag.confidence,
        "computed_at": flag.calculated_at,
    }


@router.get("/students/{student_id}/risk/explain")
def explain_risk(
    student_id: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """
    Get SHAP-based explainability for a student's risk prediction.
    Uses the XGBoost model with TreeExplainer to show per-feature contributions.
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."})

    try:
        from vista.ml.risk_engine import run_pipeline_with_shap
        from ..db import get_student_metrics
        from vista.ml.features import compute_features

        metrics = get_student_metrics(student_id, db)
        features = compute_features(metrics)

        # Build input for XGBoost pipeline
        input_data = {
            "student_id": student_id,
            "overall_attendance": features.attendance_percentage,
            "recent_attendance": features.attendance_percentage - features.attendance_drop_percentage,
            "avg_score": features.internal_marks_average,
            "recent_score": features.internal_marks_average * (1 - features.marks_decline_percentage / 100),
            "failed_subjects": 1 if features.internal_marks_average < 40 else 0,
        }

        result = run_pipeline_with_shap(input_data)

        return {
            "student_id": student_id,
            "student_name": student.name,
            "risk_level": result["risk_level"],
            "risk_score": result["risk_score"],
            "reasons": result["reasons"],
            "recommended_actions": result["recommended_actions"],
            "summary": result["summary"],
            "explainability": result.get("explainability", {}),
            "trend": result["trend"],
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail={"code": "EXPLAIN_ERROR", "message": str(exc)})
