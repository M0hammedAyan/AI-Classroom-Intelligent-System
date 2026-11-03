"""
Notifications API — Role-Scoped In-App Notification Center
===========================================================
Audience Rules:
- Admin -> 'all' (every teacher and student), or targeted 'class' or 'subject'
- Teacher -> only subjects/classes they teach (strictly validated against TeacherSubjectAssignment)
- Student -> read-only (sending strictly rejected with 403)
- Recipients are resolved dynamically at read time from audience rules.
"""
from __future__ import annotations

import html
import re
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.notification import Notification, NotificationRead
from ..models.organization import ClassSection, Subject, TeacherSubjectAssignment
from ..models.student import Student
from ..models.user import User
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

# In-memory rate limiting: user_id -> list of timestamps
_send_rate_limit: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60.0  # 1 minute
MAX_SENDS_PER_WINDOW = 10


def sanitize_text(text: str) -> str:
    """Strip dangerous HTML tags and escape to prevent stored XSS."""
    clean = re.sub(r"<(script|iframe|embed|object|style)[^>]*>.*?</\1>", "", text, flags=re.IGNORECASE | re.DOTALL)
    clean = re.sub(r"<[^>]+>", "", clean)
    return html.escape(clean.strip())


def is_rate_limited(user_id: str) -> bool:
    now = time.time()
    timestamps = [t for t in _send_rate_limit[user_id] if now - t < RATE_LIMIT_WINDOW]
    _send_rate_limit[user_id] = timestamps
    if len(timestamps) >= MAX_SENDS_PER_WINDOW:
        return True
    _send_rate_limit[user_id].append(now)
    return False


def get_user_enrolled_subjects_and_classes(user: User, db: Session) -> tuple[set[str], set[str]]:
    """Resolves subject IDs/codes and class IDs/codes for a user based on their role."""
    subject_identifiers = set()
    class_identifiers = set()

    if user.role == "teacher":
        assignments = db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == user.id,
            TeacherSubjectAssignment.is_active == True,
        ).all()
        for a in assignments:
            subject_identifiers.add(a.subject_id)
            class_identifiers.add(a.class_section_id)
            # Add subject codes
            subj = db.query(Subject).filter(Subject.id == a.subject_id).first()
            if subj:
                subject_identifiers.add(subj.code)
                subject_identifiers.add(subj.name)
            cs = db.query(ClassSection).filter(ClassSection.id == a.class_section_id).first()
            if cs:
                class_identifiers.add(cs.code)
                class_identifiers.add(cs.name)
    elif user.role == "student":
        student_id = user.id.replace("student-", "") if user.id.startswith("student-") else user.email.split("@")[0].upper()
        student = db.query(Student).filter((Student.student_id == student_id) | (Student.student_id == user.email.split("@")[0].upper())).first()
        if student:
            if student.classroom_id:
                class_identifiers.add(student.classroom_id)
            if student.class_:
                class_identifiers.add(student.class_)

            # Active curriculum subjects
            active_subjs = db.query(Subject).filter(Subject.is_active == True).all()
            for s in active_subjs:
                subject_identifiers.add(s.id)
                subject_identifiers.add(s.code)
                subject_identifiers.add(s.name)

    return subject_identifiers, class_identifiers


def can_user_view_notification(user: User, notif: Notification, user_subjects: set[str], user_classes: set[str]) -> bool:
    """
    Evaluates whether a notification is visible to the given user:
    - Admin: sees all
    - Sender: always sees own notification
    - 'all': visible to everyone
    - 'class': matches user's enrolled/assigned class
    - 'subject': matches user's enrolled/assigned subject
    """
    if user.role == "admin" or notif.sender_id == user.id:
        return True

    # Teacher visibility:
    # If sent by another teacher, teachers only see if they teach that class/subject
    # If sent by admin, teachers see 'all', or matching class/subject
    if notif.audience_type == "all":
        # If teacher sent 'all', it targets their audience (classes they teach)
        if notif.sender_role == "teacher":
            # Must overlap with sender's classes/subjects
            if user.role == "student":
                # Is student in sender's audience?
                return bool(user_classes.intersection(notif.class_id.split(",")) if notif.class_id else True)
            return False  # other teachers don't see another teacher's general broadcast
        return True  # Admin broadcast -> everyone

    if notif.audience_type == "subject":
        return bool(notif.subject_id and notif.subject_id in user_subjects)

    if notif.audience_type == "class":
        return bool(notif.class_id and notif.class_id in user_classes)

    return False


class CreateNotificationRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    body: str = Field(..., min_length=2, max_length=2000)
    audience_type: str = Field("all", pattern="^(all|class|subject)$")
    class_id: str | None = None
    subject_id: str | None = None
    priority: str = Field("normal", pattern="^(normal|important)$")
    expires_at: str | None = None


