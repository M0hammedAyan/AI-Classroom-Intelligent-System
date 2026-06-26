from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from ..db import Base


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        Index("ix_attendance_student_date", "student_id", "session_date"),
        Index("ix_attendance_classroom_date", "classroom_id", "session_date"),
        UniqueConstraint("student_id", "session_date", "status", name="uq_attendance_student_day_status",
                         sqlite_on_conflict="IGNORE"),
    )

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
    __table_args__ = (
        Index("ix_scores_student_date", "student_id", "date"),
    )

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
    __table_args__ = (
        Index("ix_risk_student_calc", "student_id", "calculated_at"),
    )

    id = Column(Text, primary_key=True)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    risk_level = Column(Text, nullable=False)     # low | medium | high
    reasons = Column(Text, nullable=False)        # JSON array string
    confidence = Column(Text, nullable=False)     # high | moderate | low
    calculated_at = Column(Text, nullable=False)
    created_at = Column(Text, nullable=False)

    student = relationship("Student", back_populates="risk_flags")
