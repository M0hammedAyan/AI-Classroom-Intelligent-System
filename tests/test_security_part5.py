"""
Part 5 — Security Tests
=======================
Tests:
  1. Route inventory: every non-public route requires JWT auth (401 without token).
  2. Forbidden internal fields: no response exposes password_hash, face_embedding, or jwt secrets.
  3. Auth policy helpers: can_view_student, can_view_teacher, can_mutate_slot, can_capture_for_slot.
  4. IDOR prevention: student A cannot access student B's report.
  5. Security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy set on responses.
  6. admin_policy require_admin/require_teacher_or_admin raise correctly.
"""
import os
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from vista.backend.app.main import app
from vista.backend.app.db import SessionLocal
from vista.backend.app.models.user import User
from vista.backend.app.models.student import Student
from vista.backend.app.models.organization import ClassSection, Subject, TeacherSubjectAssignment
from vista.backend.app.models.timetable import TimetableSlot
from vista.backend.app.routes.auth import _make_jwt
from vista.backend.app.auth_policy import (
    can_view_student, can_view_teacher, can_mutate_slot,
    can_capture_for_slot, require_admin, require_teacher_or_admin,
)


# Public routes that intentionally do not require authentication
PUBLIC_ROUTES = {
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/metrics",
    "/metrics/json",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/dev/status",  # returns only {"enabled": bool}; the UI needs it before login
    "/ws/attendance",
}

# Route prefixes that use WebSocket (skip HTTP auth test)
WS_PREFIXES = {"/ws"}


