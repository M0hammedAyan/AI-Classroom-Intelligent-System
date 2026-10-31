"""
AI Study Coach API — Interactive Guidance for Students
======================================================
Endpoints:
- POST   /api/v1/coach/chat      — Send message to Study Coach (Student only)
- GET    /api/v1/coach/history   — Retrieve conversation history (Student only)
- DELETE /api/v1/coach/history   — Clear conversation history (Student only)
- GET    /api/v1/coach/summary   — Proactive summary and dashboard tip card (Zero-LLM)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.chat import ChatMessage
from ..models.user import User
from ..routes.student_portal import _get_student_id, _require_student
from ..services.coach_service import chat_with_coach, get_coach_facts, get_coach_tip

router = APIRouter(prefix="/api/v1/coach", tags=["coach"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Student question or query")


@router.post("/chat")
def coach_chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """
    Chat with the AI Study Coach.
    Strict Security: Student ID is resolved strictly from the authenticated JWT token.
    Never from request body.
    """
    student_id = _get_student_id(current_user)
    try:
        result = chat_with_coach(student_id=student_id, user_message=body.message, db=db)
        # Include facts for groundedness verification (no PII — student_id is internal)
        facts = get_coach_facts(student_id=student_id, db=db)
        return {
            "reply": result["reply"],
            "provider": result["provider"],
            "model": result["model"],
            "disclaimer": "AI-generated advice based on your verified academic records. Check with your course teacher for official academic decisions.",
            "facts": facts,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail={"code": "COACH_ERROR", "message": str(exc)})


@router.get("/history")
def get_chat_history(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Retrieve chat conversation history for the authenticated student."""
    student_id = _get_student_id(current_user)
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.student_id == student_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )
    return {
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in messages
        ],
        "total": len(messages),
    }


@router.delete("/history")
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """Clear chat conversation history for the authenticated student."""
    student_id = _get_student_id(current_user)
    deleted_count = db.query(ChatMessage).filter(ChatMessage.student_id == student_id).delete(synchronize_session=False)
    db.commit()
    return {"status": "cleared", "deleted_messages": deleted_count}


@router.get("/summary")
def get_coach_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_student),
):
    """
    Proactive coach summary and tip card.
    Zero external LLM invocation — pure deterministic math from coach_facts.
    """
    student_id = _get_student_id(current_user)
    tip = get_coach_tip(student_id=student_id, db=db)
    facts = get_coach_facts(student_id=student_id, db=db)
    return {
        "tip_card": tip,
        "facts": facts,
    }
