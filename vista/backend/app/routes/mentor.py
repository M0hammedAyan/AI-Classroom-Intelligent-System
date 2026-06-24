"""
Mentor API — Student monitoring, interventions, watchlist.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.intervention import Intervention
from ..models.organization import MentorAssignment
from ..models.attendance import RiskFlag
from ..models.student import Student
from ..models.user import User
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/mentor", tags=["mentor"])


def _require_mentor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("mentor", "admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Mentor access required."})
    return current_user


@router.get("/dashboard")
def mentor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_mentor),
):
    """Mentor dashboard data — assigned students, risk stats, recent interventions."""
    # Get assigned students
    assignments = (
        db.query(MentorAssignment)
        .filter(MentorAssignment.mentor_id == current_user.id, MentorAssignment.is_active == True)
        .all()
    )
    student_ids = [a.student_id for a in assignments]

    # Get risk flags for assigned students
    high_risk = 0
    medium_risk = 0
    for sid in student_ids:
        flag = (
            db.query(RiskFlag)
            .filter(RiskFlag.student_id == sid)
            .order_by(RiskFlag.calculated_at.desc())
            .first()
        )
        if flag:
            if flag.risk_level == "high":
                high_risk += 1
            elif flag.risk_level == "medium":
                medium_risk += 1

    # Recent interventions
    recent = (
        db.query(Intervention)
        .filter(Intervention.mentor_id == current_user.id)
        .order_by(Intervention.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "assigned_students": len(student_ids),
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "recent_interventions": [
            {"id": i.id, "student_id": i.student_id, "type": i.type, "outcome": i.outcome, "created_at": i.created_at}
            for i in recent
        ],
    }


@router.get("/students")
def mentor_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_mentor),
):
    """List all students assigned to this mentor with their risk level."""
    assignments = (
        db.query(MentorAssignment)
        .filter(MentorAssignment.mentor_id == current_user.id, MentorAssignment.is_active == True)
        .all()
    )

    students = []
    for a in assignments:
        student = db.query(Student).filter(Student.student_id == a.student_id).first()
        if not student:
            continue
        flag = (
            db.query(RiskFlag)
            .filter(RiskFlag.student_id == a.student_id)
            .order_by(RiskFlag.calculated_at.desc())
            .first()
        )
        students.append({
            "student_id": student.student_id,
            "name": student.name,
            "class": student.class_,
            "risk_level": flag.risk_level if flag else "unknown",
            "risk_reasons": json.loads(flag.reasons) if flag and flag.reasons else [],
        })

    # Sort: high risk first
    order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
    students.sort(key=lambda s: order.get(s["risk_level"], 3))
    return {"students": students, "total": len(students)}


@router.get("/watchlist")
def mentor_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_mentor),
):
    """High and medium risk students only — sorted by severity."""
    result = mentor_students(db=db, current_user=current_user)
    watchlist = [s for s in result["students"] if s["risk_level"] in ("high", "medium")]
    return {"students": watchlist, "total": len(watchlist)}


class InterventionRequest(BaseModel):
    student_id: str
    type: str               # counselling | call | meeting | referral | email
    notes: str | None = None
    outcome: str | None = None  # pending | improved | no_change | escalated


@router.post("/interventions")
def create_intervention(
    body: InterventionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_mentor),
):
    """Log a new intervention for a student."""
    valid_types = ["counselling", "call", "meeting", "referral", "email"]
    if body.type not in valid_types:
        raise HTTPException(status_code=400, detail={"code": "INVALID_TYPE", "message": f"Type must be one of: {valid_types}"})

    now = datetime.now(timezone.utc).isoformat()
    intervention = Intervention(
        id=str(uuid.uuid4()),
        mentor_id=current_user.id,
        student_id=body.student_id,
        type=body.type,
        notes=body.notes,
        outcome=body.outcome or "pending",
        created_at=now,
    )
    db.add(intervention)
    db.commit()

    # Log to audit
    _audit(db, current_user.id, "create_intervention", "student", body.student_id)

    return {"id": intervention.id, "student_id": body.student_id, "type": body.type, "status": "logged"}


@router.get("/interventions")
def list_interventions(
    student_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_mentor),
):
    """List interventions by this mentor, optionally filtered by student."""
    query = db.query(Intervention).filter(Intervention.mentor_id == current_user.id)
    if student_id:
        query = query.filter(Intervention.student_id == student_id)
    rows = query.order_by(Intervention.created_at.desc()).limit(50).all()
    return {
        "interventions": [
            {
                "id": r.id,
                "student_id": r.student_id,
                "type": r.type,
                "notes": r.notes,
                "outcome": r.outcome,
                "created_at": r.created_at,
            }
            for r in rows
        ],
    }


@router.patch("/interventions/{intervention_id}")
def update_intervention(
    intervention_id: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_mentor),
):
    """Update outcome or notes on an existing intervention."""
    row = db.query(Intervention).filter(Intervention.id == intervention_id, Intervention.mentor_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Intervention not found."})
    if "outcome" in body:
        row.outcome = body["outcome"]
    if "notes" in body:
        row.notes = body["notes"]
    db.commit()
    return {"id": row.id, "outcome": row.outcome, "updated": True}


def _audit(db: Session, user_id: str, action: str, target_type: str, target_id: str):
    """Write an audit log entry."""
    from ..models.audit import AuditLog
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    ))
