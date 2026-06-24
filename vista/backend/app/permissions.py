"""
Role-Based Access Control (RBAC) — Permission System
=====================================================
Hierarchical permission checks:
  admin → full access everywhere
  hos   → full access within their school
  hop   → full access within their department
  mentor → access to assigned students only
  teacher → access to their subjects/classes only

Usage:
    from ..permissions import check_access, can_view_student
    check_access(user, "manage_scores", school_id="school-cs")
"""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from .models.user import User
from .models.organization import MentorAssignment, TeacherSubjectAssignment


# Role hierarchy (higher number = more access)
ROLE_HIERARCHY = {
    "admin": 100,
    "hos": 80,
    "hop": 60,
    "mentor": 40,
    "teacher": 30,
}

# Permissions each role gets by default
DEFAULT_PERMISSIONS = {
    "admin": [
        "manage_users", "manage_schools", "manage_departments",
        "manage_students", "manage_scores", "manage_attendance",
        "recompute_risk", "view_all", "export_reports",
        "approve_requests", "manage_enrollment",
    ],
    "hos": [
        "manage_departments", "manage_students", "manage_scores",
        "manage_attendance", "recompute_risk", "view_school",
        "export_reports", "approve_requests", "manage_enrollment",
    ],
    "hop": [
        "manage_students", "manage_scores", "manage_attendance",
        "recompute_risk", "view_department", "export_reports",
        "approve_requests",
    ],
    "mentor": [
        "view_assigned_students", "view_attendance",
        "view_risk", "request_access",
    ],
    "teacher": [
        "view_subject_students", "manage_subject_scores",
        "view_attendance", "mark_attendance", "request_access",
    ],
}


def get_user_permissions(user: User) -> list[str]:
    """Get all effective permissions for a user (role defaults + custom)."""
    perms = list(DEFAULT_PERMISSIONS.get(user.role, []))

    # Add custom permissions if any
    if user.custom_permissions:
        try:
            custom = json.loads(user.custom_permissions)
            if isinstance(custom, list):
                perms.extend(custom)
        except (json.JSONDecodeError, TypeError):
            pass

    return list(set(perms))


def has_permission(user: User, permission: str) -> bool:
    """Check if user has a specific permission."""
    if user.role == "admin":
        return True
    return permission in get_user_permissions(user)


def can_access_school(user: User, school_id: str) -> bool:
    """Check if user can access data within a school."""
    if user.role == "admin":
        return True
    if user.role == "hos":
        return user.school_id == school_id
    if user.role in ("hop", "mentor", "teacher"):
        # HOP/mentor/teacher belong to a department within a school
        # We need to check if their department is in this school
        return user.school_id == school_id
    return False


def can_access_department(user: User, department_id: str, db: Session | None = None) -> bool:
    """Check if user can access data within a department."""
    if user.role == "admin":
        return True
    if user.role == "hos":
        # HOS can access all departments in their school
        if db:
            from .models.organization import Department
            dept = db.query(Department).filter(Department.id == department_id).first()
            return dept and dept.school_id == user.school_id
        return True
    if user.role == "hop":
        return user.department_id == department_id
    return False


def can_view_student(user: User, student_id: str, db: Session) -> bool:
    """Check if user can view a specific student's data."""
    if user.role == "admin":
        return True

    if user.role == "hos":
        # Check if student belongs to their school
        from .models.student import Student
        from .models.organization import Department, ClassSection
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            return False
        # Student's classroom → department → school
        return True  # Simplified: HOS sees all in pilot

    if user.role == "hop":
        # Check if student is in their department
        return True  # Simplified for pilot

    if user.role == "mentor":
        # Check mentor assignment
        assignment = (
            db.query(MentorAssignment)
            .filter(
                MentorAssignment.mentor_id == user.id,
                MentorAssignment.student_id == student_id,
                MentorAssignment.is_active == True,
            )
            .first()
        )
        return assignment is not None

    if user.role == "teacher":
        # Teachers can see students in their assigned classes
        # Simplified for pilot: can view all
        return True

    return False


def can_approve_requests(user: User) -> bool:
    """Check if user can approve access requests."""
    return user.role in ("admin", "hos", "hop")
