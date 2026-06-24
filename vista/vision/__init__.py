"""
VISTA Vision Module — Face Recognition Pipeline
================================================
Public API:
    recognize(image_path: str) -> dict
        Returns: {student_id, confidence, liveness_passed}
"""
from .recognize import recognize

__all__ = ["recognize"]
