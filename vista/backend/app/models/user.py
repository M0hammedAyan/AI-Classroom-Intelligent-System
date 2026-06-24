from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Text

from ..db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False)           # admin | hos | hop | mentor | teacher
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)

    # Organizational assignment (nullable — admin has no specific org)
    school_id = Column(Text, ForeignKey("schools.id"), nullable=True)
    department_id = Column(Text, ForeignKey("departments.id"), nullable=True)

    # Custom permissions (JSON array of permission strings)
    # e.g., ["view_attendance", "manage_scores", "recompute_risk"]
    custom_permissions = Column(Text, nullable=True)  # JSON
