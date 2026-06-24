from __future__ import annotations

from sqlalchemy import Boolean, Column, Text

from ..db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False)           # admin | teacher
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)
