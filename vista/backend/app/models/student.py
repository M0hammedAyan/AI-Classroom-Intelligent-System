from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Text
from sqlalchemy.orm import relationship

from ..db import Base


class Classroom(Base):
    __tablename__ = "classrooms"

    classroom_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)

    students = relationship("Student", back_populates="classroom")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    class_ = Column("class", Text, nullable=False)
    classroom_id = Column(Text, ForeignKey("classrooms.classroom_id"), nullable=False)
    embedding = Column(Text, nullable=True)
    enrolled_at = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(Text, nullable=False)

    # Profile fields
    usn = Column(Text, nullable=True)                  # University Seat Number (editable once)
    usn_updated = Column(Boolean, nullable=False, default=False)  # True after first USN update
    phone = Column(Text, nullable=True)
    extracurricular = Column(Text, nullable=True)      # JSON array of activities

    classroom = relationship("Classroom", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")
    scores = relationship("Score", back_populates="student")
    risk_flags = relationship("RiskFlag", back_populates="student")
