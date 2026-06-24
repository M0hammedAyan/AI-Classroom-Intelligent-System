from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from .features import FeatureVector, StudentMetrics, compute_features


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class StudentNotFoundError(Exception):
    pass


class InsufficientDataError(Exception):
    pass


# ---------------------------------------------------------------------------
# Result schema
# ---------------------------------------------------------------------------

@dataclass
class RiskResult:
    student_id: str
    risk_score: int                  # 0–100
    risk_level: str                  # "LOW" | "MEDIUM" | "HIGH"
    confidence: str                  # "high" | "moderate" | "low"
    reasons: list[str]               # max 4, ordered by severity
    recommendations: list[str]       # max 3
    computed_at: str                 # ISO 8601 UTC
    override_applied: bool
    override_reason: str | None

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------

WEIGHTS: dict[str, float] = {
    "attendance":   0.30,
    "marks":        0.25,
    "drop":         0.15,
    "decline":      0.15,
    "consecutive":  0.10,
    "engagement":   0.05,
}

TREND_SCORE: dict[str, float] = {
    "DECLINING":         60.0,
    "STABLE":            20.0,
    "IMPROVING":          0.0,
    "INSUFFICIENT_DATA": 30.0,
}

# ---------------------------------------------------------------------------
# Recommendations by risk level
# ---------------------------------------------------------------------------

_BASE_RECOMMENDATIONS: dict[str, list[str]] = {
    "HIGH": [
        "Immediate counselling referral required",
        "Notify Head of Department",
        "Create a structured intervention plan",
    ],
    "MEDIUM": [
        "Schedule a one-on-one check-in with the student",
        "Notify academic mentor",
        "Monitor attendance and marks weekly",
    ],
    "LOW": [
        "Continue regular monitoring",
        "No immediate action required",
    ],
}


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _compute_component_scores(f: FeatureVector) -> dict[str, float]:
    return {
        "attendance":  max(0.0, 100.0 - f.attendance_percentage),
        "marks":       max(0.0, 100.0 - f.internal_marks_average),
        "drop":        min(100.0, f.attendance_drop_percentage * 3.0),
        "decline":     min(100.0, f.marks_decline_percentage * 2.5),
        "consecutive": min(100.0, f.consecutive_absence_count * 12.0),
        "trend":       TREND_SCORE.get(f.performance_trend, 30.0),
        "engagement":  max(0.0, 100.0 - f.engagement_score),
    }


def _weighted_sum(scores: dict[str, float]) -> int:
    raw = (
        scores["attendance"] * WEIGHTS["attendance"]
        + scores["marks"]    * WEIGHTS["marks"]
        + scores["drop"]     * WEIGHTS["drop"]
        + scores["decline"]  * WEIGHTS["decline"]
        + scores["consecutive"] * WEIGHTS["consecutive"]
        + scores["engagement"]  * WEIGHTS["engagement"]
        # trend contributes as a modifier inside engagement weight bucket
        # (see RISK_ENGINE_SPEC.md — trend score replaces engagement when engagement absent)
    )
    return int(round(min(100.0, max(0.0, raw))))


def _score_to_level(score: int) -> str:
    if score < 40:
        return "LOW"
    if score < 70:
        return "MEDIUM"
    return "HIGH"


def _apply_overrides(
    level: str, f: FeatureVector
) -> tuple[str, bool, str | None]:
    """Evaluate override rules in priority order. Only upgrades, never downgrades."""
    if f.has_critical_absence_streak:
        return "HIGH", True, "Consecutive absences >= 7"
    if f.has_critical_low_attendance:
        return "HIGH", True, "Attendance below 50%"
    if f.has_critical_low_marks:
        return "HIGH", True, "Marks average below 35%"
    if f.attendance_drop_percentage > 25.0 and level == "LOW":
        return "MEDIUM", True, "Attendance drop > 25%"
    if f.marks_decline_percentage > 30.0 and level == "LOW":
        return "MEDIUM", True, "Marks decline > 30%"
    if (f.attendance_percentage < 75.0 and f.internal_marks_average < 60.0
            and level == "LOW"):
        return "MEDIUM", True, "Attendance and marks both below threshold"
    return level, False, None


