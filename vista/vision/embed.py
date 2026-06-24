"""
Face Embedding Module
=====================
Extracts 512-dimensional face embeddings using ArcFace (R50 backbone).
InsightFace's buffalo_l model pack includes the recognition model.

The embedding extraction is handled by the FaceAnalysis app in detect.py,
which runs detection + recognition in a single pass. This module provides
utility functions for embedding operations.

Usage:
    from vista.vision.embed import normalize_embedding, average_embeddings
"""
from __future__ import annotations

import numpy as np


def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """
    L2-normalize an embedding vector.
    InsightFace already returns normalized embeddings, but this is a safety net.
    """
    norm = np.linalg.norm(embedding)
    if norm < 1e-10:
        return embedding
    return embedding / norm


def average_embeddings(embeddings: list[np.ndarray]) -> np.ndarray:
    """
    Compute the mean embedding from multiple enrollment images.
    Used during student enrollment (3-5 photos → 1 reference embedding).

    Args:
        embeddings: List of 512-dim normalized embedding vectors.

    Returns:
        Averaged and re-normalized 512-dim embedding.
    """
    if not embeddings:
        raise ValueError("Cannot average zero embeddings")

    stacked = np.stack(embeddings, axis=0)
    mean_emb = np.mean(stacked, axis=0)
    return normalize_embedding(mean_emb)


def embedding_to_list(embedding: np.ndarray) -> list[float]:
    """Convert numpy embedding to JSON-serializable list of floats."""
    return embedding.astype(float).tolist()


def list_to_embedding(emb_list: list[float]) -> np.ndarray:
    """Convert JSON list back to numpy embedding."""
    return np.array(emb_list, dtype=np.float32)