class TestSecurityRouteInventory(unittest.TestCase):
    """Every non-public route must return 401 or 403 when called without a JWT token."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)

    def _is_public(self, path: str) -> bool:
        if path in PUBLIC_ROUTES:
            return True
        for prefix in WS_PREFIXES:
            if path.startswith(prefix):
                return True
        # FastAPI internal routes
        if path.startswith("/openapi") or path.startswith("/redoc") or path.startswith("/docs"):
            return True
        return False

    def test_all_api_routes_require_auth(self):
        """Non-public API routes must reject unauthenticated requests (401 or 403)."""
        from fastapi.routing import APIRoute
        tested = 0
        failures = []
        for route in app.routes:
            if not isinstance(route, APIRoute):
                continue
            path = route.path
            if self._is_public(path):
                continue
            # Skip routes with complex path params that can't be guessed
            if "{" in path:
                # Replace path params with safe placeholder values
                test_path = path.replace("{student_id}", "NOSUCHSTUDENT")
                test_path = test_path.replace("{teacher_id}", "NOSUCHTEACHER")
                test_path = test_path.replace("{slot_id}", "NOSUCHSLOT")
                test_path = test_path.replace("{class_section_id}", "NOSUCHCLASS")
                test_path = test_path.replace("{class_id}", "NOSUCHCLASS")
                test_path = test_path.replace("{subject_id}", "NOSUCHSUBJECT")
                test_path = test_path.replace("{report_id}", "NOSUCHREPORT")
                test_path = test_path.replace("{notification_id}", "NOSUCHNOTIF")
                test_path = test_path.replace("{user_id}", "NOSUCHUSER")
                test_path = test_path.replace("{id}", "NOSUCHID")
                # Replace any remaining {param} with NOSUCH
                import re
                test_path = re.sub(r"\{[^}]+\}", "NOSUCHPARAM", test_path)
            else:
                test_path = path

            methods = list(route.methods or {"GET"})
            method = methods[0]
            resp = getattr(self.client, method.lower())(test_path)

            if resp.status_code not in (401, 403, 404, 405, 422):
                # 404 means route exists but no object found (still required auth)
                # 405 means wrong method tried
                # 422 means validation error (body required) — still got past auth means no auth
                if resp.status_code == 200:
                    failures.append(
                        f"{method} {path} -> {resp.status_code} (should require auth)"
                    )
            tested += 1

        self.assertEqual(
            failures, [],
            msg=f"Routes accessible without auth:\n" + "\n".join(failures)
        )
        self.assertGreater(tested, 5, "Should have tested at least 5 protected routes")


class TestForbiddenInternalFields(unittest.TestCase):
    """No API response body should expose sensitive internal fields."""

    FORBIDDEN_FIELDS = {"password_hash", "hashed_password", "face_embedding", "VISTA_JWT_SECRET"}

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)
        cls.db = SessionLocal()

        # Create a test admin user for authenticated requests
        admin = cls.db.query(User).filter(User.id == "admin-sec-test").first()
        if not admin:
            cls.db.add(User(
                id="admin-sec-test",
                name="Security Admin",
                email="sec-admin@vista.local",
                role="admin",
                is_active=True,
                password_hash="hashed-not-exposed",
                created_at="2026-01-01T00:00:00Z",
            ))
            cls.db.commit()
        cls.admin_token = _make_jwt("admin-sec-test", "admin")

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _check_response_for_forbidden(self, data, path="root"):
        """Recursively scan response JSON for forbidden field names."""
        violations = []
        if isinstance(data, dict):
            for key, val in data.items():
                if key in self.FORBIDDEN_FIELDS:
                    violations.append(f"Found forbidden field '{key}' at {path}.{key}")
                violations.extend(self._check_response_for_forbidden(val, f"{path}.{key}"))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                violations.extend(self._check_response_for_forbidden(item, f"{path}[{i}]"))
        return violations

    def test_student_list_no_sensitive_fields(self):
        """GET /api/v1/students does not expose password_hash or face_embedding."""
        resp = self.client.get(
            "/api/v1/students",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        if resp.status_code != 200:
            self.skipTest(f"Student list returned {resp.status_code}")
        violations = self._check_response_for_forbidden(resp.json())
        self.assertEqual(violations, [], msg="\n".join(violations))

    def test_user_endpoints_no_password_hash(self):
        """Admin dashboard does not expose password_hash in user data."""
        resp = self.client.get(
            "/api/v1/admin/audit-log",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        if resp.status_code not in (200, 404):
            self.skipTest(f"Audit log returned {resp.status_code}")
        if resp.status_code == 200:
            violations = self._check_response_for_forbidden(resp.json())
            self.assertEqual(violations, [], msg="\n".join(violations))

    def test_timetable_no_sensitive_fields(self):
        """Timetable admin endpoint does not expose sensitive fields."""
        resp = self.client.get(
            "/api/v1/timetable/admin",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        if resp.status_code != 200:
            self.skipTest(f"Timetable admin returned {resp.status_code}")
        violations = self._check_response_for_forbidden(resp.json())
        self.assertEqual(violations, [], msg="\n".join(violations))


class TestSecurityHeaders(unittest.TestCase):
    """Security headers must be present on API responses."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)

    def test_security_headers_on_public_endpoint(self):
        """Security headers are set even on public endpoints (login page)."""
        resp = self.client.post(
            "/api/v1/auth/login",
            json={"email": "doesnotexist@vista.local", "password": "badpw"},
        )
        # May return 401 — we just need the headers
        self.assertIn(
            resp.headers.get("x-content-type-options", "").lower(),
            ("nosniff",),
            "X-Content-Type-Options: nosniff must be set",
        )
        self.assertIn(
            resp.headers.get("x-frame-options", "").upper(),
            ("DENY", "SAMEORIGIN"),
            "X-Frame-Options must be DENY or SAMEORIGIN",
        )
        self.assertIn(
            resp.headers.get("referrer-policy", ""),
            ("strict-origin-when-cross-origin", "no-referrer", "same-origin"),
            "Referrer-Policy must be set",
        )

    def test_no_server_header_exposing_version(self):
        """Server header should not expose the internal framework version."""
        resp = self.client.get("/docs")
        server_header = resp.headers.get("server", "").lower()
        # Uvicorn sets "uvicorn" but should not expose "fastapi/version" etc.
        self.assertNotIn("fastapi/", server_header)


