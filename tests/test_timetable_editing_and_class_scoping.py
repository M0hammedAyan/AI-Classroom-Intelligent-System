import os
import unittest
from fastapi.testclient import TestClient
from vista.backend.app.main import app
from vista.backend.app.db import SessionLocal
from vista.backend.app.models.user import User
from vista.backend.app.models.timetable import TimetableSlot
from vista.backend.app.models.student import Student
from vista.backend.app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
from vista.backend.app.routes.auth import _make_jwt

class TestTimetableEditingAndClassScoping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Ensure Admin User
        admin = cls.db.query(User).filter(User.id == "admin-test-scope").first()
        if not admin:
            admin = User(
                id="admin-test-scope",
                email="admin-scope@vista.local",
                name="Scope Admin",
                role="admin",
                is_active=True,
                password_hash="pw",
                created_at="2026-08-01T00:00:00Z",
            )
            cls.db.add(admin)

        # Teacher 1 (Rajeshwari)
        t1 = cls.db.query(User).filter(User.id == "t1-scope").first()
        if not t1:
            t1 = User(
                id="t1-scope",
                email="t1-scope@vista.local",
                name="Teacher One",
                role="teacher",
                is_active=True,
                password_hash="pw",
                created_at="2026-08-01T00:00:00Z",
            )
            cls.db.add(t1)

        # Teacher 2 (Ajayprakash)
        t2 = cls.db.query(User).filter(User.id == "t2-scope").first()
        if not t2:
            t2 = User(
                id="t2-scope",
                email="t2-scope@vista.local",
                name="Teacher Two",
                role="teacher",
                is_active=True,
                password_hash="pw",
                created_at="2026-08-01T00:00:00Z",
            )
            cls.db.add(t2)

        # Student User
        student_user = cls.db.query(User).filter(User.id == "student-1DA23AI001").first()
        if not student_user:
            student_user = User(
                id="student-1DA23AI001",
                email="1da23ai001@vista.local",
                name="Test Student",
                role="student",
                is_active=True,
                password_hash="pw",
                created_at="2026-08-01T00:00:00Z",
            )
            cls.db.add(student_user)

        # Class Section
        cs = cls.db.query(ClassSection).filter(ClassSection.id == "class-aiml-4a").first()
        if not cs:
            cs = ClassSection(
                id="class-aiml-4a",
                department_id="dept-aiml",
                name="4th Year AIML",
                code="AIML-4A",
                semester="7",
                is_active=True,
                created_at="2026-08-01T00:00:00Z",
            )
            cls.db.add(cs)

        # Subject
        subj = cls.db.query(Subject).filter(Subject.id == "subject-22aiu701").first()
        if not subj:
            subj = Subject(
                id="subject-22aiu701",
                department_id="dept-aiml",
                name="Deep Learning",
                code="22AIU701",
                credits=4.0,
                is_active=True,
            )
            cls.db.add(subj)

        # Teacher Subject Assignment
        tsa = cls.db.query(TeacherSubjectAssignment).filter(
            TeacherSubjectAssignment.teacher_id == "t1-scope",
            TeacherSubjectAssignment.subject_id == "subject-22aiu701",
        ).first()
        if not tsa:
            cls.db.add(TeacherSubjectAssignment(
                id="tsa-test-t1",
                teacher_id="t1-scope",
                subject_id="subject-22aiu701",
                class_section_id="class-aiml-4a",
                is_active=True,
                assigned_at="2026-08-01T00:00:00Z",
            ))

        cls.db.commit()

        # Tokens
        cls.admin_token = _make_jwt("admin-test-scope", "admin")
        cls.t1_token = _make_jwt("t1-scope", "teacher")
        cls.t2_token = _make_jwt("t2-scope", "teacher")
        cls.student_token = _make_jwt("student-1DA23AI001", "student")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_get_class_timetable_authorized(self):
        """Admin and Teacher can view any class timetable."""
        res_admin = self.client.get(
            "/api/v1/timetable/class/class-aiml-4a",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn("slots", res_admin.json())
        self.assertEqual(res_admin.json()["class_code"], "AIML-4A")

        res_teacher = self.client.get(
            "/api/v1/timetable/class/class-aiml-4a",
            headers={"Authorization": f"Bearer {self.t1_token}"},
        )
        self.assertEqual(res_teacher.status_code, 200)
        self.assertIn("slots", res_teacher.json())

    def test_02_get_class_timetable_not_found(self):
        """Non-existent class returns 404."""
        res = self.client.get(
            "/api/v1/timetable/class/non-existent-class-xyz",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(res.status_code, 404)

    def test_03_teacher_can_edit_own_slot(self):
        """Teacher can edit their own assigned slot (e.g. room change)."""
        # Create a non-conflicting slot for Teacher 1 on day 5 (Saturday)
        slot = TimetableSlot(
            id="slot-test-t1-edit",
            class_section_id="class-aiml-4a",
            subject_id="subject-22aiu701",
            teacher_id="t1-scope",
            day_of_week=6,  # Sunday — no seeded slots exist on day 6
            start_time="09:00",
            end_time="10:00",
            room="Room-101",
            period_label="S1",
            slot_type="teaching",
            is_active=True,
            created_at="2026-08-01T00:00:00Z",
        )
        self.db.merge(slot)
        self.db.commit()

        # Teacher 1 edits their own slot
        update_payload = {"room": "Advanced-AI-Lab"}
        res = self.client.put(
            f"/api/v1/timetable/slots/{slot.id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.t1_token}"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["room"], "Advanced-AI-Lab")

    def test_04_teacher_cannot_edit_other_teacher_slot(self):
        """Teacher 2 cannot modify Teacher 1's slot (403 Forbidden)."""
        update_payload = {"room": "Hacked-Room"}
        res = self.client.put(
            "/api/v1/timetable/slots/slot-test-t1-edit",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.t2_token}"},
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Teachers can only modify their own assigned timetable slots", res.json()["detail"])

    def test_05_student_cannot_edit_slots(self):
        """Student cannot modify or delete timetable slots (403 Forbidden)."""
        res_put = self.client.put(
            "/api/v1/timetable/slots/slot-test-t1-edit",
            json={"room": "Student-Room"},
            headers={"Authorization": f"Bearer {self.student_token}"},
        )
        self.assertEqual(res_put.status_code, 403)

        res_del = self.client.delete(
            "/api/v1/timetable/slots/slot-test-t1-edit",
            headers={"Authorization": f"Bearer {self.student_token}"},
        )
        self.assertEqual(res_del.status_code, 403)

    def test_06_admin_can_edit_any_slot(self):
        """Admin has full permission to edit any slot."""
        update_payload = {"room": "Auditorium-A"}
        res = self.client.put(
            "/api/v1/timetable/slots/slot-test-t1-edit",
            json=update_payload,
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["room"], "Auditorium-A")

if __name__ == "__main__":
    unittest.main()
