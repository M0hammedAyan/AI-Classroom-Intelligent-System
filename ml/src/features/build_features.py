from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_PATH = Path("ml/data/sample/student_data.csv")
DEFAULT_TIME_GAP_DAYS = 30.0
RECENT_SCORE_WEIGHT = 0.7
STREAK_WEIGHT_1 = 0.7
STREAK_WEIGHT_2 = 0.3
MAX_CONSECUTIVE_ABSENCES = 10.0
MAX_ATTENDANCE_DROP = 100.0


REQUIRED_COLUMNS = [
    "student_id",
    "overall_attendance",
    "recent_attendance",
    "avg_score",
    "recent_score",
    "failed_subjects",
    "label",
]


def load_dataset(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Load raw student dataset from CSV."""
    return pd.read_csv(path)


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()

    # Keep student_id as string and replace missing IDs with a placeholder.
    clean_df["student_id"] = clean_df["student_id"].astype("string").fillna("UNKNOWN")

    numeric_columns = [
        "overall_attendance",
        "recent_attendance",
        "avg_score",
        "recent_score",
        "failed_subjects",
        "label",
    ]

    for column in numeric_columns:
        clean_df[column] = pd.to_numeric(clean_df[column], errors="coerce")
        if clean_df[column].isna().any():
            clean_df[column] = clean_df[column].fillna(clean_df[column].median())

    clean_df["failed_subjects"] = clean_df["failed_subjects"].round().clip(0, 5).astype(int)
    clean_df["label"] = clean_df["label"].round().clip(0, 1).astype(int)

    return clean_df


def _create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    features_df = df.copy()

    # Positive attendance_drop means recent attendance is worse than long-term attendance.
    features_df["attendance_drop"] = (
        features_df["overall_attendance"] - features_df["recent_attendance"]
    )
    features_df["score_trend"] = features_df["recent_score"] - features_df["avg_score"]

    features_df["low_attendance_flag"] = (features_df["overall_attendance"] < 75).astype(int)
    features_df["declining_performance_flag"] = (features_df["score_trend"] < 0).astype(int)
    features_df["high_failure_flag"] = (features_df["failed_subjects"] >= 2).astype(int)

    attendance_risk_component = 1.0 - (features_df["overall_attendance"] / 100.0)
    score_risk_component = 1.0 - (features_df["avg_score"] / 100.0)
    failed_subjects_component = features_df["failed_subjects"] / 5.0

    features_df["risk_score_manual"] = (
        0.4 * attendance_risk_component
        + 0.4 * score_risk_component
        + 0.2 * failed_subjects_component
    )
    features_df["risk_score_manual"] = features_df["risk_score_manual"].clip(0.0, 1.0)

    features_df["severe_risk_flag"] = (
        (features_df["overall_attendance"] < 50) & (features_df["avg_score"] < 35)
    ).astype(int)
    features_df["improvement_flag"] = (features_df["score_trend"] > 5).astype(int)
    features_df["attendance_score_interaction"] = (
        features_df["overall_attendance"] * features_df["avg_score"]
    )

    safe_overall_attendance = features_df["overall_attendance"].replace(0, 1e-6)
    features_df["recent_vs_past_attendance_ratio"] = (
        features_df["recent_attendance"] / safe_overall_attendance
    )

    default_gap_series = pd.Series(DEFAULT_TIME_GAP_DAYS, index=features_df.index, dtype=float)

    if "time_gap_days" in features_df.columns:
        provided_gap = pd.to_numeric(features_df["time_gap_days"], errors="coerce")
        default_gap_series = provided_gap.where(provided_gap > 0, default_gap_series)

    date_pairs = [
        ("recent_score_date", "past_score_date"),
        ("recent_score_date", "avg_score_date"),
        ("recent_attendance_date", "overall_attendance_date"),
        ("recent_date", "past_date"),
    ]

    for recent_col, past_col in date_pairs:
        if recent_col in features_df.columns and past_col in features_df.columns:
            recent_dt = pd.to_datetime(features_df[recent_col], errors="coerce")
            past_dt = pd.to_datetime(features_df[past_col], errors="coerce")
            inferred_gap = (recent_dt - past_dt).dt.days.abs().astype(float)
            valid_gap = inferred_gap.where(inferred_gap > 0)
            default_gap_series = valid_gap.fillna(default_gap_series)

    features_df["time_gap_days"] = default_gap_series.clip(lower=1.0)
    features_df["score_velocity"] = features_df["score_trend"] / features_df["time_gap_days"]
    features_df["performance_drop_flag"] = (features_df["score_trend"] < -10).astype(int)

    features_df["borderline_flag"] = (
        features_df["overall_attendance"].between(60, 75, inclusive="both")
        & features_df["avg_score"].between(40, 60, inclusive="both")
    ).astype(int)

    if "consecutive_absences" in features_df.columns:
        consecutive_absences = pd.to_numeric(features_df["consecutive_absences"], errors="coerce").fillna(0.0)
    else:
        # Fallback proxy when streak history is unavailable.
        consecutive_absences = (
            ((100.0 - features_df["recent_attendance"]).clip(lower=0.0) / 12.0)
            + (features_df["failed_subjects"] * 0.5)
        )

    consecutive_absences = consecutive_absences.clip(lower=0.0, upper=MAX_CONSECUTIVE_ABSENCES)
    attendance_drop_positive = features_df["attendance_drop"].clip(lower=0.0, upper=MAX_ATTENDANCE_DROP)

    raw_streak_impact = (
        (consecutive_absences.pow(2) * STREAK_WEIGHT_1)
        + (attendance_drop_positive * STREAK_WEIGHT_2)
    )
    max_raw_streak_impact = (
        (MAX_CONSECUTIVE_ABSENCES**2) * STREAK_WEIGHT_1
        + MAX_ATTENDANCE_DROP * STREAK_WEIGHT_2
    )
    features_df["attendance_streak_impact"] = (raw_streak_impact / max_raw_streak_impact).clip(
        lower=0.0,
        upper=1.0,
    )

    features_df["weighted_recent_score"] = (
        RECENT_SCORE_WEIGHT * features_df["recent_score"]
        + (1.0 - RECENT_SCORE_WEIGHT) * features_df["avg_score"]
    )

    return features_df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a clean, model-ready DataFrame with derived risk features."""
    _validate_columns(df)
    clean_df = _handle_missing_values(df)
    return _create_derived_features(clean_df)


def load_and_build_features(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Convenience helper to load CSV from disk and build features."""
    raw_df = load_dataset(path)
    return build_features(raw_df)


if __name__ == "__main__":
    output_df = load_and_build_features()
    print(output_df.head())
