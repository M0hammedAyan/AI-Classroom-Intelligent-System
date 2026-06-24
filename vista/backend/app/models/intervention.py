"""Intervention tracking — mentors log actions taken for students."""
from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Text

from ..db import Base


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Text, primary_key=True)
    mentor_id = Column(Text, ForeignKey("users.id"), nullable=False)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    type = Column(Text, nullable=False)          # counselling | call | meeting | referral | email
    notes = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)        # pending | improved | no_change | escalated
    created_at = Column(Text, nullable=False)
