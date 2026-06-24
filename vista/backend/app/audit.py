"""
Audit Logger — Records significant system actions.
Called from routes when important events happen.

Usage:
    from ..audit import log_action
    log_action(db, user_id="...", action="mark_attendance", target_type="student", target_id="CS22B001")
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session


def log_action(
    db: Session,
    user_id: str,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    details: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Write an audit log entry. Non-blocking — won't raise on failure."""
    try:
        from .models.audit import AuditLog
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc).isoformat(),
        ))
    except Exception:
        pass  # Never let audit logging break the main flow
