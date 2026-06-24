"""
Liveness / Anti-Spoofing Module
===============================
Basic anti-spoofing check for single-frame images.

For the pilot, this uses a simple heuristic approach based on:
- Detection confidence (very low confidence suggests a printed photo)
- Face size relative to image (very small faces are suspicious)
- Laplacian variance (blurriness check — printed photos tend to be sharper/flatter)

Phase 2 will integrate MiniFASNet or Silent-FAS for deep learning-based anti-spoofing.

Usage:
    from vista.vision.liveness import check_liveness
    result = check_liveness(face_data, image_path)
"""
from __future__ import annotations

import cv2
import numpy as np


# Minimum detection confidence to consider "live"
MIN_DET_CONFIDENCE = 0.5

# Minimum face size (width in pixels) — tiny faces are unreliable
MIN_FACE_WIDTH = 50

# Laplacian variance threshold — very low = too blurry, very high = screen artifact
MIN_LAPLACIAN_VARIANCE = 20.0


def check_liveness(
    face_data: dict,
    image_path: str | None = None,
) -> dict:
    """
    Perform basic liveness check on a detected face.

    Args:
        face_data: Dict from detect.py containing bbox, det_score, etc.
        image_path: Optional path to original image for texture analysis.

    Returns:
        {
            "liveness_passed": bool,
            "liveness_score": float (0.0-1.0, higher = more likely real),
            "reason": str or None (why it failed, if it did)
        }
    """
    score = 1.0
    reason = None

    # Check 1: Detection confidence
    det_score = face_data.get("det_score", 0.0)
    if det_score < MIN_DET_CONFIDENCE:
        return {
            "liveness_passed": False,
            "liveness_score": det_score * 0.5,
            "reason": f"Detection confidence too low ({det_score:.2f})",
        }

    # Check 2: Face size
    bbox = face_data.get("bbox", [0, 0, 0, 0])
    face_width = bbox[2] - bbox[0] if len(bbox) >= 4 else 0
    if face_width < MIN_FACE_WIDTH:
        return {
            "liveness_passed": False,
            "liveness_score": 0.3,
            "reason": f"Face too small ({face_width:.0f}px width)",
        }

    # Check 3: Texture analysis (if image available)
    if image_path is not None:
        try:
            img = cv2.imread(image_path)
            if img is not None:
                x1, y1, x2, y2 = [int(c) for c in bbox[:4]]
                # Clamp to image bounds
                h, w = img.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                face_crop = img[y1:y2, x1:x2]
                if face_crop.size > 0:
                    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

                    if laplacian_var < MIN_LAPLACIAN_VARIANCE:
                        score *= 0.6
                        reason = f"Low texture variance ({laplacian_var:.1f})"
        except Exception:
            pass  # Don't fail liveness on texture analysis errors

    # Combine scores
    liveness_score = score * min(1.0, det_score / 0.8)
    passed = liveness_score >= 0.5 and reason is None

    return {
        "liveness_passed": passed,
        "liveness_score": liveness_score,
        "reason": reason,
    }
