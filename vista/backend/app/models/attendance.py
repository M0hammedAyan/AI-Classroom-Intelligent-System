from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from ..db import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Text, primary_key=True)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=True)
    classroom_id = Column(Text, ForeignKey("classrooms.classroom_id"), nullable=False)
    session_date = Column(Text, nullable=False)   # YYYY-MM-DD
    timestamp = Column(Text, nullable=False)      # ISO 8601 UTC
    status = Column(Text, nullable=False)         # present | liveness_failed | absent
    confidence = Column(Float, nullable=True)
    is_manual_override = Column(Boolean, nullable=False, default=False)
    override_note = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)

    student = relationship("Student", back_populates="attendance_records")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Text, primary_key=True)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    subject = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    date = Column(Text, nullable=False)           # YYYY-MM-DD
    created_at = Column(Text, nullable=False)

    student = relationship("Student", back_populates="scores")


class RiskFlag(Base):
    __tablename__ = "risk_flags"

    id = Column(Text, primary_key=True)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    risk_level = Column(Text, nullable=False)     # low | medium | high
    reasons = Column(Text, nullable=False)        # JSON array string
    confidence = Column(Text, nullable=False)     # high | moderate | low
    calculated_at = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)

    student = relationship("Student", back_populates="risk_flags")
