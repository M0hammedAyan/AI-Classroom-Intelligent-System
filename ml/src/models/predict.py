from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "model.pkl"


try:
    from ml.src.features.build_features import build_features
except ModuleNotFoundError:
    import sys

    sys.path.append(str(PROJECT_ROOT))
    from ml.src.features.build_features import build_features


def load_model_artifact(model_path: Path | str = MODEL_PATH) -> Dict[str, Any]:
    """Load trained model artifact and metadata from disk."""
    path = Path(model_path)
    with path.open("rb") as model_file:
        artifact = pickle.load(model_file)
    return artifact


def _ensure_single_student(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if df.shape[0] != 1:
        raise ValueError("Input DataFrame must contain exactly one student row.")
    return df.copy()


def _prepare_for_feature_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    prepared_df = df.copy()

    # The shared feature pipeline expects label; a placeholder keeps inference path consistent.
    if "label" not in prepared_df.columns:
        prepared_df["label"] = 0

    return build_features(prepared_df)


def _risk_level_from_score(risk_score: float) -> str:
    if risk_score < 0.4:
        return "LOW"
    if risk_score < 0.7:
        return "MEDIUM"
    return "HIGH"


def _predict_probability(model: Any, x: pd.DataFrame) -> float:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x)
        return float(probabilities[0][1])

    if hasattr(model, "decision_function"):
        import numpy as np

        score = float(model.decision_function(x)[0])
        return float(1.0 / (1.0 + np.exp(-score)))

    prediction = model.predict(x)
    return float(prediction[0])


def _confidence_from_score(risk_score: float) -> float:
    # Normalize distance from 0.5 to [0, 1] for interpretable confidence.
    return max(0.0, min(1.0, 2.0 * abs(risk_score - 0.5)))


def predict_student(df: pd.DataFrame) -> dict:
    """Predict a single student's fail-risk score and risk level."""
    student_df = _ensure_single_student(df)
    artifact = load_model_artifact(MODEL_PATH)

    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    featured_df = _prepare_for_feature_pipeline(student_df)
    x = featured_df.reindex(columns=feature_columns, fill_value=0)

    risk_score = _predict_probability(model, x)
    risk_level = _risk_level_from_score(risk_score)
    confidence = _confidence_from_score(risk_score)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence": confidence,
    }
