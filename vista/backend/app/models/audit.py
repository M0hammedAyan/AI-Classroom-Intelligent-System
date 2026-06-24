"""Audit log — tracks all significant actions in the system."""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Text

from ..db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Text, primary_key=True)
    user_id = Column(Text, ForeignKey("users.id"), nullable=False)
    action = Column(Text, nullable=False)         # login | create_user | mark_attendance | recompute_risk | ...
    target_type = Column(Text, nullable=True)     # student | user | school | department
    target_id = Column(Text, nullable=True)       # ID of the affected resource
    details = Column(Text, nullable=True)         # JSON extra info
    ip_address = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)
