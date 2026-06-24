"""
Face Recognition Pipeline — Main Entry Point
=============================================
Orchestrates: detect → embed → match → liveness → result

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
from pathlib import Path

from .detect import get_detector
from .liveness import check_liveness
from .match import FaceMatcher

logger = logging.getLogger(__name__)

# Module-level matcher instance
_matcher = FaceMatcher(threshold=0.55)


def _load_gallery() -> dict[str, list[float]]:
    """
    Load enrolled student embeddings from the database.
    Returns dict mapping student_id → embedding (as list of floats).

    Falls back to empty dict if DB is unavailable (vision module
    should not depend on backend imports at import time).
    """
    try:
        from vista.backend.app.db import SessionLocal
        from vista.backend.app.models.student import Student

        db = SessionLocal()
        try:
            students = (
                db.query(Student)
                .filter(Student.embedding.isnot(None), Student.is_active == True)
                .all()
            )
            gallery = {}
            for s in students:
                if s.embedding:
                    emb = json.loads(s.embedding) if isinstance(s.embedding, str) else s.embedding
                    if isinstance(emb, list) and len(emb) == 512:
                        gallery[s.student_id] = emb
            return gallery
        finally:
            db.close()
    except Exception as exc:
        logger.warning(f"Could not load gallery from DB: {exc}")
        return {}


def recognize_all(image_path: str) -> list[dict]:
    """
    Recognize ALL student faces in an image.

    Uses the same detect → match → liveness pipeline as recognize(),
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

    gallery = _load_gallery()
    results: list[dict] = []

    for face in faces:
        # Liveness check per face
        liveness = check_liveness(face, image_path)
        liveness_passed = liveness["liveness_passed"]

        embedding = face.get("embedding")

        if embedding is None:
            results.append({
                "student_id": None,
                "confidence": face["det_score"],
                "liveness_passed": liveness_passed,
            })
            continue

        if not gallery:
            results.append({
                "student_id": None,
                "confidence": 0.0,
                "liveness_passed": liveness_passed,
            })
            continue

        match_result = _matcher.match(embedding, gallery)

        results.append({
            "student_id": match_result["student_id"],
            "confidence": match_result["similarity"] if match_result["matched"] else face["det_score"],
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
        gallery = _load_gallery()
        if gallery and face.get("embedding") is not None:
            match_result = _matcher.match(face["embedding"], gallery)
            return {
                "student_id": match_result["student_id"],  # may be None
                "confidence": match_result["similarity"],
                "liveness_passed": False,
            }
        return {
            "student_id": None,
            "confidence": face["det_score"],
            "liveness_passed": False,
        }

    # Step 3: Match against enrolled students
    embedding = face.get("embedding")
    if embedding is None:
        return {
            "student_id": None,
            "confidence": face["det_score"],
            "liveness_passed": True,
        }

    gallery = _load_gallery()
    if not gallery:
        logger.warning("No enrolled students in gallery — cannot match.")
        return {
            "student_id": None,
            "confidence": 0.0,
            "liveness_passed": True,
        }

    match_result = _matcher.match(embedding, gallery)

    return {
        "student_id": match_result["student_id"],
        "confidence": match_result["similarity"] if match_result["matched"] else face["det_score"],
        "liveness_passed": True,
    }