# ---------------------------------------------------------------------------
# Reason generation
# ---------------------------------------------------------------------------

def _generate_reasons(f: FeatureVector, scores: dict[str, float]) -> list[str]:
    candidates: list[tuple[float, str]] = []

    if f.attendance_percentage < 75:
        candidates.append((
            scores["attendance"],
            f"Attendance at {f.attendance_percentage:.0f}% — below the 75% threshold",
        ))
    if f.attendance_drop_percentage > 10:
        candidates.append((
            scores["drop"],
            f"Attendance dropped {f.attendance_drop_percentage:.0f}% recently",
        ))
    if f.internal_marks_average < 60:
        candidates.append((
            scores["marks"],
            f"Average internal marks at {f.internal_marks_average:.0f}% — below the 60% threshold",
        ))
    if f.marks_decline_percentage > 15:
        candidates.append((
            scores["decline"],
            f"Marks declined {f.marks_decline_percentage:.0f}% from recent peak",
        ))
    if f.consecutive_absence_count >= 3:
        candidates.append((
            scores["consecutive"],
            f"{f.consecutive_absence_count} consecutive absences detected",
        ))
    if f.performance_trend == "DECLINING":
        candidates.append((
            scores["trend"],
            "Declining score trend across last 3 assessments",
        ))
    if f.engagement_score < 60:
        candidates.append((
            scores["engagement"],
            f"Engagement score at {f.engagement_score:.0f}% — low participation",
        ))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [reason for _, reason in candidates[:4]]


# ---------------------------------------------------------------------------
# Recommendation generation
# ---------------------------------------------------------------------------

def _generate_recommendations(
    risk_level: str, reasons: list[str]
) -> list[str]:
    base = list(_BASE_RECOMMENDATIONS[risk_level])
    extras: list[str] = []

    combined = " ".join(reasons).lower()
    if "attendance" in combined:
        extras.append("Review attendance records with the student")
    if "marks" in combined or "score" in combined or "decline" in combined:
        extras.append("Provide additional academic support resources")

    all_recs: list[str] = []
    for r in base + extras:
        if r not in all_recs:
            all_recs.append(r)

    return all_recs[:3]


# ---------------------------------------------------------------------------
# Confidence
# ---------------------------------------------------------------------------

def _compute_confidence(metrics: StudentMetrics) -> str:
    missing = sum([
        metrics.assignments_submitted is None,
        len(metrics.assessment_scores) < 3,
        len(metrics.attendance_by_week) < 4,
    ])
    if missing == 0:
        return "high"
    if missing == 1:
        return "moderate"
    return "low"


# ---------------------------------------------------------------------------
# Data loading stub — wired to real DB in backend integration (Task 4)
# ---------------------------------------------------------------------------

def _load_student_metrics(student_id: str) -> StudentMetrics:
    """
    Load raw student data from the DB and return a StudentMetrics object.

    Delegates to backend/app/db.get_student_metrics() which queries the
    attendance and scores tables and builds a StudentMetrics instance.

    Raises StudentNotFoundError if the student does not exist in the DB.
    """
    from vista.backend.app.db import SessionLocal, get_student_metrics

    db = SessionLocal()
    try:
        return get_student_metrics(student_id, db)
    except ValueError as exc:
        raise StudentNotFoundError(str(exc)) from exc
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def calculate_risk_from_metrics(metrics: StudentMetrics) -> dict:
    """
    Rule-based risk scoring from a pre-built StudentMetrics object.
    Use this until DB integration is complete (Task 4).
    """
    if metrics.total_sessions <= 0:
        raise InsufficientDataError(
            f"No sessions recorded for student {metrics.student_id}."
        )

    features = compute_features(metrics)
    component_scores = _compute_component_scores(features)
    risk_score = _weighted_sum(component_scores)
    risk_level = _score_to_level(risk_score)
    risk_level, override_applied, override_reason = _apply_overrides(risk_level, features)

    reasons = _generate_reasons(features, component_scores)
    recommendations = _generate_recommendations(risk_level, reasons)
    confidence = _compute_confidence(metrics)

    return RiskResult(
        student_id=metrics.student_id,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        reasons=reasons,
        recommendations=recommendations,
        computed_at=datetime.now(timezone.utc).isoformat(),
        override_applied=override_applied,
        override_reason=override_reason,
    ).to_dict()


