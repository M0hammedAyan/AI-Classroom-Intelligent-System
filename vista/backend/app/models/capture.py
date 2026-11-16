"""
Capture History Event Model
===========================
Stores metadata for face attendance capture attempts.
STRICT PRIVACY RULE: NEVER stores captured photos, images, or face embeddings.
Only sha256 hash of image and count metadata are recorded.
"""
from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from ..db import Base


class CaptureEvent(Base):
    """Metadata audit event for attendance capture operations."""
    __tablename__ = "capture_events"

    id = Column(Text, primary_key=True)
    teacher_id = Column(Text, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=True)
    class_id = Column(Text, ForeignKey("class_sections.id"), nullable=False)
    slot_id = Column(Text, ForeignKey("timetable_slots.id"), nullable=True)
    captured_at = Column(Text, nullable=False)  # ISO 8601 UTC
    source = Column(Text, nullable=False, default="face")  # face | manual
    faces_detected = Column(Integer, nullable=False, default=0)
    recognized_count = Column(Integer, nullable=False, default=0)
    unrecognized_count = Column(Integer, nullable=False, default=0)
    liveness_rejected_count = Column(Integer, nullable=False, default=0)
    duplicates_skipped = Column(Integer, nullable=False, default=0)
    status = Column(Text, nullable=False, default="completed")  # completed | failed
    is_extra_class = Column(Boolean, nullable=False, default=False)
    reason = Column(Text, nullable=True)
    image_sha256 = Column(Text, nullable=True)  # Cryptographic hash only
