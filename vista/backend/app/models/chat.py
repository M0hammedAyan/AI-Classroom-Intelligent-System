"""Chat message history model for AI Study Coach."""
from __future__ import annotations

from sqlalchemy import Column, Index, Text
from ..db import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_student_created", "student_id", "created_at"),
    )

    id = Column(Text, primary_key=True)
    student_id = Column(Text, nullable=False)
    role = Column(Text, nullable=False)       # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)
