"""Notifications API — In-app notification center."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.notification import Notification
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get notifications for the current user."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()
    unread_count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count()
    )

    notifications = (
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "notifications": [_to_dict(n) for n in notifications],
        "total": total,
        "unread_count": unread_count,
        "page": page,
        "page_size": page_size,
    }


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Quick count of unread notifications (for badge)."""
    count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count()
    )
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Mark a single notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"status": "ok"}


@router.patch("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Mark all notifications as read for the current user."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Helper: create a notification (used by other modules)
# ---------------------------------------------------------------------------

def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    type_: str = "system",
    link: str | None = None,
) -> Notification:
    """Create and persist a notification. Does NOT commit — caller must commit."""
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        message=message,
        type=type_,
        is_read=False,
        link=link,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(notif)
    return notif


def notify_high_risk(db: Session, student_id: str, student_name: str, risk_level: str, reasons: list[str]):
    """
    Auto-create notifications for mentors and HOP/HOS when a student is flagged HIGH risk.
    Called from risk computation pipeline.
    """
    if risk_level.lower() != "high":
        return

    from ..models.organization import MentorAssignment
    from ..models.user import User

    reason_text = "; ".join(reasons[:3]) if reasons else "Multiple risk factors detected"

    # Notify assigned mentor(s)
    mentor_assignments = (
        db.query(MentorAssignment)
        .filter(MentorAssignment.student_id == student_id, MentorAssignment.is_active == True)
        .all()
    )
    for ma in mentor_assignments:
        create_notification(
            db,
            user_id=ma.mentor_id,
            title=f"🚨 HIGH Risk: {student_name}",
            message=f"Student {student_name} ({student_id}) flagged as HIGH risk. {reason_text}",
            type_="risk_alert",
            link=f"/student/{student_id}",
        )

    # Notify HOP users in the same department
    hop_users = db.query(User).filter(User.role == "hop", User.is_active == True).all()
    for hop in hop_users:
        create_notification(
            db,
            user_id=hop.id,
            title=f"⚠️ HIGH Risk Alert: {student_name}",
            message=f"Student {student_name} ({student_id}) requires intervention. {reason_text}",
            type_="risk_alert",
            link=f"/student/{student_id}",
        )

    # Notify admin
    admins = db.query(User).filter(User.role == "admin", User.is_active == True).all()
    for admin in admins:
        create_notification(
            db,
            user_id=admin.id,
            title=f"⚠️ HIGH Risk Alert: {student_name}",
            message=f"Student {student_name} ({student_id}) flagged HIGH risk. {reason_text}",
            type_="risk_alert",
            link=f"/student/{student_id}",
        )


def _to_dict(n: Notification) -> dict:
    return {
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "is_read": n.is_read,
        "link": n.link,
        "created_at": n.created_at,
    }
