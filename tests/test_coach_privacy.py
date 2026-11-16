"""
Test Chatbot Privacy and Cross-User Isolation
Proves that a student's coach chat history is never visible to another user.
"""
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from vista.backend.app.main import app
from vista.backend.app.db import SessionLocal
from vista.backend.app.models.user import User
from vista.backend.app.models.student import Student
from vista.backend.app.models.chat import ChatMessage
from vista.backend.app.routes.auth import _make_jwt


class TestCoachPrivacy(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.client = TestClient(app)

    def tearDown(self):
        self.db.close()

    def test_coach_history_cross_user_isolation(self):
        """
        Verify that:
        1. Student A can only view Student A's messages.
        2. Student B can only view Student B's messages.
        3. Student A cannot query Student B's messages by query/path params.
        """
        now = datetime.now(timezone.utc).isoformat()

        user_a = User(
            id="student-STU-ALPHA",
            email="alpha@vista.local",
            name="Student Alpha",
            role="student",
            password_hash="mock_hash",
            is_active=True,
            created_at=now,
        )
        student_a = Student(
            student_id="STU-ALPHA",
            name="Student Alpha",
            usn="1DA23AI098",
            class_="AIML-4A",
            classroom_id="class-aiml-4a",
            is_active=True,
            created_at=now,
        )

        user_b = User(
            id="student-STU-BETA",
            email="beta@vista.local",
            name="Student Beta",
            role="student",
            password_hash="mock_hash",
            is_active=True,
            created_at=now,
        )
        student_b = Student(
            student_id="STU-BETA",
            name="Student Beta",
            usn="1DA23AI099",
            class_="AIML-4A",
            classroom_id="class-aiml-4a",
            is_active=True,
            created_at=now,
        )

        self.db.merge(user_a)
        self.db.merge(student_a)
        self.db.merge(user_b)
        self.db.merge(student_b)
        self.db.commit()

        # Seed distinct chat messages for each student
        msg_a = ChatMessage(
            id="msg-a-001",
            student_id="STU-ALPHA",
            role="user",
            content="Secret message from Alpha about grades",
            created_at=now,
        )
        msg_b = ChatMessage(
            id="msg-b-001",
            student_id="STU-BETA",
            role="user",
            content="Confidential message from Beta about medical leave",
            created_at=now,
        )
        self.db.merge(msg_a)
        self.db.merge(msg_b)
        self.db.commit()

        token_a = _make_jwt(user_a.id, user_a.role)
        token_b = _make_jwt(user_b.id, user_b.role)

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Student A requests history
        res_a = self.client.get("/api/v1/coach/history", headers=headers_a)
        self.assertEqual(res_a.status_code, 200, res_a.text)
        messages_a = res_a.json().get("messages", [])
        contents_a = [m["content"] for m in messages_a]
        self.assertIn("Secret message from Alpha about grades", contents_a)
        self.assertNotIn("Confidential message from Beta about medical leave", contents_a)

        # Student B requests history
        res_b = self.client.get("/api/v1/coach/history", headers=headers_b)
        self.assertEqual(res_b.status_code, 200, res_b.text)
        messages_b = res_b.json().get("messages", [])
        contents_b = [m["content"] for m in messages_b]
        self.assertIn("Confidential message from Beta about medical leave", contents_b)
        self.assertNotIn("Secret message from Alpha about grades", contents_b)

        # Student A attempts to pass Student B's ID via query param
        res_a_spoof = self.client.get("/api/v1/coach/history?student_id=STU-BETA", headers=headers_a)
        self.assertEqual(res_a_spoof.status_code, 200)
        contents_spoof = [m["content"] for m in res_a_spoof.json().get("messages", [])]
        # Still only sees Alpha's messages, never Beta's
        self.assertNotIn("Confidential message from Beta about medical leave", contents_spoof)
        self.assertIn("Secret message from Alpha about grades", contents_spoof)
