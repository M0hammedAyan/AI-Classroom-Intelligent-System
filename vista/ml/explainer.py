"""
SHAP Explainability Module
===========================
Provides per-prediction explanations using SHAP TreeExplainer for the XGBoost model.
Converts raw SHAP values into human-readable reason strings.

Usage:
    from vista.ml.explainer import explain_prediction
    reasons = explain_prediction(feature_vector, model_artifact)
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np

MODEL_PATH = Path(__file__).parent / "model.pkl"

FEATURE_NAMES = [
    "overall_attendance",
    "recent_attendance",
    "avg_score",
    "recent_score",
    "failed_subjects",
]

FEATURE_DESCRIPTIONS = {
    "overall_attendance": "Overall attendance",
    "recent_attendance": "Recent attendance",
    "avg_score": "Average internal marks",
    "recent_score": "Recent assessment score",
    "failed_subjects": "Failed subjects count",
}

LABEL_NAMES = ["LOW", "MEDIUM", "HIGH"]


def _load_model() -> dict:
    """Load the trained model artifact."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run: python -m vista.ml.train")
    with MODEL_PATH.open("rb") as f:
        return pickle.load(f)


def _get_explainer(model: Any):
    """Create a SHAP TreeExplainer for the model."""
    import shap
    return shap.TreeExplainer(model)


def explain_prediction(
    feature_values: list[float],
    predicted_class_idx: int | None = None,
    max_reasons: int = 4,
) -> dict:
    """
    Generate SHAP-based explanations for a single prediction.

    Args:
        feature_values: List of 5 feature values matching FEATURE_NAMES order.
        predicted_class_idx: Index of predicted class (0=LOW, 1=MEDIUM, 2=HIGH).
                            If None, uses the class with highest prediction.
        max_reasons: Maximum number of reasons to return.

    Returns:
        {
            "reasons": [str, ...],          # Human-readable reason strings
            "shap_values": {feature: value}, # Raw SHAP contributions
            "base_value": float,             # Model's base prediction
            "predicted_class": str,          # "LOW", "MEDIUM", or "HIGH"
        }
    """
    import shap

    artifact = _load_model()
    model = artifact["model"]
    scaler = artifact.get("scaler")
    needs_scaling = artifact.get("needs_scaling", False)

    # Prepare features
    features_array = np.array([feature_values])
    if needs_scaling and scaler is not None:
        features_array = scaler.transform(features_array)

    # Get prediction
    proba = model.predict_proba(features_array)[0]
    if predicted_class_idx is None:
        predicted_class_idx = int(np.argmax(proba))

    # Compute SHAP values
    explainer = _get_explainer(model)
    shap_values = explainer.shap_values(features_array)

    # shap_values shape: (n_classes, n_samples, n_features) or (n_samples, n_features)
    if isinstance(shap_values, list):
        # Multi-class: list of arrays, one per class
        class_shap = shap_values[predicted_class_idx][0]
        base_value = explainer.expected_value[predicted_class_idx]
    elif len(shap_values.shape) == 3:
        # Shape: (n_samples, n_features, n_classes)
        class_shap = shap_values[0, :, predicted_class_idx]
        base_value = explainer.expected_value[predicted_class_idx]
    else:
        # Binary or single output
        class_shap = shap_values[0]
        base_value = float(explainer.expected_value)

    # Build reason strings from top contributors
    feature_contributions = []
    for i, (name, shap_val) in enumerate(zip(FEATURE_NAMES, class_shap)):
        feature_contributions.append({
            "feature": name,
            "description": FEATURE_DESCRIPTIONS[name],
            "shap_value": float(shap_val),
            "feature_value": feature_values[i],
            "direction": "increases risk" if shap_val > 0 else "decreases risk",
        })

    # Sort by absolute SHAP value (most important first)
    feature_contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    # Generate human-readable reasons
    reasons = []
    for contrib in feature_contributions[:max_reasons]:
        if abs(contrib["shap_value"]) < 0.01:
            continue  # Skip negligible contributions

        reason = _format_reason(contrib)
        if reason:
            reasons.append(reason)

    return {
        "reasons": reasons,
        "shap_values": {
            name: float(val) for name, val in zip(FEATURE_NAMES, class_shap)
        },
        "base_value": float(base_value),
        "predicted_class": LABEL_NAMES[predicted_class_idx],
        "confidence": float(proba[predicted_class_idx]),
    }


def _format_reason(contrib: dict) -> str | None:
    """Convert a SHAP contribution into a human-readable reason string."""
    name = contrib["feature"]
    value = contrib["feature_value"]
    direction = contrib["direction"]
    shap_val = contrib["shap_value"]

    if abs(shap_val) < 0.01:
        return None

    if name == "overall_attendance":
        if shap_val > 0 and value < 75:
            return f"Overall attendance at {value:.0f}% — below recommended level"
        elif shap_val > 0:
            return None  # Don't flag high attendance as a risk factor
        else:
            return f"Good overall attendance ({value:.0f}%) — reducing risk"

    elif name == "recent_attendance":
        if shap_val > 0 and value < 70:
            return f"Recent attendance dropped to {value:.0f}% — declining trend"
        elif shap_val > 0:
            return None  # Don't flag acceptable recent attendance
        else:
            return None  # Skip positive mentions

    elif name == "avg_score":
        if shap_val > 0 and value < 60:
            return f"Average marks at {value:.0f}% — below passing threshold"
        elif shap_val > 0:
            return None  # Don't flag acceptable scores
        else:
            return None  # Skip positive mentions

    elif name == "recent_score":
        if shap_val > 0 and value < 55:
            return f"Recent assessment score {value:.0f}% — declining performance"
        elif shap_val > 0:
            return None  # Don't flag acceptable recent scores
        else:
            return None  # Skip positive mentions

    elif name == "failed_subjects":
        if value > 0 and shap_val > 0:
            return f"{int(value)} subject(s) failed — significant academic concern"
        else:
            return None  # Don't mention zero failures

    return f"{FEATURE_DESCRIPTIONS[name]}: {value:.1f} ({direction})"


def get_shap_summary(feature_values_batch: list[list[float]]) -> dict:
    """
    Generate SHAP summary statistics for a batch of students.
    Useful for understanding global feature importance.

    Returns:
        {
            "feature_importance": {feature_name: mean_abs_shap_value},
            "top_features": [ordered list of features by importance]
        }
    """
    import shap

    artifact = _load_model()
    model = artifact["model"]
    scaler = artifact.get("scaler")
    needs_scaling = artifact.get("needs_scaling", False)

    features_array = np.array(feature_values_batch)
    if needs_scaling and scaler is not None:
        features_array = scaler.transform(features_array)

    explainer = _get_explainer(model)
    shap_values = explainer.shap_values(features_array)

    # Compute mean absolute SHAP per feature (across all classes and samples)
    if isinstance(shap_values, list):
        all_shap = np.array(shap_values)  # (n_classes, n_samples, n_features)
        mean_abs = np.mean(np.abs(all_shap), axis=(0, 1))
    elif len(shap_values.shape) == 3:
        mean_abs = np.mean(np.abs(shap_values), axis=(0, 2))
    else:
        mean_abs = np.mean(np.abs(shap_values), axis=0)

    importance = {name: float(val) for name, val in zip(FEATURE_NAMES, mean_abs)}
    top_features = sorted(importance.keys(), key=lambda k: importance[k], reverse=True)

    return {
        "feature_importance": importance,
        "top_features": top_features,
    }