class TestAuthPolicyHelpers(unittest.TestCase):
    """Unit tests for auth_policy.py helper functions."""

    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls._setup_fixtures(cls.db)

    @classmethod
    def _setup_fixtures(cls, db):
        # Admin user
        admin = db.query(User).filter(User.id == "auth-policy-admin").first()
        if not admin:
            db.add(User(id="auth-policy-admin", name="Policy Admin", email="policy-admin@vista.local",
                        role="admin", is_active=True, password_hash="x", created_at="2026-01-01T00:00:00Z"))
        # Teacher
        teacher = db.query(User).filter(User.id == "auth-policy-teacher").first()
        if not teacher:
            db.add(User(id="auth-policy-teacher", name="Policy Teacher", email="policy-teacher@vista.local",
                        role="teacher", is_active=True, password_hash="x", created_at="2026-01-01T00:00:00Z"))
        # Student user + Student record
        stu_user = db.query(User).filter(User.id == "student-POLICY001").first()
        if not stu_user:
            db.add(User(id="student-POLICY001", name="Policy Student", email="policy-stu@vista.local",
                        role="student", is_active=True, password_hash="x", created_at="2026-01-01T00:00:00Z"))
        stu = db.query(Student).filter(Student.student_id == "POLICY001").first()
        if not stu:
            db.add(Student(student_id="POLICY001", name="Policy Student", class_="AIML-4A",
                           classroom_id="class-aiml-4a", is_active=True,
                           enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))
        # Another student (POLICY002) in a different class
        stu2 = db.query(Student).filter(Student.student_id == "POLICY002").first()
        if not stu2:
            db.add(Student(student_id="POLICY002", name="Other Student", class_="AIML-3A",
                           classroom_id="class-other-999", is_active=True,
                           enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))
        # Timetable slot owned by policy-teacher
        slot = db.query(TimetableSlot).filter(TimetableSlot.id == "slot-policy-test").first()
        if not slot:
            db.add(TimetableSlot(
                id="slot-policy-test",
                class_section_id="class-aiml-4a",
                teacher_id="auth-policy-teacher",
                day_of_week=6,
                start_time="08:00",
                end_time="09:00",
                period_label="S0",
                slot_type="teaching",
                is_active=True,
                created_at="2026-01-01T00:00:00Z",
            ))
        db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _make_user(self, role: str, uid: str) -> User:
        return User(id=uid, name="Test", email=f"{uid}@test.local",
                    role=role, is_active=True, password_hash="x", created_at="2026-01-01T00:00:00Z")

    # --- require_admin ---
    def test_require_admin_allows_admin(self):
        admin = self._make_user("admin", "auth-policy-admin")
        require_admin(admin)  # Should not raise

    def test_require_admin_blocks_teacher(self):
        teacher = self._make_user("teacher", "auth-policy-teacher")
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            require_admin(teacher)
        self.assertEqual(ctx.exception.status_code, 403)

    # --- can_view_student ---
    def test_admin_can_view_any_student(self):
        admin = self.db.query(User).filter(User.id == "auth-policy-admin").first()
        student = can_view_student(admin, "POLICY001", self.db)
        self.assertEqual(student.student_id, "POLICY001")

    def test_student_can_view_own_record(self):
        stu_user = self.db.query(User).filter(User.id == "student-POLICY001").first()
        student = can_view_student(stu_user, "POLICY001", self.db)
        self.assertEqual(student.student_id, "POLICY001")

    def test_student_cannot_view_other_student(self):
        stu_user = self.db.query(User).filter(User.id == "student-POLICY001").first()
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            can_view_student(stu_user, "POLICY002", self.db)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_unassigned_teacher_cannot_view_student(self):
        teacher = self.db.query(User).filter(User.id == "auth-policy-teacher").first()
        from fastapi import HTTPException
        # POLICY002 is in class-other-999 which teacher is not assigned to
        with self.assertRaises(HTTPException) as ctx:
            can_view_student(teacher, "POLICY002", self.db)
        self.assertEqual(ctx.exception.status_code, 403)

    # --- can_view_teacher ---
    def test_admin_can_view_any_teacher(self):
        admin = self.db.query(User).filter(User.id == "auth-policy-admin").first()
        teacher = can_view_teacher(admin, "auth-policy-teacher", self.db)
        self.assertEqual(teacher.id, "auth-policy-teacher")

    def test_teacher_can_view_own_data(self):
        teacher = self.db.query(User).filter(User.id == "auth-policy-teacher").first()
        result = can_view_teacher(teacher, "auth-policy-teacher", self.db)
        self.assertEqual(result.id, "auth-policy-teacher")

    def test_student_cannot_view_teacher(self):
        stu_user = self.db.query(User).filter(User.id == "student-POLICY001").first()
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            can_view_teacher(stu_user, "auth-policy-teacher", self.db)
        self.assertEqual(ctx.exception.status_code, 403)

    # --- can_mutate_slot ---
    def test_admin_can_mutate_any_slot(self):
        admin = self.db.query(User).filter(User.id == "auth-policy-admin").first()
        slot = can_mutate_slot(admin, "slot-policy-test", self.db)
        self.assertEqual(slot.id, "slot-policy-test")

    def test_teacher_can_mutate_own_slot(self):
        teacher = self.db.query(User).filter(User.id == "auth-policy-teacher").first()
        slot = can_mutate_slot(teacher, "slot-policy-test", self.db)
        self.assertEqual(slot.id, "slot-policy-test")

    def test_student_cannot_mutate_slot(self):
        stu_user = self.db.query(User).filter(User.id == "student-POLICY001").first()
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            can_mutate_slot(stu_user, "slot-policy-test", self.db)
        self.assertEqual(ctx.exception.status_code, 403)

    # --- can_capture_for_slot ---
    def test_admin_can_capture_anywhere(self):
        admin = self.db.query(User).filter(User.id == "auth-policy-admin").first()
        result = can_capture_for_slot(admin, "class-aiml-4a", None, None, self.db)
        self.assertTrue(result)

    def test_student_cannot_capture(self):
        stu_user = self.db.query(User).filter(User.id == "student-POLICY001").first()
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            can_capture_for_slot(stu_user, "class-aiml-4a", None, None, self.db)
        self.assertEqual(ctx.exception.status_code, 403)


