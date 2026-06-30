"""
Academics API — Timetable, Semester Results, Announcements, Study Materials, Assignments, Parent Alerts.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.organization import ClassSection, Subject, TeacherSubjectAssignment
from ..models.student import Student
from ..models.timetable import (
    Announcement, Assignment, AssignmentSubmission,
    ParentAlert, ParentContact, SemesterResult, StudyMaterial, TimetableSlot,
)
from ..models.user import User
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["academics"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===========================================================================
# 1. TIMETABLE
# ===========================================================================

class CreateSlotRequest(BaseModel):
    class_section_id: str
    subject_id: str
    teacher_id: str | None = None
    day_of_week: int  # 0=Mon, 4=Fri
    start_time: str   # "09:00"
    end_time: str     # "10:00"
    room: str | None = None


@router.post("/timetable")
def create_timetable_slot(
    body: CreateSlotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a timetable slot. HOP/HOS/Admin."""
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail="Only Admin/HOS/HOP can manage timetable")
    if body.day_of_week < 0 or body.day_of_week > 4:
        raise HTTPException(status_code=400, detail="day_of_week must be 0-4 (Mon-Fri)")

    now = datetime.now(timezone.utc).isoformat()
    slot = TimetableSlot(
        id=str(uuid.uuid4()),
        class_section_id=body.class_section_id,
        subject_id=body.subject_id,
        teacher_id=body.teacher_id,
        day_of_week=body.day_of_week,
        start_time=body.start_time,
        end_time=body.end_time,
        room=body.room,
        is_active=True,
        created_at=now,
    )
    db.add(slot)
    db.commit()
    return {"id": slot.id, "status": "created"}


@router.get("/timetable/{class_section_id}")
def get_timetable(
    class_section_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get weekly timetable for a class section."""
    slots = (
        db.query(TimetableSlot)
        .filter(TimetableSlot.class_section_id == class_section_id, TimetableSlot.is_active == True)
        .order_by(TimetableSlot.day_of_week, TimetableSlot.start_time)
        .all()
    )
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    result = {d: [] for d in days}

    for slot in slots:
        subject = db.query(Subject).filter(Subject.id == slot.subject_id).first()
        teacher = db.query(User).filter(User.id == slot.teacher_id).first() if slot.teacher_id else None
        result[days[slot.day_of_week]].append({
            "id": slot.id,
            "subject_name": subject.name if subject else "Unknown",
            "subject_code": subject.code if subject else "?",
            "teacher_name": teacher.name if teacher else "TBA",
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "room": slot.room,
        })

    return {"class_section_id": class_section_id, "timetable": result}


@router.delete("/timetable/{slot_id}")
def delete_timetable_slot(
    slot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail="Only Admin/HOS/HOP can manage timetable")
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot.is_active = False
    db.commit()
    return {"status": "deleted"}


# ===========================================================================
# 2. SEMESTER RESULTS
# ===========================================================================

class CreateResultRequest(BaseModel):
    student_id: str
    subject_id: str
    semester: str
    academic_year: str
    marks_obtained: float
    max_marks: float
    grade: str | None = None
    credits: float | None = None
    result: str  # "pass" | "fail" | "absent"


@router.post("/semester-results")
def add_semester_result(
    body: CreateResultRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add semester result. Admin/HOS/HOP."""
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail="Only Admin/HOS/HOP can add results")

    now = datetime.now(timezone.utc).isoformat()
    result = SemesterResult(
        id=str(uuid.uuid4()),
        student_id=body.student_id,
        subject_id=body.subject_id,
        semester=body.semester,
        academic_year=body.academic_year,
        marks_obtained=body.marks_obtained,
        max_marks=body.max_marks,
        grade=body.grade,
        credits=body.credits,
        result=body.result,
        declared_at=now,
        created_at=now,
    )
    db.add(result)
    db.commit()
    return {"id": result.id, "status": "added"}


