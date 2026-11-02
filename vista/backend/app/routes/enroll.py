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

import cv2
import numpy as np
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
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Admin role required for enrollment."})
    return current_user


class EnrollRequest(BaseModel):
    images: list[str]  # List of base64-encoded JPEG/PNG images


def _decode_image(img_b64: str, index: int) -> bytes:
    try:
        img_bytes = base64.b64decode(img_b64, validate=True)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_IMAGE", "message": f"Image {index + 1} is not valid base64."},
        ) from exc

    if len(img_bytes) > 30 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail={"code": "UPLOAD_TOO_LARGE", "message": f"Image {index + 1} exceeds 30 MB."},
        )

    if not (img_bytes.startswith(b"\xff\xd8\xff") or img_bytes.startswith(b"\x89PNG\r\n\x1a\n")):
        raise HTTPException(
            status_code=400,
            detail={"code": "UNSUPPORTED_FORMAT", "message": f"Image {index + 1} must be a JPEG or PNG."},
        )
    if cv2.imdecode(np.frombuffer(img_bytes, dtype="uint8"), cv2.IMREAD_COLOR) is None:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_IMAGE", "message": f"Image {index + 1} is not a readable JPEG or PNG."},
        )
    return img_bytes


@router.post("/{student_id}/enroll")
def enroll_student(
    student_id: str,
    body: EnrollRequest,
    db: Session = Depends(get_db),
    _user=Depends(_require_enroll_access),
):
    """
    Enroll a student's face by providing base64-encoded images.
    Extracts embeddings, averages them, and stores in the students table.
    """
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

    # Decode images to temp files
    temp_paths = []
    try:
        for i, img_b64 in enumerate(body.images):
            img_bytes = _decode_image(img_b64, i)

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
        no_face = (result["error"] or "").startswith("No faces detected")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_FACE_DETECTED" if no_face else "ENROLLMENT_FAILED",
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

            result = vision_enroll(sid, img_paths)  # All images per student
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