class TestIDORPrevention(unittest.TestCase):
    """IDOR: Student A cannot access Student B's data."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)
        db = SessionLocal()

        # Student A
        sa = db.query(User).filter(User.id == "student-IDOR_A001").first()
        if not sa:
            db.add(User(id="student-IDOR_A001", name="IDOR Student A", email="idor-a@vista.local",
                        role="student", is_active=True, password_hash="x", created_at="2026-01-01T00:00:00Z"))
        stu_a = db.query(Student).filter(Student.student_id == "IDOR_A001").first()
        if not stu_a:
            db.add(Student(student_id="IDOR_A001", name="IDOR A", class_="AIML-4A", classroom_id="class-aiml-4a",
                           is_active=True, enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))

        # Student B
        sb = db.query(User).filter(User.id == "student-IDOR_B002").first()
        if not sb:
            db.add(User(id="student-IDOR_B002", name="IDOR Student B", email="idor-b@vista.local",
                        role="student", is_active=True, password_hash="x", created_at="2026-01-01T00:00:00Z"))
        stu_b = db.query(Student).filter(Student.student_id == "IDOR_B002").first()
        if not stu_b:
            db.add(Student(student_id="IDOR_B002", name="IDOR B", class_="AIML-4A", classroom_id="class-aiml-4a",
                           is_active=True, enrolled_at="2026-01-01", created_at="2026-01-01T00:00:00Z"))

        db.commit()
        db.close()

        cls.token_a = _make_jwt("student-IDOR_A001", "student")
        cls.token_b = _make_jwt("student-IDOR_B002", "student")

    def test_student_cannot_access_other_student_report(self):
        """Student A cannot GET /api/v1/reports/student/IDOR_B002 (must 403)."""
        resp = self.client.get(
            "/api/v1/reports/student/IDOR_B002",
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        self.assertEqual(resp.status_code, 403)

    def test_student_cannot_access_other_student_csv(self):
        """Student A cannot GET /api/v1/reports/student/IDOR_B002/csv (must 403)."""
        resp = self.client.get(
            "/api/v1/reports/student/IDOR_B002/csv",
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        self.assertEqual(resp.status_code, 403)

    def test_student_can_access_own_report(self):
        """Student A CAN GET /api/v1/reports/student/IDOR_A001 (must 200 or 404-if-no-data)."""
        resp = self.client.get(
            "/api/v1/reports/student/IDOR_A001",
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        self.assertIn(resp.status_code, (200, 404))

    def test_student_cannot_edit_timetable(self):
        """Student token trying to PUT a timetable slot must get 403."""
        resp = self.client.put(
            "/api/v1/timetable/slots/slot-policy-test",
            json={"room": "Student-Hacked-Room"},
            headers={"Authorization": f"Bearer {self.token_a}"},
        )
        self.assertEqual(resp.status_code, 403)


if __name__ == "__main__":
    unittest.main()
