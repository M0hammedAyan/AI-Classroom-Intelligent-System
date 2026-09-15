"""Tests for the personally trained face-classifier adapter."""
from pathlib import Path

import numpy as np

from vista.vision.personal_classifier import classify_face, model_info


def test_personal_checkpoint_metadata():
    info = model_info()

    assert info["model"] == "personal_resnet50"
    assert info["classes"] == 20
    assert len(info["class_names"]) == 20
    assert 0.0 < info["threshold"] < 1.0


def test_personal_classifier_returns_known_class_for_npz_face():
    npz_path = Path("data/processed/facial_pipeline_results.npz")
    if not npz_path.exists():
        raise AssertionError(f"Required trained dataset is missing: {npz_path}")

    data = np.load(npz_path, allow_pickle=True)
    image = data["images"][0]
    result = classify_face(image)

    assert result["student_id"] is None or result["student_id"] in model_info()["class_names"]
    assert 0.0 <= result["confidence"] <= 1.0