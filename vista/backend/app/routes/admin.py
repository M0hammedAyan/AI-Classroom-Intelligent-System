"""
Admin & Organization Management API
====================================
- Create/manage users with roles
- Create schools, departments, class sections
- Assign mentors to students
- Assign teachers to subjects
- Handle access requests (approve/reject)
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.organization import (
    AccessRequest, ClassSection, Department, MentorAssignment,
    School, Subject, TeacherSubjectAssignment,
)
from ..models.student import Student
from ..models.user import User
from ..permissions import can_approve_requests, get_user_permissions, has_permission
from ..routes.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------------

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str               # admin | hos | hop | mentor | teacher
    school_id: str | None = None
    department_id: str | None = None
    custom_permissions: list[str] | None = None


@router.post("/users")
def create_user(
    body: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new user with role-based creation rules:
    - Admin: can create ANY user (HOS, HOP, Mentor, Teacher)
    - HOS: can create HOP, Mentor, Teacher (within their school)
    - HOP: can create Mentor, Teacher (within their department)
    - Mentor/Teacher: CANNOT create users
    """
    # Who can create whom
    creation_rules = {
        "admin": ["admin", "hos", "hop", "mentor", "teacher"],
        "hos": ["hop", "mentor", "teacher"],
        "hop": ["mentor", "teacher"],
        "mentor": [],
        "teacher": [],
    }

    allowed_roles = creation_rules.get(current_user.role, [])
    if not allowed_roles:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": f"Role '{current_user.role}' cannot create users."})

    if body.role not in allowed_roles:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": f"Your role ({current_user.role}) cannot create '{body.role}' users. Allowed: {allowed_roles}"})

    # Scope enforcement
    if current_user.role == "hos":
        # HOS forces new user into their school
        if body.school_id and body.school_id != current_user.school_id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "HOS can only create users within their own school."})
        body.school_id = body.school_id or current_user.school_id

    if current_user.role == "hop":
        # HOP forces new user into their department + school
        body.school_id = body.school_id or current_user.school_id
        body.department_id = body.department_id or current_user.department_id

    # Validate role
    valid_roles = ["admin", "hos", "hop", "mentor", "teacher"]
    if body.role not in valid_roles:
        raise HTTPException(status_code=400, detail={"code": "INVALID_ROLE", "message": f"Role must be one of: {valid_roles}"})

    # Check email unique
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={"code": "EMAIL_EXISTS", "message": "Email already registered."})

    now = datetime.now(timezone.utc).isoformat()
    pw_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt(rounds=12)).decode()

    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        password_hash=pw_hash,
        role=body.role,
        school_id=body.school_id,
        department_id=body.department_id,
        custom_permissions=json.dumps(body.custom_permissions) if body.custom_permissions else None,
        is_active=True,
        created_at=now,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "school_id": user.school_id,
        "department_id": user.department_id,
        "permissions": get_user_permissions(user),
        "created_by": current_user.name,
    }


@router.get("/users")
def list_users(
    role: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List users. Scoped by role of requester."""
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Insufficient access."})

    query = db.query(User)

    # Scope to school for HOS
    if current_user.role == "hos":
        query = query.filter(User.school_id == current_user.school_id)
    # Scope to department for HOP
    elif current_user.role == "hop":
        query = query.filter(User.department_id == current_user.department_id)

    if role:
        query = query.filter(User.role == role)

    users = query.all()
    return {
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
                "school_id": u.school_id,
                "department_id": u.department_id,
                "is_active": u.is_active,
                "permissions": get_user_permissions(u),
            }
            for u in users
        ],
        "total": len(users),
    }


@router.patch("/users/{user_id}/permissions")
def update_permissions(
    user_id: str,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update custom permissions for a user. Admin/HOS only."""
    if current_user.role not in ("admin", "hos"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only admin/HOS can modify permissions."})

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "User not found."})

    permissions = body.get("permissions", [])
    user.custom_permissions = json.dumps(permissions)
    db.commit()

    return {"user_id": user_id, "permissions": get_user_permissions(user)}


