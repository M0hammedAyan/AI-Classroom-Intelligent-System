"""
Face Detection Module
=====================
Uses InsightFace's built-in SCRFD detector (bundled with buffalo_l model pack).
Detects faces and returns bounding boxes + aligned face crops.

Usage:
    from vista.vision.detect import FaceDetector
    detector = FaceDetector()
    faces = detector.detect(image_path)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


class FaceDetector:
    """Detect faces in an image using InsightFace's SCRFD detector."""

    def __init__(self, det_size: tuple[int, int] = (640, 640)):
        self._app = None
        self._det_size = det_size

    def _ensure_loaded(self) -> None:
        """Lazy-load the InsightFace model on first use."""
        if self._app is not None:
            return

        from insightface.app import FaceAnalysis

        self._app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )
        self._app.prepare(ctx_id=-1, det_size=self._det_size)

    def detect(self, image_path: str) -> list[dict[str, Any]]:
        """
        Detect all faces in an image.

        Args:
            image_path: Path to image file (JPEG/PNG).

        Returns:
            List of face dicts, each containing:
                - bbox: [x1, y1, x2, y2] bounding box
                - embedding: 512-dim numpy array (normalized)
                - det_score: detection confidence [0.0, 1.0]
                - landmark: 5-point facial landmarks
                - aligned_face: aligned face crop (112x112 BGR numpy array)
        """
        self._ensure_loaded()

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        faces = self._app.get(img)

        results = []
        for face in faces:
            results.append({
                "bbox": face.bbox.tolist(),
                "embedding": face.normed_embedding,
                "det_score": float(face.det_score),
                "landmark": face.landmark_2d_106 if hasattr(face, "landmark_2d_106") else face.kps,
                "aligned_face": face.get("aligned_face", None),
            })

        # Sort by detection score (highest first)
        results.sort(key=lambda x: x["det_score"], reverse=True)
        return results

    def detect_single(self, image_path: str) -> dict[str, Any] | None:
        """
        Detect the single largest/highest-confidence face in an image.
        Returns None if no face found.
        """
        faces = self.detect(image_path)
        if not faces:
            return None
        return faces[0]


# Module-level singleton (lazy-loaded on first use)
_detector: FaceDetector | None = None


def get_detector() -> FaceDetector:
    """Get or create the module-level FaceDetector singleton."""
    global _detector
    if _detector is None:
        _detector = FaceDetector()
    return _detector
