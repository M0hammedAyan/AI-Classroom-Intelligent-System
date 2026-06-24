"""
Organization Hierarchy Models
==============================
School → Department → Class → Student (auto-assignment)
Roles: admin, hos, hop, mentor, teacher
"""
from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Text
from sqlalchemy.orm import relationship

from ..db import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(Text, primary_key=True)           # e.g., "school-cs"
    name = Column(Text, nullable=False)            # "School of Computer Science"
    code = Column(Text, unique=True, nullable=False)  # "CS"
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, nullable=False)

    departments = relationship("Department", back_populates="school")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Text, primary_key=True)           # e.g., "dept-aiml"
    school_id = Column(Text, ForeignKey("schools.id"), nullable=False)
    name = Column(Text, nullable=False)            # "Artificial Intelligence & ML"
    code = Column(Text, unique=True, nullable=False)  # "AIML"
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, nullable=False)

    school = relationship("School", back_populates="departments")
    classes = relationship("ClassSection", back_populates="department")


class ClassSection(Base):
    """A class/section within a department (e.g., AIML-3A, CSE-2B)"""
    __tablename__ = "class_sections"

    id = Column(Text, primary_key=True)           # e.g., "class-aiml-3a"
    department_id = Column(Text, ForeignKey("departments.id"), nullable=False)
    name = Column(Text, nullable=False)            # "AIML 3rd Year A"
    code = Column(Text, unique=True, nullable=False)  # "AIML-3A"
    semester = Column(Text, nullable=True)         # "6"
    is_active = Column(Boolean, default=True)
    created_at = Column(Text, nullable=False)

    department = relationship("Department", back_populates="classes")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Text, primary_key=True)
    department_id = Column(Text, ForeignKey("departments.id"), nullable=False)
    name = Column(Text, nullable=False)            # "Data Structures"
    code = Column(Text, nullable=False)            # "CS301"
    semester = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)


class MentorAssignment(Base):
    """Maps a mentor to their assigned students."""
    __tablename__ = "mentor_assignments"

    id = Column(Text, primary_key=True)
    mentor_id = Column(Text, ForeignKey("users.id"), nullable=False)
    student_id = Column(Text, ForeignKey("students.student_id"), nullable=False)
    assigned_at = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)


class TeacherSubjectAssignment(Base):
    """Maps a teacher to their subjects and classes."""
    __tablename__ = "teacher_subjects"

    id = Column(Text, primary_key=True)
    teacher_id = Column(Text, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Text, ForeignKey("subjects.id"), nullable=False)
    class_section_id = Column(Text, ForeignKey("class_sections.id"), nullable=False)
    assigned_at = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)


class AccessRequest(Base):
    """
    Requests from teachers/mentors to HOP/HOS for access to students.
    Workflow: teacher requests → HOP/HOS approves/rejects.
    """
    __tablename__ = "access_requests"

    id = Column(Text, primary_key=True)
    requester_id = Column(Text, ForeignKey("users.id"), nullable=False)  # who is asking
    request_type = Column(Text, nullable=False)    # "mentor_students" | "subject_class"
    target_details = Column(Text, nullable=False)  # JSON: {student_ids, class_id, subject_id}
    status = Column(Text, nullable=False, default="pending")  # pending | approved | rejected
    reviewed_by = Column(Text, ForeignKey("users.id"), nullable=True)
    review_note = Column(Text, nullable=True)
    created_at = Column(Text, nullable=False)
    reviewed_at = Column(Text, nullable=True)
