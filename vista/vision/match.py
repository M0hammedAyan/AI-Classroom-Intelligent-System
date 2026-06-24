"""
Face Matching Module
====================
Compares a probe embedding against stored student embeddings using cosine similarity.
Returns the best match if above threshold.

Usage:
    from vista.vision.match import FaceMatcher
    matcher = FaceMatcher(threshold=0.55)
    result = matcher.match(probe_embedding, stored_embeddings)
"""
from __future__ import annotations

import numpy as np

from .embed import list_to_embedding


# Default cosine similarity threshold for a positive match.
# Tuned for ArcFace R50 on small galleries (20-30 students).
# Lower = more permissive (higher recall, lower precision)
# Higher = more strict (higher precision, lower recall)
DEFAULT_THRESHOLD = 0.55


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two L2-normalized vectors.
    For normalized vectors: cosine_sim = dot(a, b)
    """
    return float(np.dot(a, b))


class FaceMatcher:
    """Match a probe face against a gallery of enrolled student embeddings."""

    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        self.threshold = threshold

    def match(
        self,
        probe_embedding: np.ndarray,
        gallery: dict[str, list[float]],
    ) -> dict:
        """
        Find the best matching student for a probe embedding.

        Args:
            probe_embedding: 512-dim normalized embedding of the detected face.
            gallery: Dict mapping student_id → embedding (as list of floats from DB).

        Returns:
            {
                "student_id": str or None,
                "similarity": float (0.0-1.0),
                "matched": bool
            }
        """
        if not gallery:
            return {"student_id": None, "similarity": 0.0, "matched": False}

        best_id = None
        best_sim = -1.0

        for student_id, emb_list in gallery.items():
            stored_emb = list_to_embedding(emb_list)
            sim = cosine_similarity(probe_embedding, stored_emb)
            if sim > best_sim:
                best_sim = sim
                best_id = student_id

        matched = best_sim >= self.threshold

        return {
            "student_id": best_id if matched else None,
            "similarity": best_sim,
            "matched": matched,
        }

    def match_all(
        self,
        probe_embeddings: list[np.ndarray],
        gallery: dict[str, list[float]],
    ) -> list[dict]:
        """
        Match multiple probe faces against the gallery.
        Used for multi-face detection in a single image.

        Returns:
            List of match results, one per probe face.
        """
        return [self.match(probe, gallery) for probe in probe_embeddings]
