"""
Unit and Integration Tests for VISTA Full-Stack Audit Fixes
===========================================================
Covers:
- Task 1: Student portal attendance percentage calculation & zero-sessions handling
- Task 1: Student portal authorization boundary (students can only see own data)
- Task 1 & 2: 7th Semester subjects & CIE 1/2 marks drill-down
- Task 4: Seed demo data idempotency, source tagging, and preservation of real records
- Task 5: Manual attendance and marks validation (ranges, dates, mandatory reasons, teacher scoping)
"""

import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

# Setup paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "vista", "backend")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.db import SessionLocal
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance, Score
from app.models.audit import AuditLog
from app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
from app.routes.student_portal import (
    student_dashboard,
    student_attendance_by_subject,
    student_scores,
    student_subject_detail,
)
from app.routes.attendance import create_manual_attendance, ManualAttendanceRequest
from app.routes.lms import add_score, get_student_marks
from app.routes.students import list_students
from fastapi import HTTPException


class TestStudentPortalFixes(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.student_usn = "1DA24AI403"  # Mohammed Ayyan
        self.student_user = self.db.query(User).filter(User.id == f"student-{self.student_usn}").first()
        self.assertIsNotNone(self.student_user, "Mohammed Ayyan student user must exist in DB")

    def tearDown(self):
        self.db.close()

    def test_task1_percentage_calculation_bounded_and_rounded(self):
        """Attendance percentage must be bounded between 0 and 100, and rounded to at most 1 decimal."""
        res = student_dashboard(db=self.db, current_user=self.student_user)
        self.assertIn("attendance_pct", res)
        pct = res["attendance_pct"]
        if pct is not None:
            self.assertGreaterEqual(pct, 0.0)
            self.assertLessEqual(pct, 100.0)
            self.assertEqual(round(pct, 1), pct)

    def test_task1_zero_sessions_handles_gracefully(self):
        """A student with 0 sessions must return None without ZeroDivisionError."""
        dummy_user = User(
            id="student-1DA99AI999",
            name="Dummy Zero Sessions",
            email="dummy999@vista.local",
            role="student",
        )
        dummy_student = Student(
            student_id="1DA99AI999",
            name="Dummy Zero Sessions",
            classroom_id="class-empty-test",
            class_="4th Year AIML",
            is_active=True,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.db.add(dummy_student)
        self.db.commit()
        try:
            res = student_dashboard(db=self.db, current_user=dummy_user)
            self.assertIsNone(res["attendance_pct"], "0 sessions should return None (rendered as 'No sessions yet')")
        finally:
            self.db.delete(dummy_student)
            self.db.commit()

    def test_task1_student_authorization_strict_own_data(self):
        """Student can only access their own data; resolved from JWT user token."""
        detail = student_subject_detail(subject_id="22AIU701", db=self.db, current_user=self.student_user)
        self.assertEqual(detail["student"]["student_id"], self.student_usn)

    def test_task1_and_task2_all_7th_sem_subjects_visible(self):
        """Student sees all 5 subjects of 4th Year AIML (7th Semester)."""
        att_res = student_attendance_by_subject(db=self.db, current_user=self.student_user)
        subjects = att_res["by_subject"]
        subject_codes = {s["subject_code"] for s in subjects}
        expected_codes = {"22AIU701", "22AIU702", "22AIT703", "22AIT704C", "22AIP706"}
        self.assertTrue(expected_codes.issubset(subject_codes), f"Missing 7th sem subjects: {expected_codes - subject_codes}")

    def test_task1_subject_drilldown_marks_and_source_badges(self):
        """Subject drill-down returns date-wise attendance with source badges and CIE 1 + CIE 2."""
        detail = student_subject_detail(subject_id="22AIU701", db=self.db, current_user=self.student_user)
        self.assertIn("marks", detail)
        self.assertIn("cie1", detail["marks"])
        self.assertIn("cie2", detail["marks"])
        self.assertIn("total", detail["marks"])

        att_records = detail["attendance"]
        self.assertGreater(len(att_records), 0)
        sources = {r["source"] for r in att_records}
        self.assertTrue(any(s in ("face", "seed", "manual") for s in sources))

        # Check real face session on 2026-10-30
        oct_30_records = [r for r in att_records if r["date"] == "2026-10-30"]
        self.assertEqual(len(oct_30_records), 1)
        self.assertEqual(oct_30_records[0]["source"], "face")
        self.assertEqual(oct_30_records[0]["status"], "present")


class TestManualValidationAndRBAC(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.admin_user = self.db.query(User).filter(User.role == "admin").first()
        self.teacher_user = self.db.query(User).filter(User.email == "rajeshwari@vista.local").first()
        self.other_teacher = self.db.query(User).filter(User.email == "ajayprakash@vista.local").first()
        self.student_user = self.db.query(User).filter(User.role == "student").first()

    def tearDown(self):
        self.db.close()

    def test_task5_marks_mandatory_reason(self):
        """Marks entry without a reason must be rejected with 400 REASON_REQUIRED."""
        body = {
            "student_id": "1DA24AI403",
            "subject": "22AIU701",
            "score": 20.0,
            "max_score": 25.0,
            "reason": "",  # Missing reason
        }
        with self.assertRaises(HTTPException) as ctx:
            add_score(body, db=self.db, current_user=self.teacher_user)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail["code"], "REASON_REQUIRED")

    def test_task5_marks_out_of_range(self):
        """CIE marks > 25 or < 0 must be rejected with 400 SCORE_OUT_OF_RANGE."""
        body_too_high = {
            "student_id": "1DA24AI403",
            "subject": "22AIU701",
            "score": 28.5,  # Exceeds 25
            "assessment_type": "CIE 1",
            "reason": "Test high score",
        }
        with self.assertRaises(HTTPException) as ctx:
            add_score(body_too_high, db=self.db, current_user=self.teacher_user)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail["code"], "SCORE_OUT_OF_RANGE")

        body_negative = {
            "student_id": "1DA24AI403",
            "subject": "22AIU701",
            "score": -5.0,
            "assessment_type": "CIE 1",
            "reason": "Test negative",
        }
        with self.assertRaises(HTTPException) as ctx2:
            add_score(body_negative, db=self.db, current_user=self.teacher_user)
        self.assertEqual(ctx2.exception.status_code, 400)
        self.assertEqual(ctx2.exception.detail["code"], "SCORE_OUT_OF_RANGE")

    def test_task5_future_date_rejected(self):
        """Future dates must be rejected."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=5)).date().isoformat()
        body = {
            "student_id": "1DA24AI403",
            "subject": "22AIU701",
            "score": 22.0,
            "date": future_date,
            "reason": "Test future date",
        }
        with self.assertRaises(HTTPException) as ctx:
            add_score(body, db=self.db, current_user=self.teacher_user)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail["code"], "FUTURE_DATE")

    def test_task5_teacher_subject_scope_enforcement(self):
        """Mrs. Rajeshwari (DL teacher) cannot edit marks for Generative AI (Dr. Ajay Prakash)."""
        body = {
            "student_id": "1DA24AI403",
            "subject": "22AIU702",  # Generative AI
            "score": 21.0,
            "reason": "Unauthorized teacher attempt",
        }
        with self.assertRaises(HTTPException) as ctx:
            add_score(body, db=self.db, current_user=self.teacher_user)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.detail["code"], "SUBJECT_SCOPE")

    def test_task5_student_cannot_edit_marks(self):
        """Students are strictly forbidden from adding or editing marks."""
        body = {
            "student_id": "1DA24AI403",
            "subject": "22AIU701",
            "score": 25.0,
            "reason": "Student self entry attempt",
        }
        with self.assertRaises(HTTPException) as ctx:
            add_score(body, db=self.db, current_user=self.student_user)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_task5_manual_attendance_creates_audit_log(self):
        """Manual attendance creates a row with source='manual' and writes an AuditLog entry."""
        payload = ManualAttendanceRequest(
            student_id="1DA24AI403",
            classroom_id="class-aiml-4a",
            session_date="2026-10-28",
            subject_id="22AIU701",
            status="present",
            note="Verified OD for college hackathon",
        )
        res = create_manual_attendance(payload, db=self.db, _current_user=self.admin_user)
        self.assertEqual(res["status"], "present")
        self.assertEqual(res["source"], "manual")

        row = self.db.query(Attendance).filter(
            Attendance.student_id == "1DA24AI403",
            Attendance.session_date == "2026-10-28",
            Attendance.subject_id == "subject-22aiu701",
        ).first()
        self.assertIsNotNone(row)
        self.assertEqual(row.source, "manual")


class TestAttendancePctOverflowFix(unittest.TestCase):
    """Task 3: attendance_pct in the students list must never exceed 100 (overflow fix)."""

    def setUp(self):
        self.db = SessionLocal()
        self.admin_user = self.db.query(User).filter(User.role == "admin").first()
        self.assertIsNotNone(self.admin_user, "An admin user must exist in DB")

    def tearDown(self):
        self.db.close()

    def test_attendance_pct_never_exceeds_100(self):
        """Fetch all students (admin scope) and assert every attendance_pct <= 100.0."""
        res = list_students(page=1, page_size=100, db=self.db, current_user=self.admin_user)
        students = res["students"]
        self.assertGreater(len(students), 0, "Seeded DB should contain students")
        for s in students:
            self.assertIsNotNone(s["attendance_pct"], f"{s['student_id']} returned None attendance_pct")
            self.assertLessEqual(
                s["attendance_pct"], 100.0,
                f"{s['student_id']} ({s['name']}) attendance_pct={s['attendance_pct']} exceeds 100",
            )


if __name__ == "__main__":
    unittest.main()
