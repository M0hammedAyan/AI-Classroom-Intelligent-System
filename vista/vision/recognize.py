"""
Face Recognition Pipeline — Main Entry Point
=============================================
Orchestrates: detect → personal classifier → liveness → result

This is the FIXED PUBLIC API consumed by backend/app/routes/attendance.py.
The signature MUST NOT change without a team sync.

Usage:
    from vista.vision.recognize import recognize
    result = recognize("path/to/classroom_image.jpg")
    # Returns: {student_id, confidence, liveness_passed}
"""
from __future__ import annotations

import json
import logging
import os

import cv2
import numpy as np

from .detect import get_detector
from .embed import list_to_embedding
from .liveness import check_liveness
from .match import FaceMatcher
from .personal_classifier import classify_face

logger = logging.getLogger(__name__)

def _crop_face(image_path: str, bbox: list[float]) -> np.ndarray | None:
    image = cv2.imread(image_path)
    if image is None:
        return None
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    x1, y1, x2, y2 = [int(value) for value in bbox[:4]]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(width, x2), min(height, y2)
    if x2 <= x1 or y2 <= y1:
        return None
    return image[y1:y2, x1:x2].copy()


def _load_student_gallery() -> dict[str, list[float]]:
    """Load the currently enrolled student embeddings from the database."""
    try:
        from vista.backend.app.db import SessionLocal
        from vista.backend.app.models.student import Student

        db = SessionLocal()
        try:
            students = db.query(Student).filter(Student.embedding.isnot(None), Student.is_active.is_(True)).all()
            gallery: dict[str, list[float]] = {}
            for student in students:
                if not student.embedding:
                    continue
                try:
                    emb = json.loads(student.embedding)
                except (TypeError, json.JSONDecodeError):
                    continue
                if isinstance(emb, list) and len(emb) == 512:
                    gallery[student.student_id] = emb
            return gallery
        finally:
            db.close()
    except Exception:
        return {}


def _match_student_gallery(face: dict) -> dict:
    """Match an extracted face embedding against the enrolled gallery."""
    embedding = face.get("embedding")
    if embedding is None:
        return {"student_id": None, "confidence": 0.0, "matched": False}

    gallery = _load_student_gallery()
    if not gallery:
        return {"student_id": None, "confidence": 0.0, "matched": False}

    try:
        probe = np.asarray(embedding, dtype=np.float32)
    except Exception:
        return {"student_id": None, "confidence": 0.0, "matched": False}

    matcher = FaceMatcher(threshold=float(os.getenv("VISTA_FACE_MATCH_THRESHOLD", "0.55")))
    result = matcher.match(probe, gallery)
    if result["matched"]:
        return {
            "student_id": result["student_id"],
            "confidence": float(result["similarity"]),
            "matched": True,
        }

    return {
        "student_id": None,
        "confidence": float(result["similarity"]),
        "matched": False,
    }


def _classify_detected_face(image_path: str, face: dict) -> dict:
    gallery_match = _match_student_gallery(face)
    if gallery_match["matched"]:
        return {
            "student_id": gallery_match["student_id"],
            "confidence": gallery_match["confidence"],
        }

    crop = _crop_face(image_path, face["bbox"])
    if crop is None:
        return {"student_id": None, "confidence": max(gallery_match["confidence"], 0.0)}

    classifier_result = classify_face(crop)
    if classifier_result.get("student_id") is not None:
        return classifier_result

    return {
        "student_id": None,
        "confidence": max(classifier_result.get("confidence", 0.0), gallery_match["confidence"]),
    }


def recognize_all(image_path: str) -> list[dict]:
    """
    Recognize ALL student faces in an image.

    Uses the same detect → classify → liveness pipeline as recognize(),
    but processes every detected face instead of just the first one.

    Deduplicates: if the same student_id is matched by multiple faces,
    only the highest-confidence result is kept.

    Args:
        image_path: Path to image file (JPEG/PNG).

    Returns:
        List of dicts, each containing:
            {
                "student_id": str or None,
                "confidence": float,
                "liveness_passed": bool
            }
        Empty list if no faces are detected.
    """
    detector = get_detector()
    faces = detector.detect(image_path)

    if not faces:
        return []

    results: list[dict] = []

    for face in faces:
        # Liveness check per face
        liveness = check_liveness(face, image_path)
        liveness_passed = liveness["liveness_passed"]

        classification = _classify_detected_face(image_path, face)

        results.append({
            "student_id": classification["student_id"],
            "confidence": classification["confidence"],
            "liveness_passed": liveness_passed,
        })

    # Deduplicate: keep highest-confidence result per student_id
    seen: dict[str, dict] = {}
    deduped: list[dict] = []

    for r in results:
        sid = r["student_id"]
        if sid is None:
            # Always keep unrecognized faces (no dedup needed)
            deduped.append(r)
        elif sid not in seen or r["confidence"] > seen[sid]["confidence"]:
            seen[sid] = r

    deduped.extend(seen.values())
    return deduped


def recognize(image_path: str) -> dict:
    """
    Recognize a student face in an image.

    This is the FIXED PUBLIC API. Signature never changes.

    Args:
        image_path: Path to image file (JPEG/PNG).

    Returns:
        {
            "student_id": str or None,    # None if no confident match
            "confidence": float,           # 0.0–1.0
            "liveness_passed": bool
        }
    """
    # Step 1: Detect face
    detector = get_detector()
    face = detector.detect_single(image_path)

    if face is None:
        return {
            "student_id": None,
            "confidence": 0.0,
            "liveness_passed": False,
        }

    # Step 2: Liveness check
    liveness = check_liveness(face, image_path)

    if not liveness["liveness_passed"]:
        # Still try to identify who it might be (for logging purposes)
        classification = _classify_detected_face(image_path, face)
        return {
            "student_id": classification["student_id"],
            "confidence": classification["confidence"],
            "liveness_passed": False,
        }

    # Step 3: Classify with the personally trained student model.
    classification = _classify_detected_face(image_path, face)

    return {
        "student_id": classification["student_id"],
        "confidence": classification["confidence"],
        "liveness_passed": True,
    }
