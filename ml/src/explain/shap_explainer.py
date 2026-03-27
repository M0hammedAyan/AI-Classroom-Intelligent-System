from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import shap


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "model.pkl"
DATA_PATH = PROJECT_ROOT / "ml" / "data" / "sample" / "student_data.csv"
TOP_K_FEATURES = 3
MIN_REASON_COUNT = 2


try:
    from ml.src.features.build_features import build_features, load_dataset
except ModuleNotFoundError:
    import sys

    sys.path.append(str(PROJECT_ROOT))
    from ml.src.features.build_features import build_features, load_dataset


def load_model_artifact(model_path: Path | str = MODEL_PATH) -> Dict[str, Any]:
    """Load the trained model artifact from disk."""
    with Path(model_path).open("rb") as model_file:
        return pickle.load(model_file)


def _ensure_single_student(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if df.shape[0] != 1:
        raise ValueError("Input DataFrame must contain exactly one student row.")
    return df.copy()


def _prepare_feature_row(df: pd.DataFrame, feature_columns: List[str]) -> pd.DataFrame:
    prepared_df = df.copy()
    if "label" not in prepared_df.columns:
        prepared_df["label"] = 0

    featured_df = build_features(prepared_df)
    return featured_df.reindex(columns=feature_columns, fill_value=0)


def _get_background_data(feature_columns: List[str], data_path: Path | str = DATA_PATH) -> pd.DataFrame:
    raw_df = load_dataset(data_path)
    featured_df = build_features(raw_df)
    return featured_df.reindex(columns=feature_columns, fill_value=0)


def _extract_feature_impacts(model: Any, x_row: pd.DataFrame, background_df: pd.DataFrame) -> pd.Series:
    shap_model = model

    # SHAP may not directly support calibrated wrappers; fall back to an underlying estimator.
    if hasattr(model, "calibrated_classifiers_") and getattr(model, "calibrated_classifiers_", None):
        first_calibrator = model.calibrated_classifiers_[0]
        if hasattr(first_calibrator, "estimator"):
            shap_model = first_calibrator.estimator
    elif hasattr(model, "estimator"):
        shap_model = model.estimator

    explainer = shap.Explainer(shap_model, background_df)
    explanation = explainer(x_row)

    if isinstance(explanation, list):
        if not explanation:
            raise ValueError("SHAP explainer returned an empty explanation list.")
        explanation_obj: Any = explanation[0]
    else:
        explanation_obj = explanation

    values = np.asarray(explanation_obj.values)
    if values.ndim == 3:
        # Multi-output shape: (n_samples, n_features, n_classes). Use fail-class index 1 when available.
        class_index = 1 if values.shape[2] > 1 else 0
        sample_values = values[0, :, class_index]
    elif values.ndim == 2:
        # Standard binary shape: (n_samples, n_features).
        sample_values = values[0, :]
    else:
        raise ValueError("Unexpected SHAP value dimensions.")

    return pd.Series(sample_values, index=x_row.columns)


def _reason_from_feature(feature_name: str, feature_value: float) -> str | None:
    if feature_name == "score_velocity":
        if feature_value < -0.1:
            return "Rapid score decline"
        return None

    if feature_name == "performance_drop_flag":
        if feature_value >= 1:
            return "Sudden drop in performance"
        return None

    if feature_name == "attendance_streak_impact":
        if feature_value > 0.2:
            return "Irregular attendance pattern"
        return None

    if feature_name == "recent_vs_past_attendance_ratio":
        if feature_value < 1.0:
            return "Attendance worsening"
        return None

    if feature_name in {"overall_attendance", "recent_attendance"}:
        if feature_value < 75:
            return "Attendance below recommended level"
        return None

    if feature_name in {"avg_score", "recent_score"}:
        if feature_value < 40:
            return "Low academic scores"
        return None

    if feature_name == "score_trend":
        if feature_value < 0:
            return "Declining scores"
        return None

    if feature_name in {"failed_subjects", "high_failure_flag"}:
        return "Multiple failed subjects"

    if feature_name == "low_attendance_flag":
        return "Attendance below recommended level"

    if feature_name == "declining_performance_flag":
        return "Declining scores"

    if feature_name == "attendance_drop":
        if feature_value > 0:
            return "Attendance worsening"
        return None

    if feature_name == "severe_risk_flag" and feature_value >= 1:
        return "Severe risk pattern detected"

    if feature_name == "borderline_flag" and feature_value >= 1:
        return "Performance near failing threshold"

    return None


def _top_reasons_from_impacts(
    impacts: pd.Series,
    x_row: pd.DataFrame,
    top_k: int = TOP_K_FEATURES,
) -> List[Dict[str, Any]]:
    ordered_features = impacts.abs().sort_values(ascending=False).index.tolist()

    reason_texts: List[str] = []
    for feature_name in ordered_features:
        reason = _reason_from_feature(feature_name, float(x_row.iloc[0][feature_name]))
        if reason and reason not in reason_texts:
            reason_texts.append(reason)
        if len(reason_texts) >= top_k:
            break

    if len(reason_texts) < MIN_REASON_COUNT:
        fallback_order = [
            "Attendance below recommended level",
            "Low academic scores",
            "Declining scores",
            "Multiple failed subjects",
        ]
        for fallback_reason in fallback_order:
            if fallback_reason not in reason_texts:
                reason_texts.append(fallback_reason)
            if len(reason_texts) >= MIN_REASON_COUNT:
                break

    return [
        {"text": reason_text, "priority": idx + 1}
        for idx, reason_text in enumerate(reason_texts[:top_k])
    ]


def explain_prediction(df: pd.DataFrame) -> list:
    """Return top 3 human-readable reasons that most influence one student's risk prediction."""
    student_df = _ensure_single_student(df)
    artifact = load_model_artifact(MODEL_PATH)

    model = artifact["model"]
    feature_columns = list(artifact["feature_columns"])

    x_row = _prepare_feature_row(student_df, feature_columns)
    background_df = _get_background_data(feature_columns, DATA_PATH)

    impacts = _extract_feature_impacts(model, x_row, background_df)
    return _top_reasons_from_impacts(impacts, x_row, top_k=TOP_K_FEATURES)
