"""In-app notification and read receipt models."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Text, UniqueConstraint
from ..db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Text, primary_key=True)
    sender_id = Column(Text, nullable=False)
    sender_role = Column(Text, nullable=False)           # admin | teacher | system
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    audience_type = Column(Text, nullable=False, default="all")  # all | class | subject
    class_id = Column(Text, nullable=True)
    subject_id = Column(Text, nullable=True)
    priority = Column(Text, nullable=False, default="normal")    # normal | important
    created_at = Column(Text, nullable=False)
    expires_at = Column(Text, nullable=True)


class NotificationRead(Base):
    __tablename__ = "notification_reads"
    __table_args__ = (
        UniqueConstraint("notification_id", "user_id", name="uq_notification_user_read"),
    )

    id = Column(Text, primary_key=True)
    notification_id = Column(Text, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Text, ForeignKey("users.id"), nullable=False)
    read_at = Column(Text, nullable=False)