# ---------------------------------------------------------------------------
# School & Department Management
# ---------------------------------------------------------------------------

class CreateSchoolRequest(BaseModel):
    name: str
    code: str


@router.post("/schools")
def create_school(
    body: CreateSchoolRequest,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Create a new school. Admin only."""
    now = datetime.now(timezone.utc).isoformat()
    school = School(
        id=f"school-{body.code.lower()}",
        name=body.name,
        code=body.code.upper(),
        is_active=True,
        created_at=now,
    )
    db.add(school)
    db.commit()
    return {"id": school.id, "name": school.name, "code": school.code}


@router.get("/schools")
def list_schools(
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    schools = db.query(School).filter(School.is_active == True).all()
    return {"schools": [{"id": s.id, "name": s.name, "code": s.code} for s in schools]}


class CreateDepartmentRequest(BaseModel):
    school_id: str
    name: str
    code: str


@router.post("/departments")
def create_department(
    body: CreateDepartmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a department. Admin or HOS of the school."""
    if current_user.role == "hos" and current_user.school_id != body.school_id:
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Cannot create department in another school."})
    if current_user.role not in ("admin", "hos"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only admin/HOS can create departments."})

    now = datetime.now(timezone.utc).isoformat()
    dept = Department(
        id=f"dept-{body.code.lower()}",
        school_id=body.school_id,
        name=body.name,
        code=body.code.upper(),
        is_active=True,
        created_at=now,
    )
    db.add(dept)
    db.commit()
    return {"id": dept.id, "name": dept.name, "code": dept.code, "school_id": dept.school_id}


@router.get("/departments")
def list_departments(
    school_id: str | None = None,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    query = db.query(Department).filter(Department.is_active == True)
    if school_id:
        query = query.filter(Department.school_id == school_id)
    depts = query.all()
    return {"departments": [{"id": d.id, "name": d.name, "code": d.code, "school_id": d.school_id} for d in depts]}


# ---------------------------------------------------------------------------
# Mentor & Teacher Assignments
# ---------------------------------------------------------------------------

class AssignMentorRequest(BaseModel):
    mentor_id: str
    student_ids: list[str]


@router.post("/assign-mentor")
def assign_mentor(
    body: AssignMentorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign students to a mentor. HOP/HOS/Admin can do this."""
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only admin/HOS/HOP can assign mentors."})

    mentor = db.query(User).filter(User.id == body.mentor_id, User.role == "mentor").first()
    if not mentor:
        raise HTTPException(status_code=404, detail={"code": "MENTOR_NOT_FOUND", "message": "Mentor not found or user is not a mentor."})

    now = datetime.now(timezone.utc).isoformat()
    assigned = 0
    for sid in body.student_ids:
        student = db.query(Student).filter(Student.student_id == sid).first()
        if not student:
            continue
        # Check if already assigned
        existing = db.query(MentorAssignment).filter(
            MentorAssignment.mentor_id == body.mentor_id,
            MentorAssignment.student_id == sid,
            MentorAssignment.is_active == True,
        ).first()
        if existing:
            continue
        db.add(MentorAssignment(
            id=str(uuid.uuid4()),
            mentor_id=body.mentor_id,
            student_id=sid,
            assigned_at=now,
            is_active=True,
        ))
        assigned += 1

    db.commit()
    return {"assigned": assigned, "mentor_id": body.mentor_id}


class AssignTeacherRequest(BaseModel):
    teacher_id: str
    subject_id: str
    class_section_id: str


@router.post("/assign-teacher")
def assign_teacher(
    body: AssignTeacherRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign a teacher to a subject+class. HOP/HOS/Admin can do this."""
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only admin/HOS/HOP can assign teachers."})

    now = datetime.now(timezone.utc).isoformat()
    db.add(TeacherSubjectAssignment(
        id=str(uuid.uuid4()),
        teacher_id=body.teacher_id,
        subject_id=body.subject_id,
        class_section_id=body.class_section_id,
        assigned_at=now,
        is_active=True,
    ))
    db.commit()
    return {"assigned": True, "teacher_id": body.teacher_id, "subject_id": body.subject_id}


# ---------------------------------------------------------------------------
# Access Requests (teacher/mentor → HOP/HOS approval)
# ---------------------------------------------------------------------------

class CreateAccessRequest(BaseModel):
    request_type: str       # "mentor_students" | "subject_class"
    target_details: dict    # {student_ids: [...]} or {class_id, subject_id}


@router.post("/access-requests")
def create_access_request(
    body: CreateAccessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an access request (mentor or teacher requesting access)."""
    if current_user.role not in ("mentor", "teacher"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_REQUEST", "message": "Only mentors/teachers submit access requests."})

    now = datetime.now(timezone.utc).isoformat()
    req = AccessRequest(
        id=str(uuid.uuid4()),
        requester_id=current_user.id,
        request_type=body.request_type,
        target_details=json.dumps(body.target_details),
        status="pending",
        created_at=now,
    )
    db.add(req)
    db.commit()
    return {"request_id": req.id, "status": "pending"}


@router.get("/access-requests")
def list_access_requests(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List access requests. HOP/HOS/Admin see pending requests."""
    if not can_approve_requests(current_user):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Cannot view access requests."})

    query = db.query(AccessRequest)
    if status:
        query = query.filter(AccessRequest.status == status)
    requests = query.order_by(AccessRequest.created_at.desc()).all()

    return {
        "requests": [
            {
                "id": r.id,
                "requester_id": r.requester_id,
                "request_type": r.request_type,
                "target_details": json.loads(r.target_details) if r.target_details else {},
                "status": r.status,
                "reviewed_by": r.reviewed_by,
                "created_at": r.created_at,
            }
            for r in requests
        ],
    }


class ReviewRequest(BaseModel):
    action: str         # "approve" | "reject"
    note: str | None = None


@router.patch("/access-requests/{request_id}")
def review_access_request(
    request_id: str,
    body: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject an access request."""
    if not can_approve_requests(current_user):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Cannot review requests."})

    req = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Request not found."})

    if body.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail={"code": "INVALID_ACTION", "message": "Action must be 'approve' or 'reject'."})

    now = datetime.now(timezone.utc).isoformat()
    req.status = "approved" if body.action == "approve" else "rejected"
    req.reviewed_by = current_user.id
    req.review_note = body.note
    req.reviewed_at = now

    # If approved, execute the assignment
    if body.action == "approve":
        details = json.loads(req.target_details) if req.target_details else {}

        if req.request_type == "mentor_students":
            for sid in details.get("student_ids", []):
                db.add(MentorAssignment(
                    id=str(uuid.uuid4()),
                    mentor_id=req.requester_id,
                    student_id=sid,
                    assigned_at=now,
                    is_active=True,
                ))

        elif req.request_type == "subject_class":
            db.add(TeacherSubjectAssignment(
                id=str(uuid.uuid4()),
                teacher_id=req.requester_id,
                subject_id=details.get("subject_id", ""),
                class_section_id=details.get("class_id", ""),
                assigned_at=now,
                is_active=True,
            ))

    db.commit()
    return {"request_id": request_id, "status": req.status}


# ---------------------------------------------------------------------------
# Mentor Dashboard — View assigned students with subjects & teachers
# ---------------------------------------------------------------------------

@router.get("/mentor/my-students")
def mentor_get_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mentor view: all assigned students with their subjects and teacher names.
    """
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only mentors can access this."})

    # Get assigned students
    assignments = (
        db.query(MentorAssignment)
        .filter(MentorAssignment.mentor_id == current_user.id, MentorAssignment.is_active == True)
        .all()
    )

    result = []
    for assignment in assignments:
        student = db.query(Student).filter(Student.student_id == assignment.student_id).first()
        if not student:
            continue

        # Get subjects and teachers for this student's class
        # Find teacher-subject assignments for the student's classroom
        teacher_subs = (
            db.query(TeacherSubjectAssignment)
            .filter(TeacherSubjectAssignment.is_active == True)
            .all()
        )

        subjects_info = []
        for ts in teacher_subs:
            subject = db.query(Subject).filter(Subject.id == ts.subject_id).first()
            teacher = db.query(User).filter(User.id == ts.teacher_id).first()
            if subject and teacher:
                subjects_info.append({
                    "subject_name": subject.name,
                    "subject_code": subject.code,
                    "teacher_name": teacher.name,
                    "teacher_email": teacher.email,
                })

        result.append({
            "student_id": student.student_id,
            "student_name": student.name,
            "class": student.class_,
            "is_active": student.is_active,
            "subjects": subjects_info,
            "assigned_at": assignment.assigned_at,
        })

    return {"students": result, "total": len(result), "mentor": current_user.name}


# ---------------------------------------------------------------------------
# Teacher — Create subject groups & manage their students
# ---------------------------------------------------------------------------

class CreateSubjectGroupRequest(BaseModel):
    subject_name: str
    subject_code: str
    class_section_id: str
    department_id: str


@router.post("/teacher/create-subject-group")
def teacher_create_subject_group(
    body: CreateSubjectGroupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Teacher creates a new subject group and gets assigned to it.
    This allows teachers to set up their own subject-class mappings.
    """
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only teachers can create subject groups."})

    now = datetime.now(timezone.utc).isoformat()

    # Create subject if it doesn't exist
    existing_subject = db.query(Subject).filter(Subject.code == body.subject_code).first()
    if existing_subject:
        subject = existing_subject
    else:
        subject = Subject(
            id=f"sub-{body.subject_code.lower()}",
            department_id=body.department_id,
            name=body.subject_name,
            code=body.subject_code.upper(),
            created_at=now,
        )
        db.add(subject)
        db.flush()

    # Assign teacher to this subject + class
    existing_assign = (
        db.query(TeacherSubjectAssignment)
        .filter(
            TeacherSubjectAssignment.teacher_id == current_user.id,
            TeacherSubjectAssignment.subject_id == subject.id,
            TeacherSubjectAssignment.class_section_id == body.class_section_id,
        )
        .first()
    )

    if not existing_assign:
        db.add(TeacherSubjectAssignment(
            id=str(uuid.uuid4()),
            teacher_id=current_user.id,
            subject_id=subject.id,
            class_section_id=body.class_section_id,
            assigned_at=now,
            is_active=True,
        ))

    db.commit()

    return {
        "subject_id": subject.id,
        "subject_name": subject.name,
        "subject_code": subject.code,
        "class_section_id": body.class_section_id,
        "teacher": current_user.name,
        "status": "created" if not existing_subject else "already_exists_assigned",
    }


@router.get("/teacher/my-subjects")
def teacher_get_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Teacher view: all subjects they teach with class info and student list."""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Only teachers can access this."})

    assignments = (
        db.query(TeacherSubjectAssignment)
        .filter(TeacherSubjectAssignment.teacher_id == current_user.id, TeacherSubjectAssignment.is_active == True)
        .all()
    )

    result = []
    for assign in assignments:
        subject = db.query(Subject).filter(Subject.id == assign.subject_id).first()
        class_section = db.query(ClassSection).filter(ClassSection.id == assign.class_section_id).first()

        # Get students in this class section
        students = []
        if class_section:
            # Match students by class code (classroom_id matches class_section code)
            student_rows = (
                db.query(Student)
                .filter(Student.classroom_id == class_section.code, Student.is_active == True)
                .all()
            )
            students = [{"student_id": s.student_id, "name": s.name} for s in student_rows]

        result.append({
            "subject_name": subject.name if subject else "Unknown",
            "subject_code": subject.code if subject else "?",
            "class_section": class_section.name if class_section else "Unknown",
            "class_code": class_section.code if class_section else "?",
            "students": students,
            "student_count": len(students),
        })

    return {"subjects": result, "total": len(result), "teacher": current_user.name}