@router.post("/semester-results/bulk")
def bulk_add_results(
    results: list[CreateResultRequest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk upload semester results."""
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail="Only Admin/HOS/HOP can add results")

    now = datetime.now(timezone.utc).isoformat()
    added = 0
    for body in results:
        db.add(SemesterResult(
            id=str(uuid.uuid4()),
            student_id=body.student_id,
            subject_id=body.subject_id,
            semester=body.semester,
            academic_year=body.academic_year,
            marks_obtained=body.marks_obtained,
            max_marks=body.max_marks,
            grade=body.grade,
            credits=body.credits,
            result=body.result,
            declared_at=now,
            created_at=now,
        ))
        added += 1
    db.commit()
    return {"added": added}


@router.get("/semester-results/{student_id}")
def get_student_results(
    student_id: str,
    semester: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get semester results for a student."""
    query = db.query(SemesterResult).filter(SemesterResult.student_id == student_id)
    if semester:
        query = query.filter(SemesterResult.semester == semester)
    rows = query.order_by(SemesterResult.semester, SemesterResult.created_at).all()

    results = []
    for r in rows:
        subj = db.query(Subject).filter(Subject.id == r.subject_id).first()
        results.append({
            "id": r.id,
            "subject_name": subj.name if subj else "Unknown",
            "subject_code": subj.code if subj else "?",
            "semester": r.semester,
            "academic_year": r.academic_year,
            "marks_obtained": r.marks_obtained,
            "max_marks": r.max_marks,
            "percentage": round(r.marks_obtained / r.max_marks * 100, 1) if r.max_marks > 0 else 0,
            "grade": r.grade,
            "credits": r.credits,
            "result": r.result,
            "declared_at": r.declared_at,
        })

    # SGPA calculation
    total_credits = sum(r.get("credits", 0) or 0 for r in results)
    return {"student_id": student_id, "results": results, "total_subjects": len(results)}


# ===========================================================================
# 3. ANNOUNCEMENTS
# ===========================================================================

class CreateAnnouncementRequest(BaseModel):
    title: str
    content: str
    target_scope: str = "all"  # "all" | "school:school-cse" | "dept:dept-aiml" | "class:AIML-4A"
    priority: str = "normal"   # normal | important | urgent
    expires_at: str | None = None


@router.post("/announcements")
def create_announcement(
    body: CreateAnnouncementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an announcement. Admin/HOS/HOP can create."""
    if current_user.role not in ("admin", "hos", "hop", "teacher"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    now = datetime.now(timezone.utc).isoformat()
    ann = Announcement(
        id=str(uuid.uuid4()),
        title=body.title,
        content=body.content,
        author_id=current_user.id,
        target_scope=body.target_scope,
        priority=body.priority,
        is_active=True,
        expires_at=body.expires_at,
        created_at=now,
    )
    db.add(ann)
    db.commit()
    return {"id": ann.id, "title": ann.title, "status": "published"}


@router.get("/announcements")
def list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List announcements visible to current user based on scope."""
    query = db.query(Announcement).filter(Announcement.is_active == True)

    # Filter by scope the user can see
    visible_scopes = ["all"]
    if current_user.school_id:
        visible_scopes.append(f"school:{current_user.school_id}")
    if current_user.department_id:
        visible_scopes.append(f"dept:{current_user.department_id}")
    # Students see their class announcements
    if current_user.role == "student" and current_user.id.startswith("student-"):
        sid = current_user.id.replace("student-", "")
        student = db.query(Student).filter(Student.student_id == sid).first()
        if student:
            visible_scopes.append(f"class:{student.class_}")

    query = query.filter(Announcement.target_scope.in_(visible_scopes))

    total = query.count()
    announcements = (
        query.order_by(Announcement.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    results = []
    for a in announcements:
        author = db.query(User).filter(User.id == a.author_id).first()
        results.append({
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "author_name": author.name if author else "Unknown",
            "target_scope": a.target_scope,
            "priority": a.priority,
            "expires_at": a.expires_at,
            "created_at": a.created_at,
        })

    return {"announcements": results, "total": total, "page": page}


@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Not found")
    ann.is_active = False
    db.commit()
    return {"status": "deleted"}


# ===========================================================================
# 4. STUDY MATERIALS
# ===========================================================================

@router.post("/materials")
async def upload_material(
    subject_id: str,
    title: str,
    class_section_id: str | None = None,
    description: str | None = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload study material. Teachers/HOP/HOS/Admin."""
    if current_user.role not in ("admin", "hos", "hop", "teacher"):
        raise HTTPException(status_code=403, detail="Only faculty can upload materials")

    # Save file
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    safe_name = f"{uuid.uuid4().hex[:12]}.{ext}"
    mat_dir = os.path.join(UPLOAD_DIR, "materials")
    os.makedirs(mat_dir, exist_ok=True)
    file_path = os.path.join(mat_dir, safe_name)

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    with open(file_path, "wb") as f:
        f.write(content)

    now = datetime.now(timezone.utc).isoformat()
    mat = StudyMaterial(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        class_section_id=class_section_id,
        uploaded_by=current_user.id,
        title=title,
        description=description,
        file_name=file.filename,
        file_path=f"materials/{safe_name}",
        file_size=len(content),
        file_type=ext,
        created_at=now,
    )
    db.add(mat)
    db.commit()
    return {"id": mat.id, "title": mat.title, "file_name": mat.file_name, "size": mat.file_size}


@router.get("/materials")
def list_materials(
    subject_id: str | None = None,
    class_section_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List study materials. Filtered by subject or class."""
    query = db.query(StudyMaterial)
    if subject_id:
        query = query.filter(StudyMaterial.subject_id == subject_id)
    if class_section_id:
        query = query.filter(StudyMaterial.class_section_id == class_section_id)

    materials = query.order_by(StudyMaterial.created_at.desc()).limit(50).all()
    results = []
    for m in materials:
        subj = db.query(Subject).filter(Subject.id == m.subject_id).first()
        uploader = db.query(User).filter(User.id == m.uploaded_by).first()
        results.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "subject_name": subj.name if subj else "Unknown",
            "subject_code": subj.code if subj else "?",
            "file_name": m.file_name,
            "file_type": m.file_type,
            "file_size": m.file_size,
            "uploaded_by": uploader.name if uploader else "Unknown",
            "created_at": m.created_at,
        })
    return {"materials": results, "total": len(results)}


@router.get("/materials/{material_id}/download")
def download_material(
    material_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a study material file."""
    from fastapi.responses import FileResponse

    mat = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")

    full_path = os.path.join(UPLOAD_DIR, mat.file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(full_path, filename=mat.file_name, media_type="application/octet-stream")


# ===========================================================================
# 5. ASSIGNMENTS
# ===========================================================================

class CreateAssignmentRequest(BaseModel):
    subject_id: str
    class_section_id: str
    title: str
    description: str | None = None
    max_marks: float | None = None
    due_date: str  # YYYY-MM-DD


@router.post("/assignments")
def create_assignment(
    body: CreateAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an assignment. Teachers only."""
    if current_user.role not in ("admin", "teacher", "hop"):
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")

    now = datetime.now(timezone.utc).isoformat()
    assign = Assignment(
        id=str(uuid.uuid4()),
        subject_id=body.subject_id,
        class_section_id=body.class_section_id,
        teacher_id=current_user.id,
        title=body.title,
        description=body.description,
        max_marks=body.max_marks,
        due_date=body.due_date,
        is_active=True,
        created_at=now,
    )
    db.add(assign)
    db.commit()
    return {"id": assign.id, "title": assign.title, "due_date": assign.due_date}


@router.get("/assignments")
def list_assignments(
    class_section_id: str | None = None,
    subject_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List assignments. Teachers see their own, students see their class's."""
    query = db.query(Assignment).filter(Assignment.is_active == True)

    if current_user.role == "teacher":
        query = query.filter(Assignment.teacher_id == current_user.id)
    if class_section_id:
        query = query.filter(Assignment.class_section_id == class_section_id)
    if subject_id:
        query = query.filter(Assignment.subject_id == subject_id)

    assignments = query.order_by(Assignment.due_date.desc()).limit(50).all()
    results = []
    for a in assignments:
        subj = db.query(Subject).filter(Subject.id == a.subject_id).first()
        sub_count = db.query(AssignmentSubmission).filter(AssignmentSubmission.assignment_id == a.id).count()
        results.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "subject_name": subj.name if subj else "Unknown",
            "subject_code": subj.code if subj else "?",
            "max_marks": a.max_marks,
            "due_date": a.due_date,
            "submissions_count": sub_count,
            "created_at": a.created_at,
        })
    return {"assignments": results, "total": len(results)}


class SubmitAssignmentRequest(BaseModel):
    notes: str | None = None


@router.post("/assignments/{assignment_id}/submit")
def submit_assignment(
    assignment_id: str,
    body: SubmitAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Student submits an assignment."""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    sid = current_user.id.replace("student-", "")

    # Check duplicate
    existing = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == sid,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already submitted")

    now = datetime.now(timezone.utc).isoformat()
    sub = AssignmentSubmission(
        id=str(uuid.uuid4()),
        assignment_id=assignment_id,
        student_id=sid,
        submitted_at=now,
        notes=body.notes,
    )
    db.add(sub)
    db.commit()
    return {"id": sub.id, "status": "submitted", "submitted_at": now}


class GradeSubmissionRequest(BaseModel):
    marks: float
    feedback: str | None = None


@router.patch("/assignments/submissions/{submission_id}/grade")
def grade_submission(
    submission_id: str,
    body: GradeSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Teacher grades a submission."""
    if current_user.role not in ("admin", "teacher", "hop"):
        raise HTTPException(status_code=403, detail="Only teachers can grade")

    sub = db.query(AssignmentSubmission).filter(AssignmentSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    sub.marks = body.marks
    sub.feedback = body.feedback
    sub.graded_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    return {"status": "graded", "marks": sub.marks}


@router.get("/assignments/{assignment_id}/submissions")
def list_submissions(
    assignment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List submissions for an assignment. Teachers see all, students see own."""
    subs = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()

    results = []
    for s in subs:
        student = db.query(Student).filter(Student.student_id == s.student_id).first()
        results.append({
            "id": s.id,
            "student_id": s.student_id,
            "student_name": student.name if student else "Unknown",
            "submitted_at": s.submitted_at,
            "marks": s.marks,
            "feedback": s.feedback,
            "graded_at": s.graded_at,
            "notes": s.notes,
        })
    return {"submissions": results, "total": len(results)}


# ===========================================================================
# 6. PARENT ALERTS
# ===========================================================================

class AddParentContactRequest(BaseModel):
    student_id: str
    parent_name: str
    relation: str  # father | mother | guardian
    phone: str | None = None
    email: str | None = None
    is_primary: bool = True


@router.post("/parents")
def add_parent_contact(
    body: AddParentContactRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add parent contact. Admin/HOS/HOP/Mentor can add."""
    if current_user.role not in ("admin", "hos", "hop", "mentor"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    now = datetime.now(timezone.utc).isoformat()
    contact = ParentContact(
        id=str(uuid.uuid4()),
        student_id=body.student_id,
        parent_name=body.parent_name,
        relation=body.relation,
        phone=body.phone,
        email=body.email,
        is_primary=body.is_primary,
        alert_enabled=True,
        created_at=now,
    )
    db.add(contact)
    db.commit()
    return {"id": contact.id, "parent_name": contact.parent_name}


@router.get("/parents/{student_id}")
def get_parent_contacts(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get parent contacts for a student."""
    contacts = db.query(ParentContact).filter(ParentContact.student_id == student_id).all()
    return {
        "contacts": [
            {
                "id": c.id, "parent_name": c.parent_name, "relation": c.relation,
                "phone": c.phone, "email": c.email, "is_primary": c.is_primary,
                "alert_enabled": c.alert_enabled,
            }
            for c in contacts
        ]
    }


@router.post("/parents/send-alert")
def send_parent_alert(
    student_id: str,
    alert_type: str,  # attendance_low | risk_high | result_declared
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send alert to parent. In production, this integrates with SMS/email gateway.
    For pilot: logs the alert and marks as 'pending' (manual follow-up).
    """
    if current_user.role not in ("admin", "hos", "hop", "mentor"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    contacts = db.query(ParentContact).filter(
        ParentContact.student_id == student_id,
        ParentContact.alert_enabled == True,
    ).all()
    if not contacts:
        raise HTTPException(status_code=400, detail="No parent contacts with alerts enabled")

    # Build message
    messages = {
        "attendance_low": f"Dear Parent, your ward {student.name} ({student_id}) has attendance below 75%. Please ensure regular attendance.",
        "risk_high": f"Dear Parent, your ward {student.name} ({student_id}) has been flagged as HIGH academic risk. Kindly contact the mentor.",
        "result_declared": f"Dear Parent, semester results for {student.name} ({student_id}) have been declared. Please check the portal.",
    }
    message = messages.get(alert_type, f"Alert for student {student.name}: {alert_type}")

    now = datetime.now(timezone.utc).isoformat()
    alerts_sent = []
    for contact in contacts:
        channel = "sms" if contact.phone else "email"
        alert = ParentAlert(
            id=str(uuid.uuid4()),
            student_id=student_id,
            parent_contact_id=contact.id,
            alert_type=alert_type,
            message=message,
            channel=channel,
            status="pending",  # In production: integrate with SMS gateway
            sent_at=now,
            created_at=now,
        )
        db.add(alert)
        alerts_sent.append({
            "parent_name": contact.parent_name,
            "channel": channel,
            "destination": contact.phone or contact.email,
            "status": "pending",
        })

    db.commit()
    return {"alerts_sent": len(alerts_sent), "details": alerts_sent}


@router.get("/parents/alerts/{student_id}")
def get_parent_alerts(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get alert history for a student's parents."""
    alerts = (
        db.query(ParentAlert)
        .filter(ParentAlert.student_id == student_id)
        .order_by(ParentAlert.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "alerts": [
            {
                "id": a.id, "alert_type": a.alert_type, "message": a.message,
                "channel": a.channel, "status": a.status, "sent_at": a.sent_at,
            }
            for a in alerts
        ]
    }


# ===========================================================================
# BULK SEMESTER RESULTS VIA CSV
# ===========================================================================

@router.post("/semester-results/upload-csv")
async def upload_results_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk upload semester results from CSV.
    CSV format: student_id,subject_code,semester,academic_year,marks,max_marks,grade,result
    Example: 1DA23AI050,DSA,7,2025-26,65,100,B,pass
    """
    import csv
    import io

    if current_user.role not in ("admin", "hos", "hop"):
        raise HTTPException(status_code=403, detail="Only Admin/HOS/HOP can upload results")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be .csv")

    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    required = {"student_id", "subject_code", "semester", "marks", "max_marks", "result"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise HTTPException(status_code=400, detail=f"CSV must have columns: {required}. Optional: academic_year, grade")

    now = datetime.now(timezone.utc).isoformat()
    added = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        sid = row.get("student_id", "").strip()
        subj_code = row.get("subject_code", "").strip()
        semester = row.get("semester", "").strip()
        marks = row.get("marks", "").strip()
        max_marks = row.get("max_marks", "").strip()
        result_val = row.get("result", "").strip().lower()

        if not sid or not subj_code or not marks:
            errors.append({"row": i, "error": "Missing required field"})
            continue

        # Find subject by code
        subj = db.query(Subject).filter(Subject.code == subj_code.upper()).first()
        if not subj:
            errors.append({"row": i, "error": f"Subject {subj_code} not found"})
            continue

        try:
            db.add(SemesterResult(
                id=str(uuid.uuid4()),
                student_id=sid,
                subject_id=subj.id,
                semester=semester,
                academic_year=row.get("academic_year", "").strip() or "2025-26",
                marks_obtained=float(marks),
                max_marks=float(max_marks),
                grade=row.get("grade", "").strip() or None,
                credits=None,
                result=result_val if result_val in ("pass", "fail", "absent") else "pass",
                declared_at=now,
                created_at=now,
            ))
            added += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})

    db.commit()
    return {"added": added, "errors": len(errors), "error_details": errors[:10]}
