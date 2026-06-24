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

    classroom = relationship("Classroom", back_populates="students")
    attendance_records = relationship("Attendance", back_populates="student")
    scores = relationship("Score", back_populates="student")
    risk_flags = relationship("RiskFlag", back_populates="student")
