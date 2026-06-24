"""
Student Face Enrollment
=======================
Register student face embeddings in the database.
Accepts 1-5 images per student, averages embeddings, stores in students table.

Usage (CLI):
    python -m vista.vision.enroll --student-id CS22B001 --images img1.jpg img2.jpg img3.jpg

Usage (programmatic):
    from vista.vision.enroll import enroll_student
    result = enroll_student("CS22B001", ["img1.jpg", "img2.jpg", "img3.jpg"])
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np

from .detect import get_detector
from .embed import average_embeddings, embedding_to_list

logger = logging.getLogger(__name__)


def enroll_student(student_id: str, image_paths: list[str]) -> dict:
    """
    Enroll a student by extracting and averaging face embeddings from multiple images.

    Args:
        student_id: College roll number (e.g., "CS22B001")
        image_paths: List of 1-5 image file paths containing the student's face.

    Returns:
        {
            "student_id": str,
            "enrolled": bool,
            "images_processed": int,
            "images_failed": int,
            "embedding_quality": "good" | "fair" | "poor",
            "error": str or None
        }
    """
    if not image_paths:
        return {
            "student_id": student_id,
            "enrolled": False,
            "images_processed": 0,
            "images_failed": 0,
            "embedding_quality": "poor",
            "error": "No images provided",
        }

    detector = get_detector()
    embeddings = []
    failed = 0

    for img_path in image_paths:
        try:
            face = detector.detect_single(img_path)
            if face is None:
                logger.warning(f"No face detected in {img_path}")
                failed += 1
                continue
            if face["embedding"] is not None:
                embeddings.append(face["embedding"])
            else:
                failed += 1
        except Exception as exc:
            logger.error(f"Error processing {img_path}: {exc}")
            failed += 1

    if not embeddings:
        return {
            "student_id": student_id,
            "enrolled": False,
            "images_processed": 0,
            "images_failed": failed,
            "embedding_quality": "poor",
            "error": "No faces detected in any provided images",
        }

    # Average embeddings
    avg_embedding = average_embeddings(embeddings)
    emb_list = embedding_to_list(avg_embedding)

    # Store in database
    try:
        _store_embedding(student_id, emb_list)
    except Exception as exc:
        return {
            "student_id": student_id,
            "enrolled": False,
            "images_processed": len(embeddings),
            "images_failed": failed,
            "embedding_quality": _quality_score(len(embeddings), len(image_paths)),
            "error": f"Database error: {exc}",
        }

    return {
        "student_id": student_id,
        "enrolled": True,
        "images_processed": len(embeddings),
        "images_failed": failed,
        "embedding_quality": _quality_score(len(embeddings), len(image_paths)),
        "error": None,
    }


def _store_embedding(student_id: str, embedding: list[float]) -> None:
    """Store the embedding in the students table."""
    from datetime import datetime, timezone

    from vista.backend.app.db import SessionLocal
    from vista.backend.app.models.student import Student

    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if student is None:
            raise ValueError(f"Student {student_id} not found in database")

        student.embedding = json.dumps(embedding)
        student.enrolled_at = datetime.now(timezone.utc).isoformat()
        db.commit()
        logger.info(f"Enrolled student {student_id} (512-dim embedding stored)")
    finally:
        db.close()


def _quality_score(successful: int, total: int) -> str:
    """Rate enrollment quality based on how many images succeeded."""
    if successful >= 3:
        return "good"
    elif successful >= 2:
        return "fair"
    else:
        return "poor"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Enroll a student's face in VISTA.")
    parser.add_argument("--student-id", required=True, help="Student ID (e.g., CS22B001)")
    parser.add_argument("--images", nargs="+", required=True, help="Paths to face images (1-5)")
    args = parser.parse_args()

    # Validate images exist
    for img in args.images:
        if not Path(img).exists():
            print(f"Error: Image not found: {img}")
            return

    print(f"Enrolling student {args.student_id} with {len(args.images)} image(s)...")
    result = enroll_student(args.student_id, args.images)

    if result["enrolled"]:
        print(f"✓ Enrolled successfully!")
        print(f"  Images processed: {result['images_processed']}")
        print(f"  Quality: {result['embedding_quality']}")
    else:
        print(f"✗ Enrollment failed: {result['error']}")
        print(f"  Images failed: {result['images_failed']}")


if __name__ == "__main__":
    main()
