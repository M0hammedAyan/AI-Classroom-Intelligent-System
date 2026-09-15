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

import logging

import cv2
import numpy as np

from .detect import get_detector
from .liveness import check_liveness
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


def _classify_detected_face(image_path: str, face: dict) -> dict:
    crop = _crop_face(image_path, face["bbox"])
    if crop is None:
        return {"student_id": None, "confidence": 0.0}
    return classify_face(crop)


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
