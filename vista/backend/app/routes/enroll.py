"""
Student Face Enrollment API
============================
Accepts base64-encoded face images and registers the student's embedding.

Endpoint: POST /api/v1/students/{student_id}/enroll
Auth: Admin or HOS
"""
from __future__ import annotations

import base64
import os
import tempfile
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.student import Student
from ..models.user import User
from ..routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["enrollment"])


def _require_enroll_access(current_user: User = Depends(get_current_user)) -> User:
    """Admin or HOS can enroll faces."""
    if current_user.role not in ("admin", "hos"):
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Admin or HOS role required for enrollment."})
    return current_user


class EnrollRequest(BaseModel):
    images: list[str]  # List of base64-encoded JPEG/PNG images (1-5)


# Rate limiting: max 10 enrollments per 10 minutes per user
_enroll_attempts: dict[str, list[float]] = {}

@router.post("/{student_id}/enroll")
def enroll_student(
    student_id: str,
    body: EnrollRequest,
    db: Session = Depends(get_db),
    _user=Depends(_require_enroll_access),
):
    """
    Enroll a student's face by providing 1-5 base64-encoded images.
    Extracts embeddings, averages them, and stores in the students table.
    """
    import time as _time
    # Rate limit check
    user_id = _user.id
    now = _time.time()
    attempts = _enroll_attempts.get(user_id, [])
    attempts = [t for t in attempts if now - t < 600]  # 10 min window
    if len(attempts) >= 10:
        raise HTTPException(status_code=429, detail={"code": "RATE_LIMITED", "message": "Too many enrollment attempts. Try again in 10 minutes."})
    attempts.append(now)
    _enroll_attempts[user_id] = attempts

    # Validate student exists
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": f"No student with id {student_id}."},
        )

    # Validate image count
    if not body.images:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_IMAGES", "message": "At least 1 image is required."},
        )
    if len(body.images) > 5:
        raise HTTPException(
            status_code=400,
            detail={"code": "TOO_MANY_IMAGES", "message": "Maximum 5 images allowed."},
        )

    # Decode images to temp files
    temp_paths = []
    try:
        for i, img_b64 in enumerate(body.images):
            try:
                img_bytes = base64.b64decode(img_b64)
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail={"code": "INVALID_IMAGE", "message": f"Image {i+1} is not valid base64."},
                )
            if len(img_bytes) > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail={"code": "UPLOAD_TOO_LARGE", "message": f"Image {i+1} exceeds 5 MB."},
                )

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            tmp.write(img_bytes)
            tmp.close()
            temp_paths.append(tmp.name)

        # Run enrollment via vision module
        from vista.vision.enroll import enroll_student as vision_enroll

        result = vision_enroll(student_id, temp_paths)

    finally:
        # Clean up temp files
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)

    if not result["enrolled"]:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "ENROLLMENT_FAILED",
                "message": result["error"] or "Enrollment failed.",
                "details": {
                    "images_processed": result["images_processed"],
                    "images_failed": result["images_failed"],
                },
            },
        )

    return {
        "student_id": student_id,
        "student_name": student.name,
        "enrolled": True,
        "images_processed": result["images_processed"],
        "images_failed": result["images_failed"],
        "embedding_quality": result["embedding_quality"],
        "enrolled_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/bulk-enroll")
async def bulk_enroll(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _user=Depends(_require_enroll_access),
):
    """
    Bulk face enrollment — upload multiple images.
    Filename convention: {student_id}_1.jpg, {student_id}_2.jpg, etc.
    Or: {student_id}.jpg (single image per student)
    
    Groups images by student_id prefix (before underscore or dot), enrolls each.
    """
    from collections import defaultdict
    import tempfile

    # Group files by student_id
    student_files: dict[str, list[str]] = defaultdict(list)
    temp_paths = []

    try:
        for f in files:
            # Extract student_id from filename: "1DA23AI043_1.jpg" → "1DA23AI043"
            name = f.filename.rsplit('.', 1)[0]  # remove extension
            sid = name.split('_')[0].split(' ')[0].strip()  # take part before underscore/space
            if not sid:
                continue

            # Save to temp
            content = await f.read()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            tmp.write(content)
            tmp.close()
            temp_paths.append(tmp.name)
            student_files[sid].append(tmp.name)

        # Enroll each student
        from vista.vision.enroll import enroll_student as vision_enroll

        results = []
        for sid, img_paths in student_files.items():
            # Verify student exists
            student = db.query(Student).filter(Student.student_id == sid).first()
            if not student:
                results.append({"student_id": sid, "enrolled": False, "error": "Student not found"})
                continue

            result = vision_enroll(sid, img_paths[:5])  # Max 5 images per student
            results.append({
                "student_id": sid,
                "enrolled": result["enrolled"],
                "images_processed": result["images_processed"],
                "quality": result["embedding_quality"],
                "error": result.get("error"),
            })

    finally:
        for p in temp_paths:
            if os.path.exists(p):
                os.remove(p)

    enrolled_count = sum(1 for r in results if r["enrolled"])
    return {
        "total_students": len(student_files),
        "enrolled": enrolled_count,
        "failed": len(results) - enrolled_count,
        "results": results,
    }
