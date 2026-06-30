"""Timetable, Announcements, Study Materials, Assignments, Semester Results models."""
from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, Text
from ..db import Base


class TimetableSlot(Base):
    """One period/slot in the weekly timetable."""
    __tablename__ = "timetable_slots"

    id = Column(Text, primary_key=True)
    class_section_id = Column(Text, ForeignKey("class_sections.id"), nullable=False)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Text, ForeignKey("users.id"), nullable=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 1=Tuesday ... 4=Friday
    start_time = Column(Text, nullable=False)       # "09:00"
    end_time = Column(Text, nullable=False)         # "10:00"
    room = Column(Text, nullable=True)              # "Room 301"
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, nullable=False)


class Announcement(Base):
    """General announcements/notices from HOP/HOS/Admin."""
    __tablename__ = "announcements"

    id = Column(Text, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Text, ForeignKey("users.id"), nullable=False)
    target_scope = Column(Text, nullable=False)     # "all" | "school:{id}" | "dept:{id}" | "class:{code}"
    priority = Column(Text, nullable=False, default="normal")  # normal | important | urgent
    is_active = Column(Boolean, default=True)
    expires_at = Column(Text, nullable=True)        # ISO date after which it's hidden
    created_at = Column(Text, nullable=False)


class StudyMaterial(Base):
    """Study materials/notes uploaded by teachers."""
    __tablename__ = "study_materials"

    id = Column(Text, primary_key=True)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=False)
    class_section_id = Column(Text, ForeignKey("class_sections.id"), nullable=True)
    uploaded_by = Column(Text, ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)        # Relative path on server
    file_size = Column(Integer, nullable=True)      # bytes
    file_type = Column(Text, nullable=True)         # pdf, pptx, docx, etc.
    created_at = Column(Text, nullable=False)


class Assignment(Base):
    """Assignment created by teacher for a class."""
    __tablename__ = "assignments"

    id = Column(Text, primary_key=True)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=False)
    class_section_id = Column(Text, ForeignKey("class_sections.id"), nullable=False)
    teacher_id = Column(Text, ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    max_marks = Column(Float, nullable=True)
    due_date = Column(Text, nullable=False)         # YYYY-MM-DD
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, nullable=False)


class AssignmentSubmission(Base):
    """Student's submission for an assignment."""
    __tablename__ = "assignment_submissions"

    id = Column(Text, primary_key=True)
    assignment_id = Column(Text, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    submitted_at = Column(Text, nullable=False)
    file_name = Column(Text, nullable=True)
    file_path = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)             # Student comments
    marks = Column(Float, nullable=True)            # Graded by teacher
    graded_at = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)          # Teacher feedback


class SemesterResult(Base):
    """Final semester exam results."""
    __tablename__ = "semester_results"

    id = Column(Text, primary_key=True)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=False)
    semester = Column(Text, nullable=False)         # "7"
    academic_year = Column(Text, nullable=False)    # "2025-26"
    marks_obtained = Column(Float, nullable=False)
    max_marks = Column(Float, nullable=False)
    grade = Column(Text, nullable=True)             # "A", "B+", "C", "F", etc.
    credits = Column(Float, nullable=True)
    result = Column(Text, nullable=False)           # "pass" | "fail" | "absent"
    declared_at = Column(Text, nullable=True)       # When results were published
    created_at = Column(Text, nullable=False)


class ParentContact(Base):
    """Parent/guardian contact for a student (for alerts)."""
    __tablename__ = "parent_contacts"

    id = Column(Text, primary_key=True)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    parent_name = Column(Text, nullable=False)
    relation = Column(Text, nullable=False)         # "father" | "mother" | "guardian"
    phone = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=True)
    alert_enabled = Column(Boolean, default=True)   # Whether to send auto-alerts
    created_at = Column(Text, nullable=False)


class ParentAlert(Base):
    """Log of alerts sent to parents."""
    __tablename__ = "parent_alerts"

    id = Column(Text, primary_key=True)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    parent_contact_id = Column(Text, ForeignKey("parent_contacts.id"), nullable=False)
    alert_type = Column(Text, nullable=False)       # "attendance_low" | "risk_high" | "result_declared"
    message = Column(Text, nullable=False)
    channel = Column(Text, nullable=False)          # "sms" | "email"
    status = Column(Text, nullable=False)           # "sent" | "failed" | "pending"
    sent_at = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)