@router.post("")
def create_notification(
    body: CreateNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send an in-app notification.
    - Admin can broadcast to 'all', 'class', or 'subject'.
    - Teachers can only target subjects/classes they teach.
    - Students are strictly forbidden (403).
    """
    if current_user.role == "student":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Student accounts cannot send notifications."})
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only admins and teachers can send notifications."})

    if is_rate_limited(current_user.id):
        raise HTTPException(status_code=429, detail={"code": "RATE_LIMITED", "message": "Too many notifications sent. Please wait a minute."})

    # Validate Teacher Scope
    if current_user.role == "teacher":
        t_subjs, t_classes = get_user_enrolled_subjects_and_classes(current_user, db)
        if body.audience_type == "subject":
            if not body.subject_id or body.subject_id not in t_subjs:
                raise HTTPException(
                    status_code=403,
                    detail={"code": "UNAUTHORIZED_TARGET", "message": f"Teachers can only target subjects they are assigned to teach."},
                )
        elif body.audience_type == "class":
            if not body.class_id or body.class_id not in t_classes:
                raise HTTPException(
                    status_code=403,
                    detail={"code": "UNAUTHORIZED_TARGET", "message": f"Teachers can only target classes they are assigned to teach."},
                )

    sanitized_title = sanitize_text(body.title)
    sanitized_body = sanitize_text(body.body)
    now = datetime.now(timezone.utc).isoformat()

    notif = Notification(
        id=str(uuid.uuid4()),
        sender_id=current_user.id,
        sender_role=current_user.role,
        title=sanitized_title,
        body=sanitized_body,
        audience_type=body.audience_type,
        class_id=body.class_id,
        subject_id=body.subject_id,
        priority=body.priority,
        created_at=now,
        expires_at=body.expires_at,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    return {
        "id": notif.id,
        "title": notif.title,
        "body": notif.body,
        "audience_type": notif.audience_type,
        "priority": notif.priority,
        "created_at": notif.created_at,
        "sender_name": current_user.name,
        "sender_role": current_user.role,
    }


@router.get("")
def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List notifications visible to the caller, newest first, with read status.
    """
    u_subjs, u_classes = get_user_enrolled_subjects_and_classes(current_user, db)

    # Fetch all candidate notifications (excluding expired)
    now_str = datetime.now(timezone.utc).isoformat()
    all_notifs = db.query(Notification).order_by(Notification.created_at.desc()).all()

    # Filter by visibility rules
    visible = [n for n in all_notifs if (not n.expires_at or n.expires_at > now_str) and can_user_view_notification(current_user, n, u_subjs, u_classes)]

    # Fetch user's read receipts
    visible_ids = [n.id for n in visible]
    reads = db.query(NotificationRead.notification_id).filter(
        NotificationRead.user_id == current_user.id,
        NotificationRead.notification_id.in_(visible_ids),
    ).all()
    read_ids = {r[0] for r in reads}

    # Sender names lookup
    sender_ids = {n.sender_id for n in visible}
    senders = db.query(User.id, User.name).filter(User.id.in_(sender_ids)).all()
    sender_name_map = {s[0]: s[1] for s in senders}

    total = len(visible)
    unread_count = sum(1 for n in visible if n.id not in read_ids)

    # Pagination
    start = (page - 1) * page_size
    paged = visible[start : start + page_size]

    return {
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "audience_type": n.audience_type,
                "class_id": n.class_id,
                "subject_id": n.subject_id,
                "priority": n.priority,
                "created_at": n.created_at,
                "sender_id": n.sender_id,
                "sender_name": sender_name_map.get(n.sender_id, "System / Staff"),
                "sender_role": n.sender_role,
                "read": n.id in read_ids,
            }
            for n in paged
        ],
        "total": total,
        "unread_count": unread_count,
        "page": page,
        "page_size": page_size,
    }


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns quick unread notifications count for header badge."""
    res = list_notifications(page=1, page_size=100, db=db, current_user=current_user)
    return {"unread_count": res["unread_count"]}


@router.post("/{notification_id}/read")
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read for current user."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    existing = db.query(NotificationRead).filter(
        NotificationRead.notification_id == notification_id,
        NotificationRead.user_id == current_user.id,
    ).first()

    if not existing:
        now = datetime.now(timezone.utc).isoformat()
        db.add(NotificationRead(
            id=str(uuid.uuid4()),
            notification_id=notification_id,
            user_id=current_user.id,
            read_at=now,
        ))
        db.commit()

    return {"status": "read", "notification_id": notification_id}


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all visible notifications as read for current user."""
    u_subjs, u_classes = get_user_enrolled_subjects_and_classes(current_user, db)
    all_notifs = db.query(Notification).all()
    visible = [n for n in all_notifs if can_user_view_notification(current_user, n, u_subjs, u_classes)]

    existing_reads = {
        r[0] for r in db.query(NotificationRead.notification_id).filter(NotificationRead.user_id == current_user.id).all()
    }

    now = datetime.now(timezone.utc).isoformat()
    new_reads = []
    for n in visible:
        if n.id not in existing_reads:
            new_reads.append(NotificationRead(
                id=str(uuid.uuid4()),
                notification_id=n.id,
                user_id=current_user.id,
                read_at=now,
            ))

    if new_reads:
        db.bulk_save_objects(new_reads)
        db.commit()

    return {"status": "all_read", "marked_count": len(new_reads)}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a notification (Sender or Admin only)."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    if current_user.role != "admin" and notif.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "You can only delete notifications you sent."})

    db.delete(notif)
    db.commit()
    return {"status": "deleted", "notification_id": notification_id}


def notify_high_risk(db: Session, student_id: str, student_name: str, risk_level: str, reasons: list) -> None:
    """Internal helper: create an in-app high-risk alert notification for admin/staff."""
    if risk_level != "high":
        return
    notif = Notification(
        id=str(uuid.uuid4()),
        sender_id="system",
        sender_role="admin",
        title=f"High Risk Alert: {student_name}",
        body=f"Student {student_name} ({student_id}) flagged HIGH risk. Reasons: {', '.join(str(r) for r in reasons[:3])}",
        audience_type="all",
        priority="important",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(notif)
