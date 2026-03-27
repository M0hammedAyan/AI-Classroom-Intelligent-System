from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]


try:
    from ml.src.explain.shap_explainer import explain_prediction
    from ml.src.features.build_features import build_features
    from ml.src.models.predict import predict_student
except ModuleNotFoundError:
    import sys

    sys.path.append(str(PROJECT_ROOT))
    from ml.src.explain.shap_explainer import explain_prediction
    from ml.src.features.build_features import build_features
    from ml.src.models.predict import predict_student


REQUIRED_INPUT_KEYS = [
    "student_id",
    "overall_attendance",
    "recent_attendance",
    "avg_score",
    "recent_score",
    "failed_subjects",
]


def _validate_student_json(student_json: Dict[str, Any]) -> None:
    if not isinstance(student_json, dict):
        raise TypeError("student_json must be a dictionary.")

    missing = [key for key in REQUIRED_INPUT_KEYS if key not in student_json]
    if missing:
        raise ValueError(f"Missing required input keys: {missing}")


def _student_json_to_dataframe(student_json: Dict[str, Any]) -> pd.DataFrame:
    _validate_student_json(student_json)

    row = {
        "student_id": student_json["student_id"],
        "overall_attendance": student_json["overall_attendance"],
        "recent_attendance": student_json["recent_attendance"],
        "avg_score": student_json["avg_score"],
        "recent_score": student_json["recent_score"],
        "failed_subjects": student_json["failed_subjects"],
    }

    return pd.DataFrame([row])


def _compute_trend(row: pd.Series, risk_level: str, risk_score: float) -> str:

    score_trend = float(row["score_trend"])
    attendance_drop = float(row["attendance_drop"])

    trend = "STABLE"

    if score_trend < -5.0 and attendance_drop > 10.0:
        trend = "WORSENING"

    attendance_stable = abs(attendance_drop) <= 5.0
    if score_trend > 5.0 and attendance_stable and risk_score < 0.7:
        trend = "IMPROVING"

    if risk_level == "HIGH" and trend == "IMPROVING":
        trend = "STABLE"

    if risk_level == "LOW" and trend == "WORSENING":
        very_strong_negative_signal = score_trend < -12.0 and attendance_drop > 15.0 and risk_score >= 0.35
        if not very_strong_negative_signal:
            trend = "STABLE"

    return trend


def _validate_output_consistency(
    row: pd.Series,
    risk_level: str,
    reason_texts: List[str],
) -> tuple[str, List[str]]:
    validation_flags: List[str] = []

    strong_reason_markers = {
        "Attendance below recommended level",
        "Low academic scores",
        "Sudden drop in performance",
        "Rapid score decline",
        "Irregular attendance pattern",
        "Attendance worsening",
        "Multiple failed subjects",
        "Severe risk pattern detected",
    }

    has_strong_reason = any(
        any(marker in reason for marker in strong_reason_markers)
        for reason in reason_texts
    )

    if risk_level == "HIGH" and not has_strong_reason:
        validation_flags.append("HIGH_RISK_WITHOUT_STRONG_REASON")

    severe_flags_exist = bool(
        int(row.get("severe_risk_flag", 0)) == 1
        or int(row.get("performance_drop_flag", 0)) == 1
    )

    adjusted_risk_level = risk_level
    if risk_level == "LOW" and severe_flags_exist:
        adjusted_risk_level = "MEDIUM"
        validation_flags.append("LOW_RISK_OVERRIDDEN_BY_SEVERE_FLAGS")

    moderate_signal_count = 0
    if 60.0 <= float(row.get("overall_attendance", 0.0)) <= 75.0:
        moderate_signal_count += 1
    if 40.0 <= float(row.get("avg_score", 0.0)) <= 60.0:
        moderate_signal_count += 1
    if -5.0 <= float(row.get("score_trend", 0.0)) < 0.0:
        moderate_signal_count += 1

    if adjusted_risk_level == "LOW" and moderate_signal_count >= 2:
        adjusted_risk_level = "MEDIUM"
        validation_flags.append("MEDIUM_RISK_ASSIGNED_FROM_MODERATE_SIGNALS")

    return adjusted_risk_level, validation_flags


def _recommended_actions(risk_level: str, reason_texts: List[str]) -> List[str]:
    actions: List[str] = []

    for reason in reason_texts:
        reason_lower = reason.lower()

        if "irregular attendance" in reason_lower:
            action = "Monitor attendance daily and notify mentor"
            if action not in actions:
                actions.append(action)

        if "attendance" in reason_lower:
            action = "Schedule attendance counseling session"
            if action not in actions:
                actions.append(action)

        if "score" in reason_lower or "performance" in reason_lower:
            action = "Provide academic support and assign remedial work"
            if action not in actions:
                actions.append(action)

    if risk_level == "HIGH":
        high_action = "Immediate intervention required"
        if high_action not in actions:
            actions.append(high_action)
    elif risk_level == "MEDIUM":
        medium_action = "Monitor student progress weekly"
        if medium_action not in actions:
            actions.append(medium_action)
    elif risk_level == "LOW":
        low_action = "Maintain current performance"
        if low_action not in actions:
            actions.append(low_action)

    if len(actions) < 2:
        fallback = "Monitor student progress weekly" if risk_level != "LOW" else "Maintain current performance"
        if fallback not in actions:
            actions.append(fallback)

    return actions[:4]


