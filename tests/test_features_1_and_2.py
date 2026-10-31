"""
Integration & Unit Test Suite for VISTA:
- Feature 1: Role-Scoped Notifications
- Feature 2: AI Study Coach & CIE Rules Engine
- Change 1: 3-Role Deprecation Rejection
"""

import json
import os
import sys
import unittest
from datetime import datetime, timezone

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
from app.models.notification import Notification, NotificationRead
from app.models.chat import ChatMessage
from app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
from app.cie_policy import evaluate_cie, calculate_cie2_needed_to_avoid_cie3, CIE_MAX, CIE_ELIGIBILITY_AVG
from app.routes.notifications import (
    create_notification,
    list_notifications,
    get_unread_count,
    mark_read,
    mark_all_read,
    delete_notification,
    CreateNotificationRequest,
)
from app.routes.lms import add_score
from app.routes.coach import coach_chat, get_chat_history, clear_chat_history, get_coach_summary, ChatRequest
from app.routes.auth import login, LoginRequest
from app.routes.admin import create_user, CreateUserRequest
from fastapi import HTTPException


class TestRoleScopedNotifications(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.admin = self.db.query(User).filter(User.role == "admin").first()
        self.teacher_rajeshwari = self.db.query(User).filter(User.email == "rajeshwari@vista.local").first()
        self.student_ayyan = self.db.query(User).filter(User.id == "student-1DA24AI403").first()
        self.created_notif_ids = []

    def tearDown(self):
        if self.created_notif_ids:
            self.db.query(NotificationRead).filter(NotificationRead.notification_id.in_(self.created_notif_ids)).delete(synchronize_session=False)
            self.db.query(Notification).filter(Notification.id.in_(self.created_notif_ids)).delete(synchronize_session=False)
            self.db.commit()
        self.db.close()

    def test_admin_broadcast_visible_to_all(self):
        """Admin notification with audience='all' is visible to teacher and student."""
        body = CreateNotificationRequest(
            title="Campus Holiday Announcement",
            body="College will remain closed tomorrow.",
            audience_type="all",
            priority="important",
        )
        notif = create_notification(body=body, db=self.db, current_user=self.admin)
        self.created_notif_ids.append(notif["id"])

        # Check teacher visibility
        teacher_view = list_notifications(page=1, page_size=20, db=self.db, current_user=self.teacher_rajeshwari)
        teacher_ids = [n["id"] for n in teacher_view["notifications"]]
        self.assertIn(notif["id"], teacher_ids, "Admin broadcast must be visible to teacher")

        # Check student visibility
        student_view = list_notifications(page=1, page_size=20, db=self.db, current_user=self.student_ayyan)
        student_ids = [n["id"] for n in student_view["notifications"]]
        self.assertIn(notif["id"], student_ids, "Admin broadcast must be visible to student")

    def test_teacher_subject_notification_visibility(self):
        """Teacher notification for an assigned subject is visible to students in that subject."""
        # Mrs. Rajeshwari teaches Deep Learning (subj-dl / 22AIU701)
        body = CreateNotificationRequest(
            title="DL Lab Submission",
            body="Submit notebook by Friday.",
            audience_type="subject",
            subject_id="22AIU701",
            priority="normal",
        )
        notif = create_notification(body=body, db=self.db, current_user=self.teacher_rajeshwari)
        self.created_notif_ids.append(notif["id"])

        # Student Ayyan is in 4th Year AIML taking 22AIU701
        student_view = list_notifications(page=1, page_size=20, db=self.db, current_user=self.student_ayyan)
        student_ids = [n["id"] for n in student_view["notifications"]]
        self.assertIn(notif["id"], student_ids, "Student in DL must see DL notification")

    def test_teacher_unassigned_subject_rejected(self):
        """Teacher cannot send notifications for a subject they do not teach."""
        body = CreateNotificationRequest(
            title="Unauthorized announcement",
            body="Fake message",
            audience_type="subject",
            subject_id="subj-fake-999",
        )
        with self.assertRaises(HTTPException) as ctx:
            create_notification(body=body, db=self.db, current_user=self.teacher_rajeshwari)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_student_cannot_send_notification(self):
        """Student role is strictly forbidden from creating notifications."""
        body = CreateNotificationRequest(
            title="Student announcement",
            body="Should fail",
            audience_type="all",
        )
        with self.assertRaises(HTTPException) as ctx:
            create_notification(body=body, db=self.db, current_user=self.student_ayyan)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_read_tracking_and_unread_count(self):
        """Mark as read updates unread counter accurately."""
        body = CreateNotificationRequest(
            title="Read Counter Test",
            body="Checking read state.",
            audience_type="all",
        )
        notif = create_notification(body=body, db=self.db, current_user=self.admin)
        self.created_notif_ids.append(notif["id"])

        initial_count = get_unread_count(db=self.db, current_user=self.student_ayyan)["unread_count"]
        self.assertGreaterEqual(initial_count, 1)

        # Mark this notification as read
        mark_read(notification_id=notif["id"], db=self.db, current_user=self.student_ayyan)
        after_count = get_unread_count(db=self.db, current_user=self.student_ayyan)["unread_count"]
        self.assertEqual(after_count, initial_count - 1)

    def test_xss_sanitization(self):
        """HTML script tags in notification title and body are stripped."""
        body = CreateNotificationRequest(
            title="<script>alert('hack')</script>Clean Title",
            body="Hello <img src=x onerror=alert(1)>World!",
            audience_type="all",
        )
        notif = create_notification(body=body, db=self.db, current_user=self.admin)
        self.created_notif_ids.append(notif["id"])

        self.assertNotIn("<script>", notif["title"])
        self.assertNotIn("onerror", notif["body"])


class TestCIEPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_cie_policy_both_above_20(self):
        """Both CIE 1 and CIE 2 >= 20.0 average -> NOT eligible for CIE 3, final is average of 1 & 2."""
        scores = [
            {"assessment_type": "CIE 1", "score": 21.0, "status": "scored"},
            {"assessment_type": "CIE 2", "score": 23.0, "status": "scored"},
        ]
        res = evaluate_cie(scores_records=scores)
        self.assertFalse(res["cie3_eligible"])
        self.assertEqual(res["average_cie1_cie2"], 22.0)
        self.assertEqual(res["final_out_of_25"], 22.0)
        self.assertEqual(res["final_out_of_50"], 44.0)

    def test_cie_policy_average_below_20(self):
        """Both CIE 1 and 2 taken, average < 20.0 -> eligible for CIE 3."""
        scores = [
            {"assessment_type": "CIE 1", "score": 17.0, "status": "scored"},
            {"assessment_type": "CIE 2", "score": 18.0, "status": "scored"},
        ]
        res = evaluate_cie(scores_records=scores)
        self.assertTrue(res["cie3_eligible"])
        self.assertEqual(res["average_cie1_cie2"], 17.5)
        self.assertEqual(res["final_out_of_25"], 17.5)

    def test_cie_policy_absent_never_zero(self):
        """Single absent test must never count as 0; score is single test, eligible for CIE 3."""
        scores = [
            {"assessment_type": "CIE 1", "score": 22.0, "status": "scored"},
            {"assessment_type": "CIE 2", "score": None, "status": "absent"},
        ]
        res = evaluate_cie(scores_records=scores)
        self.assertTrue(res["cie3_eligible"])
        self.assertIsNone(res["average_cie1_cie2"], "Average of 1 and 2 is undefined when one was absent")
        self.assertEqual(res["attempted_count"], 1)

    def test_cie_policy_best_two_when_cie3_taken(self):
        """When CIE 3 is taken, final score is best 2 of available scores."""
        scores = [
            {"assessment_type": "CIE 1", "score": 15.0, "status": "scored"},
            {"assessment_type": "CIE 2", "score": 18.0, "status": "scored"},
            {"assessment_type": "CIE 3", "score": 22.0, "status": "scored"},
        ]
        res = evaluate_cie(scores_records=scores)
        # Best 2 are 18.0 and 22.0 -> sum 40.0, avg 20.0
        self.assertEqual(res["best_two"], [22.0, 18.0])
        self.assertEqual(res["final_out_of_25"], 20.0)
        self.assertEqual(res["final_out_of_50"], 40.0)

    def test_cie2_needed_to_avoid_cie3(self):
        """Helper calculate_cie2_needed_to_avoid_cie3 returns correct threshold and flags overflow."""
        # CIE 1 = 18.0 -> needed = 22.0 (reachable)
        calc1 = calculate_cie2_needed_to_avoid_cie3(18.0)
        self.assertEqual(calc1["needed"], 22.0)
        self.assertTrue(calc1["is_reachable"])

        # CIE 1 = 12.0 -> needed = 28.0 (exceeds max of 25.0)
        calc2 = calculate_cie2_needed_to_avoid_cie3(12.0)
        self.assertEqual(calc2["needed"], 28.0)
        self.assertFalse(calc2["is_reachable"])
        self.assertIn("exceeds maximum", calc2["message"])



class _MockRequest:
    """Minimal HTTP request mock so auth.login() can extract client IP."""
    class _Client:
        host = "127.0.0.1"
    client = _Client()


class TestRoleDeprecation(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_login_rejects_deprecated_roles(self):
        """Users attempting to log in with role hos, hop, or mentor get 403 ROLE_DEPRECATED."""
        dummy = User(
            id="test-mentor-dummy",
            name="Test Mentor",
            email="mentor.dummy@vista.local",
            password_hash="pbkdf2:dummy",
            role="mentor",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(dummy)
        self.db.commit()
        try:
            req = LoginRequest(email="mentor.dummy@vista.local", password="wrongpassword")
            with self.assertRaises(HTTPException) as ctx:
                login(body=req, request=_MockRequest(), db=self.db)
            self.assertEqual(ctx.exception.status_code, 403)
            self.assertEqual(ctx.exception.detail.get("code"), "ROLE_DEPRECATED")
        finally:
            self.db.delete(dummy)
            self.db.commit()

    def test_admin_cannot_create_deprecated_roles(self):
        """Admin cannot create users with role other than admin, teacher, or student."""
        admin = self.db.query(User).filter(User.role == "admin").first()
        req = CreateUserRequest(
            name="New HOS User",
            email="hos.test@vista.local",
            password="Password123!",
            role="hos",
        )
        with self.assertRaises(HTTPException) as ctx:
            create_user(body=req, db=self.db, current_user=admin)
        self.assertEqual(ctx.exception.status_code, 400)


class TestCoachService(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.student_ayyan = self.db.query(User).filter(User.id == "student-1DA24AI403").first()

    def tearDown(self):
        # Clear test chat messages for Ayyan
        self.db.query(ChatMessage).filter(ChatMessage.student_id == "1DA24AI403").delete()
        self.db.commit()
        self.db.close()

    def test_coach_summary_tip(self):
        """GET /coach/summary returns a proactive tip with zero LLM call."""
        res = get_coach_summary(db=self.db, current_user=self.student_ayyan)
        self.assertIn("tip_card", res)
        self.assertIn("facts", res)
        self.assertTrue(len(res["tip_card"]["tip"]) > 0)

    def test_coach_chat_deterministic_fallback(self):
        """Coach chat returns factually grounded reply matching student data."""
        req = ChatRequest(message="What is my risk level?")
        res = coach_chat(body=req, db=self.db, current_user=self.student_ayyan)
        self.assertIn("reply", res)
        self.assertIn("facts", res)
        # Verify facts are grounded — overall_attendance is always present
        self.assertIn("overall_attendance", res["facts"])
        self.assertIsNotNone(res["facts"]["overall_attendance"]["attended"])

    def test_coach_history_persistence_and_clear(self):
        """Chat history is stored and can be cleared by student."""
        req = ChatRequest(message="Can I miss next class?")
        coach_chat(body=req, db=self.db, current_user=self.student_ayyan)

        hist = get_chat_history(limit=10, db=self.db, current_user=self.student_ayyan)
        self.assertGreaterEqual(len(hist["messages"]), 2)  # User message + bot message

        clear_chat_history(db=self.db, current_user=self.student_ayyan)
        hist_after = get_chat_history(limit=10, db=self.db, current_user=self.student_ayyan)
        self.assertEqual(len(hist_after["messages"]), 0)


if __name__ == "__main__":
    unittest.main()
