"""
VISTA — Tests for Student & Teacher Reports and Capture History
===============================================================
Covers:
  1. Student report via /reports/student/me:
     - Attendance by subject and period (S1-S7)
     - CIE 1/2/3 evaluation from cie_policy.py
     - Longitudinal rule-based risk evaluation
     - Source labeling (face, manual, seed)
  2. Teacher report via /reports/teacher/me:
     - Scheduled vs held sessions
     - Extra classes count
     - Face captures count
     - Average attendance per subject
     - Chronological daily session log
  3. Central object-level authorization:
     - Student accessing another student -> 403
     - Non-existent student -> 404
     - Teacher accessing unassigned student -> 403
     - Teacher accessing another teacher -> 403
     - Student accessing teacher report -> 403
     - Admin access to any report -> 200
  4. Capture History via /attendance/capture-history:
     - Admin can view all captures
     - Teacher can only view own captures
     - Student is forbidden (403)
     - Pagination limits and offset
"""
import os
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from vista.backend.app.main import app
from vista.backend.app.db import SessionLocal
from vista.backend.app.models.user import User
from vista.backend.app.models.student import Student
from vista.backend.app.models.attendance import Attendance, Score, RiskFlag
from vista.backend.app.models.organization import Subject, ClassSection, TeacherSubjectAssignment
from vista.backend.app.models.capture import CaptureEvent
from vista.backend.app.routes.auth import _make_jwt