def _confidence_from_risk_score(risk_score: float) -> float:
    confidence = abs(risk_score - 0.5) * 2.0
    confidence = max(0.0, min(1.0, confidence))
    return round(confidence, 2)


def _risk_change_label(previous_risk_score: Any, current_risk_score: float) -> str:
    if previous_risk_score is None:
        return "NO_PREVIOUS_DATA"

    try:
        previous = float(previous_risk_score)
    except (TypeError, ValueError):
        return "NO_PREVIOUS_DATA"

    delta = current_risk_score - previous
    if delta > 0.2:
        return "RISK_INCREASING"
    if delta < -0.2:
        return "RISK_IMPROVING"
    return "RISK_STABLE"


def _normalize_reasons(reasons: List[Any]) -> List[Dict[str, Any]]:
    clean_reason_texts: List[str] = []
    for reason in reasons:
        if isinstance(reason, dict):
            text = str(reason.get("text", "")).strip()
        else:
            text = str(reason).strip()

        if text and text not in clean_reason_texts:
            clean_reason_texts.append(text)

    return [
        {"text": text, "priority": idx + 1}
        for idx, text in enumerate(clean_reason_texts)
    ]


def _reason_texts(reasons: List[Dict[str, Any]]) -> List[str]:
    return [str(reason.get("text", "")).strip() for reason in reasons if str(reason.get("text", "")).strip()]


def _enforce_trend_reason_consistency(trend: str, reason_texts: List[str]) -> str:
    if trend != "WORSENING":
        return trend

    decline_markers = {
        "Attendance worsening",
        "Rapid score decline",
        "Sudden drop in performance",
        "Declining scores",
    }

    has_decline_reason = any(
        any(marker in text for marker in decline_markers)
        for text in reason_texts
    )

    return "WORSENING" if has_decline_reason else "STABLE"


def _build_summary(risk_level: str, reasons: List[Dict[str, Any]], recommended_actions: List[str]) -> str:
    key_issue = "current performance indicators"
    if reasons:
        key_issue = str(reasons[0].get("text", key_issue)).lower()

    if risk_level == "HIGH":
        tone = "Immediate attention is required."
    elif risk_level == "MEDIUM":
        tone = "Close monitoring is recommended."
    else:
        tone = "Continue regular monitoring."

    if recommended_actions:
        first_action = recommended_actions[0].rstrip(".")
        return f"Student is at {risk_level.lower()} risk due to {key_issue}; {first_action.lower()}."

    return f"Student is at {risk_level.lower()} risk due to {key_issue}. {tone}"


def run_pipeline(student_json: dict) -> dict:
    """Run full risk pipeline for one student and return a simple product response."""
    student_df = _student_json_to_dataframe(student_json)
    engineered_df = build_features(student_df.assign(label=0))
    engineered_row = engineered_df.iloc[0]

    prediction = predict_student(student_df)
    reasons = explain_prediction(student_df)
    normalized_reasons = _normalize_reasons(reasons)
    reason_texts = _reason_texts(normalized_reasons)

    adjusted_risk_level, validation_flags = _validate_output_consistency(
        engineered_row,
        risk_level=str(prediction["risk_level"]),
        reason_texts=reason_texts,
    )

    trend = _compute_trend(
        engineered_row,
        risk_level=adjusted_risk_level,
        risk_score=float(prediction["risk_score"]),
    )
    trend = _enforce_trend_reason_consistency(trend, reason_texts)
    confidence = _confidence_from_risk_score(float(prediction["risk_score"]))
    recommended_actions = _recommended_actions(adjusted_risk_level, reason_texts)
    risk_change = _risk_change_label(student_json.get("previous_risk_score"), float(prediction["risk_score"]))
    summary = _build_summary(adjusted_risk_level, normalized_reasons, recommended_actions)

    return {
        "student_id": str(student_json["student_id"]),
        "risk_score": float(prediction["risk_score"]),
        "risk_level": adjusted_risk_level,
        "confidence": confidence,
        "reasons": normalized_reasons,
        "recommended_actions": recommended_actions,
        "summary": summary,
        "trend": trend,
        "risk_change": risk_change,
        "validation_flags": validation_flags,
    }