def calculate_risk(student_id: str) -> dict:
    """
    Fixed public entry point consumed by backend/app/routes/risk.py.
    Signature must not change — see vista/CLAUDE.md and docs/API_CONTRACT.md.

    Loads student metrics from DB and returns structured risk result.
    Raises StudentNotFoundError if student does not exist.
    Raises InsufficientDataError if no session data is available.
    """
    metrics = _load_student_metrics(student_id)
    return calculate_risk_from_metrics(metrics)


# ---------------------------------------------------------------------------
# run_pipeline — XGBoost/LR inference from flat dict (README demo entry point)
# ---------------------------------------------------------------------------

_PIPELINE_FEATURES = [
    "overall_attendance",
    "recent_attendance",
    "avg_score",
    "recent_score",
    "failed_subjects",
]

_PIPELINE_LABEL_NAMES = ["LOW", "MEDIUM", "HIGH"]

_PIPELINE_REASONS: dict[str, Any] = {
    "low_attendance": lambda d: d["overall_attendance"] < 75,
    "worsening_attendance": lambda d: d["overall_attendance"] - d["recent_attendance"] > 10,
    "low_marks": lambda d: d["avg_score"] < 60,
    "declining_marks": lambda d: d["avg_score"] - d["recent_score"] > 10,
    "failed_subjects": lambda d: d["failed_subjects"] > 0,
}

_PIPELINE_REASON_TEXT: dict[str, str] = {
    "low_attendance": "Attendance below recommended level",
    "worsening_attendance": "Attendance worsening",
    "low_marks": "Internal marks below passing threshold",
    "declining_marks": "Recent marks declining from average",
    "failed_subjects": "One or more subjects failed",
}

_PIPELINE_ACTIONS: dict[str, list[str]] = {
    "HIGH": [
        "Immediate counselling referral required",
        "Notify Head of Department",
        "Create a structured intervention plan",
    ],
    "MEDIUM": [
        "Schedule attendance counseling session",
        "Monitor student progress weekly",
        "Notify academic mentor",
    ],
    "LOW": [
        "Continue regular monitoring",
        "No immediate action required",
    ],
}


def _load_pipeline_model() -> dict:
    import pickle
    from pathlib import Path

    model_path = Path(__file__).parent / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model not found at {model_path}. "
            "Run: python -m vista.ml.train"
        )
    with model_path.open("rb") as f:
        return pickle.load(f)