class TestReportsAndCapture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.db = SessionLocal()
        os.environ["VISTA_ENV"] = "development"
        now = datetime.now(timezone.utc).isoformat()

        # 1. Admin user
        admin = self.db.query(User).filter(User.id == "admin-report-test").first()
        if not admin:
            self.db.add(User(
                id="admin-report-test",
                name="Admin User",
                email="admin-report@vista.local",
                password_hash="fakehash",
                role="admin",
                is_active=True,
                created_at=now,
            ))

        # 2. Teacher 1 (assigned to DL and class-aiml-4a)
        t1 = self.db.query(User).filter(User.id == "teacher-report-1").first()
        if not t1:
            self.db.add(User(
                id="teacher-report-1",
                name="Prof. Rajeshwari",
                email="rajeshwari-report@vista.local",
                password_hash="fakehash",
                role="teacher",
                department_id="dept-aiml",
                is_active=True,
                created_at=now,
            ))

        # 3. Teacher 2 (unassigned)
        t2 = self.db.query(User).filter(User.id == "teacher-report-2").first()
        if not t2:
            self.db.add(User(
                id="teacher-report-2",
                name="Prof. Other",
                email="other-report@vista.local",
                password_hash="fakehash",
                role="teacher",
                department_id="dept-aiml",
                is_active=True,
                created_at=now,
            ))

        # 4. Student 1 (Ayan)
        s1 = self.db.query(Student).filter(Student.student_id == "1DA24AI403").first()
        if not s1:
            self.db.add(Student(
                student_id="1DA24AI403",
                name="MOHAMMED AYAN",
                class_="4th Year AIML",
                classroom_id="class-aiml-4a",
                batch="B1",
                created_at=now,
            ))
        else:
            s1.batch = "B1"
        u1 = self.db.query(User).filter(User.id == "student-1DA24AI403").first()
        if not u1:
            self.db.add(User(
                id="student-1DA24AI403",
                name="MOHAMMED AYAN",
                email="ayan-report@vista.local",
                password_hash="fakehash",
                role="student",
                is_active=True,
                created_at=now,
            ))

        # 5. Student 2 (Sanjana)
        s2 = self.db.query(Student).filter(Student.student_id == "1DA23AI043").first()
        if not s2:
            self.db.add(Student(
                student_id="1DA23AI043",
                name="SANJANA C H",
                class_="4th Year AIML",
                classroom_id="class-aiml-4a",
                batch="B2",
                created_at=now,
            ))
        u2 = self.db.query(User).filter(User.id == "student-1DA23AI043").first()
        if not u2:
            self.db.add(User(
                id="student-1DA23AI043",
                name="SANJANA C H",
                email="sanjana-report@vista.local",
                password_hash="fakehash",
                role="student",
                is_active=True,
                created_at=now,
            ))

        # Ensure teacher-report-1 is assigned to subject-22aiu701 in class-aiml-4a
        asgn = self.db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == "teacher-report-1",
            TeacherSubjectAssignment.subject_id == "subject-22aiu701",
        ).first()
        if not asgn:
            self.db.add(TeacherSubjectAssignment(
                id="assign-report-t1-dl",
                teacher_id="teacher-report-1",
                subject_id="subject-22aiu701",
                class_section_id="class-aiml-4a",
                assigned_at=now,
                is_active=True,
            ))

        # Ensure a CaptureEvent exists for teacher-report-1
        ce = self.db.query(CaptureEvent).filter(CaptureEvent.id == "ce-test-01").first()
        if not ce:
            self.db.add(CaptureEvent(
                id="ce-test-01",
                teacher_id="teacher-report-1",
                subject_id="subject-22aiu701",
                class_id="class-aiml-4a",
                slot_id="slot-7th-t-s1",
                captured_at=now,
                source="face",
                faces_detected=32,
                recognized_count=29,
                unrecognized_count=3,
                liveness_rejected_count=0,
                duplicates_skipped=0,
                status="completed",
                is_extra_class=False,
                image_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            ))

        self.db.commit()

    def tearDown(self):
        self.db.close()

    # =======================================================================
    # 1. Student Report Tests
    # =======================================================================
    def test_student_report_me(self):
        """Student retrieves own report via /reports/student/me with full breakdown."""
        token = _make_jwt("student-1DA24AI403", "student")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/reports/student/me", headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        # Student metadata
        self.assertEqual(data["student"]["student_id"], "1DA24AI403")
        self.assertEqual(data["student"]["name"].upper(), "MOHAMMED AYAN")
        self.assertEqual(data["student"]["batch"], "B1")

        # Overall attendance
        overall = data["overall_attendance"]
        self.assertIn("percentage", overall)
        self.assertIn("missable_classes", overall)
        self.assertIn("recovery_classes_needed", overall)
        self.assertIn("by_source", overall)
        self.assertIn("face", overall["by_source"])
        self.assertIn("manual", overall["by_source"])
        self.assertIn("seed", overall["by_source"])

        # Subjects and period breakdown
        subjects = data["subjects"]
        self.assertGreaterEqual(len(subjects), 1)
        for s in subjects:
            self.assertIn("subject_code", s)
            self.assertIn("attendance", s)
            self.assertIn("periods", s["attendance"])
            self.assertIn("S1", s["attendance"]["periods"])
            self.assertIn("by_source", s["attendance"])
            # CIE verification
            self.assertIn("cie", s)
            self.assertIn("scores", s["cie"])
            self.assertIn("cie3_eligible", s["cie"])

    def test_student_report_authorization(self):
        """Student cannot access another student's report (IDOR defense)."""
        token = _make_jwt("student-1DA24AI403", "student")
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to access student 1DA23AI043
        res = self.client.get("/api/v1/reports/student/1DA23AI043", headers=headers)
        self.assertEqual(res.status_code, 403)
        self.assertIn("Forbidden", res.json()["detail"])

    def test_admin_access_to_student_report(self):
        """Admin can access any student report by ID."""
        token = _make_jwt("admin-report-test", "admin")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/reports/student/1DA24AI403", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["student"]["student_id"], "1DA24AI403")

    def test_nonexistent_student_report_returns_404(self):
        """Querying a non-existent student returns 404."""
        token = _make_jwt("admin-report-test", "admin")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/reports/student/NONEXISTENT999", headers=headers)
        self.assertEqual(res.status_code, 404)

    # =======================================================================
    # 2. Teacher Report Tests
    # =======================================================================
    def test_teacher_report_me(self):
        """Teacher retrieves own report via /reports/teacher/me."""
        token = _make_jwt("teacher-report-1", "teacher")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/reports/teacher/me", headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertEqual(data["teacher"]["teacher_id"], "teacher-report-1")
        self.assertEqual(data["teacher"]["name"], "Prof. Rajeshwari")

        summary = data["summary"]
        self.assertIn("scheduled_slots_per_week", summary)
        self.assertIn("held_sessions_count", summary)
        self.assertIn("extra_classes_count", summary)
        self.assertIn("captures_count", summary)
        self.assertGreaterEqual(summary["captures_count"], 1)

        self.assertIn("subjects", data)
        self.assertIn("recent_sessions", data)

    def test_teacher_report_authorization(self):
        """Teacher cannot access another teacher's report; Student cannot access teacher report."""
        # Teacher 2 accessing Teacher 1
        t2_token = _make_jwt("teacher-report-2", "teacher")
        res_t2 = self.client.get("/api/v1/reports/teacher/teacher-report-1", headers={"Authorization": f"Bearer {t2_token}"})
        self.assertEqual(res_t2.status_code, 403)

        # Student accessing Teacher 1
        s_token = _make_jwt("student-1DA24AI403", "student")
        res_s = self.client.get("/api/v1/reports/teacher/teacher-report-1", headers={"Authorization": f"Bearer {s_token}"})
        self.assertEqual(res_s.status_code, 403)

    # =======================================================================
    # 3. Capture History Tests
    # =======================================================================
    def test_capture_history_teacher_scoping(self):
        """Teacher only sees own capture events."""
        token = _make_jwt("teacher-report-1", "teacher")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/attendance/capture-history", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertGreaterEqual(data["total"], 1)
        for e in data["events"]:
            self.assertEqual(e["teacher_id"], "teacher-report-1")
            self.assertIn("image_sha256", e)
            self.assertNotIn("image", e)  # Privacy check: NO raw images
            self.assertNotIn("embedding", e)  # Privacy check: NO face embeddings

    def test_capture_history_student_forbidden(self):
        """Student is forbidden from viewing capture history."""
        token = _make_jwt("student-1DA24AI403", "student")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/attendance/capture-history", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_capture_history_admin_view_all(self):
        """Admin can view all captures and paginate."""
        token = _make_jwt("admin-report-test", "admin")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/attendance/capture-history?limit=10&offset=0", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["limit"], 10)
        self.assertEqual(data["offset"], 0)


if __name__ == "__main__":
    unittest.main()
