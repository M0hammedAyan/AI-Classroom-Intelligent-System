from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DATA_PATH = PROJECT_ROOT / "ml" / "data" / "sample" / "student_data.csv"
DEFAULT_TEST_COUNT = 5
LOW_RISK_ATTENDANCE_THRESHOLD = 85.0
LOW_RISK_SCORE_THRESHOLD = 75.0
HIGH_RISK_ATTENDANCE_THRESHOLD = 60.0
HIGH_RISK_SCORE_THRESHOLD = 40.0


try:
    from ml.src.pipeline.pipeline import run_pipeline
except ModuleNotFoundError:
    import sys

    sys.path.append(str(PROJECT_ROOT))
    from ml.src.pipeline.pipeline import run_pipeline


def load_sample_data(path: Path) -> pd.DataFrame:
    """Load sample dataset used for pipeline testing."""
    return pd.read_csv(path)


def _profile_expectation(row: pd.Series) -> str:
    high_attendance_and_marks = (
        row["overall_attendance"] >= LOW_RISK_ATTENDANCE_THRESHOLD
        and row["avg_score"] >= LOW_RISK_SCORE_THRESHOLD
    )
    low_attendance_and_marks = (
        row["overall_attendance"] <= HIGH_RISK_ATTENDANCE_THRESHOLD
        and row["avg_score"] <= HIGH_RISK_SCORE_THRESHOLD
    )

    if high_attendance_and_marks:
        return "EXPECTED_LOW"
    if low_attendance_and_marks:
        return "EXPECTED_HIGH"
    return "EXPECTED_MEDIUM"


def select_test_students(df: pd.DataFrame, count: int = DEFAULT_TEST_COUNT) -> pd.DataFrame:
    """Select test rows without hardcoded IDs, ensuring strong and weak profiles are included."""
    if df.empty:
        raise ValueError("Sample dataset is empty.")

    working_df = df.copy()
    working_df["quality_score"] = (
        0.5 * working_df["overall_attendance"]
        + 0.5 * working_df["avg_score"]
        - 5.0 * working_df["failed_subjects"]
    )

    expected_low_df = working_df[
        (working_df["overall_attendance"] >= LOW_RISK_ATTENDANCE_THRESHOLD)
        & (working_df["avg_score"] >= LOW_RISK_SCORE_THRESHOLD)
    ]
    expected_high_df = working_df[
        (working_df["overall_attendance"] <= HIGH_RISK_ATTENDANCE_THRESHOLD)
        & (working_df["avg_score"] <= HIGH_RISK_SCORE_THRESHOLD)
    ]

    selected_indices: List[int] = []

    if not expected_low_df.empty:
        selected_indices.append(int(expected_low_df["quality_score"].idxmax()))

    if not expected_high_df.empty:
        selected_indices.append(int(expected_high_df["quality_score"].idxmin()))
    else:
        # Build a data-driven weak-profile fallback if no row satisfies strict expected-high thresholds.
        base_row = working_df.loc[int(working_df["quality_score"].idxmin())]
        fallback_row: Dict[str, Any] = {str(k): v for k, v in base_row.to_dict().items()}
        fallback_row["student_id"] = f"{fallback_row['student_id']}_WEAK"
        fallback_row["overall_attendance"] = min(
            float(working_df["overall_attendance"].min()),
            HIGH_RISK_ATTENDANCE_THRESHOLD,
        )
        fallback_row["recent_attendance"] = min(
            float(working_df["recent_attendance"].min()),
            HIGH_RISK_ATTENDANCE_THRESHOLD,
        )
        fallback_row["avg_score"] = min(float(working_df["avg_score"].min()), HIGH_RISK_SCORE_THRESHOLD)
        fallback_row["recent_score"] = min(
            float(working_df["recent_score"].min()),
            HIGH_RISK_SCORE_THRESHOLD,
        )
        fallback_row["failed_subjects"] = int(working_df["failed_subjects"].max())
        fallback_row["label"] = 1
        working_df = pd.concat([working_df, pd.DataFrame([fallback_row])], ignore_index=True)
        selected_indices.append(int(working_df.index.max()))

    best_idx = int(working_df["quality_score"].idxmax())
    worst_idx = int(working_df["quality_score"].idxmin())
    selected_indices.extend([best_idx, worst_idx])
    selected_indices = list(dict.fromkeys(selected_indices))

    remaining_df = working_df.drop(index=selected_indices)
    needed = max(0, count - len(selected_indices))

    if needed > 0 and not remaining_df.empty:
        sample_count = min(needed, len(remaining_df))
        sampled_df = remaining_df.sample(n=sample_count, random_state=42)
        selected_indices.extend(sampled_df.index.tolist())

    selected_df = working_df.loc[selected_indices].drop(columns=["quality_score"]).reset_index(drop=True)
    return selected_df.head(count)


def run_pipeline_for_students(students_df: pd.DataFrame) -> List[Dict[str, object]]:
    """Run risk pipeline for each selected student and capture concise test outputs."""
    outputs: List[Dict[str, object]] = []

    for _, row in students_df.iterrows():
        student_input = row.drop(labels=["label"], errors="ignore").to_dict()
        result = run_pipeline(student_input)

        outputs.append(
            {
                "student_id": str(student_input["student_id"]),
                "overall_attendance": float(student_input["overall_attendance"]),
                "avg_score": float(student_input["avg_score"]),
                "failed_subjects": int(student_input["failed_subjects"]),
                "expected_case": _profile_expectation(row),
                "predicted_risk": str(result["risk_level"]),
                "risk_score": float(result["risk_score"]),
                "trend": str(result["trend"]),
            }
        )

    return outputs


def _to_float(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float, str, np.integer, np.floating)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    return default


def print_test_results(results: List[Dict[str, object]]) -> None:
    """Print clean, readable test output for quick validation."""
    if not results:
        print("No test results to display.")
        return

    print("Pipeline Test Results (5 Students)")
    print("-" * 112)
    print(
        f"{'STUDENT':<10} {'ATTEND':>8} {'AVG_SCORE':>10} {'FAILED':>8} "
        f"{'CASE':>16} {'PRED_RISK':>10} {'RISK_SCORE':>11} {'TREND':>12}"
    )
    print("-" * 112)

    for item in results:
        print(
            f"{item['student_id']:<10} "
            f"{item['overall_attendance']:>8.2f} "
            f"{item['avg_score']:>10.2f} "
            f"{item['failed_subjects']:>8d} "
            f"{item['expected_case']:>16} "
            f"{item['predicted_risk']:>10} "
            f"{item['risk_score']:>11.4f} "
            f"{item['trend']:>12}"
        )

    risk_scores = np.array([
        _to_float(item.get("risk_score", 0.0))
        for item in results
        if isinstance(item, dict)
    ], dtype=float)

    print("-" * 112)
    print(
        "Predicted probability distribution: "
        f"min={risk_scores.min():.4f}, max={risk_scores.max():.4f}, mean={risk_scores.mean():.4f}"
    )
    print("Case key: EXPECTED_LOW = high attendance + good marks, EXPECTED_HIGH = low attendance + poor marks")


def main() -> None:
    data_df = load_sample_data(SAMPLE_DATA_PATH)
    test_students_df = select_test_students(data_df, count=DEFAULT_TEST_COUNT)
    results = run_pipeline_for_students(test_students_df)
    print_test_results(results)


if __name__ == "__main__":
    main()