def run_pipeline(input_data: dict) -> dict:
    """
    XGBoost/LR inference from a flat student dict.

    Input keys: student_id, overall_attendance, recent_attendance,
                avg_score, recent_score, failed_subjects

    Returns the full pipeline output schema documented in README.md.
    Raises FileNotFoundError if model.pkl has not been trained yet.
    """
    artifact = _load_pipeline_model()
    model = artifact["model"]
    scaler = artifact["scaler"]
    needs_scaling = artifact["needs_scaling"]

    feature_vec = [[input_data.get(f, 0) for f in _PIPELINE_FEATURES]]

    if needs_scaling and scaler is not None:
        feature_vec = scaler.transform(feature_vec)

    # Probability of each class [LOW, MEDIUM, HIGH]
    proba = model.predict_proba(feature_vec)[0]
    high_idx = _PIPELINE_LABEL_NAMES.index("HIGH")
    medium_idx = _PIPELINE_LABEL_NAMES.index("MEDIUM")

    # Aggregate risk score: weighted sum of class probabilities (cast to native float)
    risk_score = round(float(0.0 * proba[0] + 0.5 * proba[medium_idx] + 1.0 * proba[high_idx]), 4)

    if risk_score < 0.4:
        risk_level = "LOW"
    elif risk_score < 0.7:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    confidence = round(abs(risk_score - 0.5) * 2, 4)

    # Determine reasons in priority order
    active_reasons = [
        key for key in _PIPELINE_REASONS
        if _PIPELINE_REASONS[key](input_data)
    ]
    reasons = [
        {"text": _PIPELINE_REASON_TEXT[k], "priority": i + 1}
        for i, k in enumerate(active_reasons[:4])
    ]

    recommended_actions = _PIPELINE_ACTIONS[risk_level][:3]

    # Trend from attendance and score direction
    att_drop = input_data.get("overall_attendance", 0) - input_data.get("recent_attendance", 0)
    sc_drop = input_data.get("avg_score", 0) - input_data.get("recent_score", 0)
    if att_drop > 10 or sc_drop > 10:
        trend = "WORSENING"
    elif att_drop < -5 or sc_drop < -5:
        trend = "IMPROVING"
    else:
        trend = "STABLE"

    # Plain-English summary
    if reasons:
        primary = reasons[0]["text"].lower()
        action = recommended_actions[0].lower() if recommended_actions else "monitor student"
        summary = (
            f"Student is at {risk_level.lower()} risk due to {primary}; {action}."
        )
    else:
        summary = f"Student is at {risk_level.lower()} risk based on current data."

    return {
        "student_id": input_data.get("student_id", ""),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence": confidence,
        "reasons": reasons,
        "recommended_actions": recommended_actions,
        "summary": summary,
        "trend": trend,
        "risk_change": "NO_PREVIOUS_DATA",
        "validation_flags": [],
    }


# ---------------------------------------------------------------------------
# SHAP-enhanced pipeline — Milestone 4
# ---------------------------------------------------------------------------

def run_pipeline_with_shap(input_data: dict) -> dict:
    """
    XGBoost inference with SHAP-based explanations.

    Same input/output as run_pipeline(), but replaces template-based reasons
    with SHAP-generated per-prediction explanations.

    Requires: `shap` library installed.
    Falls back to run_pipeline() if SHAP is unavailable.
    """
    try:
        from .explainer import explain_prediction
    except ImportError:
        # SHAP not installed — fall back to template reasons
        return run_pipeline(input_data)

    # First get the base pipeline result
    base_result = run_pipeline(input_data)

    # Extract feature values in the correct order
    feature_values = [input_data.get(f, 0) for f in _PIPELINE_FEATURES]

    # Get predicted class index
    class_idx = _PIPELINE_LABEL_NAMES.index(base_result["risk_level"])

    # Generate SHAP explanation
    try:
        explanation = explain_prediction(
            feature_values=feature_values,
            predicted_class_idx=class_idx,
            max_reasons=4,
        )

        # Replace template reasons with SHAP reasons
        if explanation["reasons"]:
            base_result["reasons"] = [
                {"text": r, "priority": i + 1, "source": "shap"}
                for i, r in enumerate(explanation["reasons"])
            ]

        # Add SHAP metadata
        base_result["explainability"] = {
            "method": "SHAP_TreeExplainer",
            "shap_values": explanation["shap_values"],
            "base_value": explanation["base_value"],
            "model_confidence": explanation["confidence"],
        }

        # Update summary with SHAP-informed primary reason
        if explanation["reasons"]:
            primary = explanation["reasons"][0].lower()
            action = base_result["recommended_actions"][0].lower() if base_result["recommended_actions"] else "monitor student"
            base_result["summary"] = (
                f"Student is at {base_result['risk_level'].lower()} risk: {primary}. "
                f"Recommended: {action}."
            )

    except Exception as exc:
        # SHAP computation failed — keep template reasons, add error note
        base_result["explainability"] = {
            "method": "template_fallback",
            "error": str(exc),
        }

    return base_result
