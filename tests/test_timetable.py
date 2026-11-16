"""
Timetable Feature Tests
=======================
Tests Part 1 timetable requirements:
1. Student weekly grid with today/current slot highlight & batch awareness.
2. Teacher view with today's classes, real-time status, and attendance gating.
3. Admin timetable manager: CRUD, double-booking validation, audit logging.
4. Admin student batch assignment.
5. Server clock mocking with VISTA_FAKE_NOW in Asia/Kolkata.
"""
import os
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from vista.backend.app.main import app
from vista.backend.app.db import SessionLocal
from vista.backend.app.models.user import User
from vista.backend.app.models.student import Student
from vista.backend.app.models.timetable import TimetableSlot
from vista.backend.app.models.audit import AuditLog
from vista.backend.app.routes.auth import _make_jwt


class TestTimetable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Ensure timetable slots exist in test DB before sessions open
        from scripts.seed_timetable import seed_timetable
        db_url = os.environ.get("VISTA_DB_URL", "sqlite:///./test_vista.db")
        db_path = db_url.replace("sqlite:///", "").replace("sqlite://", "")
        seed_timetable(db_path)

    def setUp(self):
        self.db = SessionLocal()
        os.environ["VISTA_ENV"] = "development"

        now = datetime.now(timezone.utc).isoformat()

        # Admin user
        admin = self.db.query(User).filter(User.id == "admin-user-01").first()
        if not admin:
            self.db.add(User(
                id="admin-user-01",
                name="System Administrator",
                email="admin-user-01@vista.local",
                password_hash="fakehash",
                role="admin",
                is_active=True,
                created_at=now,
            ))
        else:
            admin.is_active = True

        # Teacher Rajeshwari
        t_raj = self.db.query(User).filter(User.id == "a65d2ace-2522-4232-b597-b6e5beb3dce1").first()
        if not t_raj:
            self.db.add(User(
                id="a65d2ace-2522-4232-b597-b6e5beb3dce1",
                name="Rajeshwari",
                email="rajeshwari.h@vista.local",
                password_hash="fakehash",
                role="teacher",
                department_id="dept-aiml",
                is_active=True,
                created_at=now,
            ))
        else:
            t_raj.is_active = True

        from vista.backend.app.models.organization import TeacherSubjectAssignment
        import uuid

        # Ensure teacher assignments exist
        as1 = self.db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == "a65d2ace-2522-4232-b597-b6e5beb3dce1",
            TeacherSubjectAssignment.subject_id == "subject-22aiu701",
        ).first()
        if not as1:
            self.db.add(TeacherSubjectAssignment(
                id="assign-test-raj-dl",
                teacher_id="a65d2ace-2522-4232-b597-b6e5beb3dce1",
                subject_id="subject-22aiu701",
                class_section_id="class-aiml-4a",
                assigned_at=now,
                is_active=True,
            ))

        t_ajay = self.db.query(User).filter(User.id == "5efb33f0-4d32-4a3f-b607-7bbe772418e2").first()
        if not t_ajay:
            self.db.add(User(
                id="5efb33f0-4d32-4a3f-b607-7bbe772418e2",
                name="Ajayprakash B V",
                email="ajayprakash.h@vista.local",
                password_hash="fakehash",
                role="teacher",
                department_id="dept-aiml",
                is_active=True,
                created_at=now,
            ))
        as2 = self.db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == "5efb33f0-4d32-4a3f-b607-7bbe772418e2",
            TeacherSubjectAssignment.subject_id == "subject-22aiu702",
        ).first()
        if not as2:
            self.db.add(TeacherSubjectAssignment(
                id="assign-test-ajay-gai",
                teacher_id="5efb33f0-4d32-4a3f-b607-7bbe772418e2",
                subject_id="subject-22aiu702",
                class_section_id="class-aiml-4a",
                assigned_at=now,
                is_active=True,
            ))

        # Student 1DA23AI001
        s1 = self.db.query(Student).filter(Student.student_id == "1DA23AI001").first()
        if not s1:
            self.db.add(Student(
                student_id="1DA23AI001",
                name="Abhay B Suvarna",
                class_="4th Year AIML",
                classroom_id="class-aiml-4a",
                created_at=now,
            ))
        u1 = self.db.query(User).filter(User.id == "student-1DA23AI001").first()
        if not u1:
            self.db.add(User(
                id="student-1DA23AI001",
                name="Abhay B Suvarna",
                email="abhay@vista.local",
                password_hash="fakehash",
                role="student",
                is_active=True,
                created_at=now,
            ))
        else:
            u1.is_active = True

        # Student 1DA23AI002
        s2 = self.db.query(Student).filter(Student.student_id == "1DA23AI002").first()
        if not s2:
            self.db.add(Student(
                student_id="1DA23AI002",
                name="Adithi Rao",
                class_="4th Year AIML",
                classroom_id="class-aiml-4a",
                created_at=now,
            ))
        u2 = self.db.query(User).filter(User.id == "student-1DA23AI002").first()
        if not u2:
            self.db.add(User(
                id="student-1DA23AI002",
                name="Adithi Rao",
                email="adithi@vista.local",
                password_hash="fakehash",
                role="student",
                is_active=True,
                created_at=now,
            ))
        else:
            u2.is_active = True

        self.db.commit()

    def tearDown(self):
        if "VISTA_FAKE_NOW" in os.environ:
            del os.environ["VISTA_FAKE_NOW"]
        self.db.close()

    def test_student_timetable_view(self):
        """Student gets weekly grid with today and current slot highlighted."""
        # Mock time to Tuesday 09:15 IST (Slot S1: 09:00 - 09:55 DL)
        os.environ["VISTA_FAKE_NOW"] = "2026-11-10T09:15:00+05:30"

        # Student user (Abhay B Suvarna)
        token = _make_jwt("student-1DA23AI001", "student")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/timetable/student", headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertEqual(data["student"]["student_id"], "1DA23AI001")
        self.assertEqual(data["server_time_ist"]["day_of_week"], 1)  # Tuesday
        self.assertEqual(data["server_time_ist"]["time"], "09:15")

        slots = data["slots"]
        self.assertGreater(len(slots), 30)

        # Tuesday S1 should be marked is_current=True and is_today=True
        tue_s1 = next((s for s in slots if s["day_of_week"] == 1 and s["period_label"] == "S1"), None)
        self.assertIsNotNone(tue_s1)
        self.assertTrue(tue_s1["is_today"])
        self.assertTrue(tue_s1["is_current"])
        self.assertEqual(tue_s1["subject_code"], "22AIU701")
        self.assertEqual(tue_s1["teacher_name"], "Rajeshwari")

    def test_student_batch_filtering(self):
        """Student with batch B1 sees lab slots labeled for B1 without for_other_batch flag."""
        # Assign batch B1 to student
        student = self.db.query(Student).filter(Student.student_id == "1DA23AI001").first()
        student.batch = "B1"
        self.db.commit()

        token = _make_jwt("student-1DA23AI001", "student")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/timetable/student", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["student"]["batch"], "B1")

        slots = data["slots"]
        # Find Monday S1 slots (B1 vs B2)
        mon_s1_b1 = next((s for s in slots if s["id"] == "slot-7th-m-s1-b1"), None)
        mon_s1_b2 = next((s for s in slots if s["id"] == "slot-7th-m-s1-b2"), None)
        self.assertIsNotNone(mon_s1_b1)
        self.assertIsNotNone(mon_s1_b2)
        self.assertFalse(mon_s1_b1["for_other_batch"])
        self.assertTrue(mon_s1_b2["for_other_batch"])

    def test_teacher_timetable_view(self):
        """Teacher gets own slots + Today's real-time schedule with attendance status."""
        # Mrs. Rajeshwari: ID a65d2ace-2522-4232-b597-b6e5beb3dce1
        token = _make_jwt("a65d2ace-2522-4232-b597-b6e5beb3dce1", "teacher")
        headers = {"Authorization": f"Bearer {token}"}

        # Mock time to Tuesday 09:15 IST (her S1 class is active)
        os.environ["VISTA_FAKE_NOW"] = "2026-11-10T09:15:00+05:30"

        res = self.client.get("/api/v1/timetable/teacher", headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()

        self.assertEqual(data["teacher_name"], "Rajeshwari")
        self.assertEqual(data["server_time_ist"]["day_of_week"], 1)

        # Weekly slots should only be hers
        for s in data["weekly_slots"]:
            self.assertEqual(s["teacher_id"], "a65d2ace-2522-4232-b597-b6e5beb3dce1")

        # Today's classes should contain Tuesday S1 with status 'now'
        today_classes = data["today_classes"]
        self.assertGreaterEqual(len(today_classes), 1)
        s1 = next((c for c in today_classes if c["slot"]["period_label"] == "S1"), None)
        self.assertIsNotNone(s1)
        self.assertEqual(s1["status"], "now")
        self.assertTrue(s1["take_attendance_enabled"])

    def test_admin_slot_management_and_validation(self):
        """Admin timetable CRUD, double-booking detection, and audit logging."""
        token = _make_jwt("admin-user-01", "admin")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test teacher double-booking rejection (Mrs. Rajeshwari already has Tue S1 09:00-09:55)
        conflict_payload = {
            "class_section_id": "class-aiml-4a",
            "subject_id": "subject-22aiu701",
            "teacher_id": "a65d2ace-2522-4232-b597-b6e5beb3dce1",
            "day_of_week": 1,
            "start_time": "09:10",
            "end_time": "10:00",
            "room": "Room 999",
            "slot_type": "teaching",
        }
        res_conflict = self.client.post("/api/v1/timetable/admin/slots", json=conflict_payload, headers=headers)
        self.assertEqual(res_conflict.status_code, 409)
        self.assertIn("Teacher double-booking", res_conflict.json()["detail"])

        # 2. Test class double-booking rejection
        class_conflict = {
            "class_section_id": "class-aiml-4a",
            "subject_id": "subject-22aiu702",
            "teacher_id": "5efb33f0-4d32-4a3f-b607-7bbe772418e2",
            "day_of_week": 1,
            "start_time": "09:00",
            "end_time": "09:55",
            "room": "Room 999",
            "slot_type": "teaching",
        }
        res_class_conflict = self.client.post("/api/v1/timetable/admin/slots", json=class_conflict, headers=headers)
        self.assertEqual(res_class_conflict.status_code, 409)
        self.assertIn("Class double-booking", res_class_conflict.json()["detail"])

        # 3. Create a valid slot on Saturday evening
        valid_payload = {
            "class_section_id": "class-aiml-4a",
            "subject_id": "subject-22aiu701",
            "teacher_id": "a65d2ace-2522-4232-b597-b6e5beb3dce1",
            "day_of_week": 5,
            "start_time": "17:00",
            "end_time": "18:00",
            "room": "A-302",
            "period_label": "Extra S8",
            "slot_type": "teaching",
        }
        res_create = self.client.post("/api/v1/timetable/admin/slots", json=valid_payload, headers=headers)
        self.assertEqual(res_create.status_code, 201, res_create.text)
        created_slot = res_create.json()
        slot_id = created_slot["id"]

        # Verify audit log was created
        audit = self.db.query(AuditLog).filter(AuditLog.target_id == slot_id).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.action, "create_timetable_slot")

        # 4. Update the slot
        res_update = self.client.put(
            f"/api/v1/timetable/admin/slots/{slot_id}",
            json={"room": "Auditorium"},
            headers=headers,
        )
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()["room"], "Auditorium")

        # 5. Delete (soft-delete) the slot
        res_del = self.client.delete(f"/api/v1/timetable/admin/slots/{slot_id}", headers=headers)
        self.assertEqual(res_del.status_code, 200)
        deleted = self.db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
        self.assertFalse(deleted.is_active)

    def test_admin_assign_student_batch(self):
        """Admin assigns a lab batch to a student and creates an audit log."""
        token = _make_jwt("admin-user-01", "admin")
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.patch(
            "/api/v1/timetable/admin/students/1DA23AI002/batch",
            json={"batch": "B2"},
            headers=headers,
        )
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertEqual(data["batch"], "B2")

        # Check DB
        student = self.db.query(Student).filter(Student.student_id == "1DA23AI002").first()
        self.assertEqual(student.batch, "B2")

        # Check audit log
        audit = self.db.query(AuditLog).filter(
            AuditLog.target_id == "1DA23AI002",
            AuditLog.action == "assign_student_batch"
        ).first()
        self.assertIsNotNone(audit)
