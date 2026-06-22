"""
UCI Student Performance Dataset — Feature Pipeline Validator
============================================================
Downloads: https://archive.ics.uci.edu/ml/datasets/student+performance
           student-mat.csv (Math) or student-por.csv (Portuguese)

Usage (from vista/ root):
    python -m ml.validate_uci --file path/to/student-mat.csv

What this script does:
  1. Maps UCI columns → StudentMetrics
  2. Runs compute_features() on every student
  3. Runs calculate_risk_from_metrics() on every student
  4. Compares predicted risk level against actual pass/fail (G3 >= 10)
  5. Prints a confusion-style summary and sanity checks

This is a sanity check for the rule-based engine against known outcomes,
NOT a training step. See docs/DATASET_ANALYSIS.md for context.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow: python -m ml.validate_uci  OR  python vista/ml/validate_uci.py
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import pandas as pd
except ImportError:
    print("pandas is required: pip install pandas")
    sys.exit(1)

from vista.ml.features import StudentMetrics, compute_features
from vista.ml.risk_engine import InsufficientDataError, calculate_risk_from_metrics

# ---------------------------------------------------------------------------
# UCI column mapping
# ---------------------------------------------------------------------------
# UCI absences: count (0–93). We approximate attendance_percentage by assuming
# a 40-session semester and capping absences at 40.
UCI_TOTAL_SESSIONS = 40
UCI_PASS_THRESHOLD = 10      # G3 >= 10 = pass
UCI_ATTENDANCE_CAP = 40      # absences capped to total sessions


def _uci_row_to_metrics(row: "pd.Series", idx: int) -> StudentMetrics:
    absences = min(int(row.get("absences", 0)), UCI_ATTENDANCE_CAP)
    sessions_attended = max(0, UCI_TOTAL_SESSIONS - absences)

    # G1, G2, G3 are on 0–20 scale — normalise to 0–100
    raw_scores = []
    raw_max = []
    for col in ["G1", "G2", "G3"]:
        if col in row.index and pd.notna(row[col]):
            raw_scores.append(float(row[col]))
            raw_max.append(20.0)

    # Approximate weekly attendance from absence count spread over 8 weeks
    weekly_absences = absences / 8.0
    weekly_att = max(0.0, ((UCI_TOTAL_SESSIONS / 8.0) - weekly_absences)
                     / (UCI_TOTAL_SESSIONS / 8.0) * 100.0)
    attendance_by_week = [weekly_att] * 8

    # Consecutive absences: UCI has no streak data — proxy as absences // 3
    consec = min(absences // 3, 10)

    return StudentMetrics(
        student_id=f"UCI_{idx:04d}",
        total_sessions=UCI_TOTAL_SESSIONS,
        sessions_attended=sessions_attended,
        attendance_by_week=attendance_by_week,
        consecutive_absences=consec,
        assessment_scores=raw_scores,
        assessment_max_scores=raw_max,
        assignments_submitted=None,
        assignments_total=None,
    )


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def _actual_outcome(row: "pd.Series") -> str:
    """HIGH_RISK if failed (G3 < 10), LOW_RISK if passed."""
    g3 = float(row.get("G3", 10))
    return "HIGH_RISK" if g3 < UCI_PASS_THRESHOLD else "LOW_RISK"


def validate(csv_path: Path) -> None:
    print(f"\nLoading UCI dataset from: {csv_path}")

    try:
        # UCI file uses semicolon separator
        df = pd.read_csv(csv_path, sep=";")
    except Exception as exc:
        print(f"Failed to read file: {exc}")
        sys.exit(1)

    required = {"G3", "absences"}
    missing = required - set(df.columns)
    if missing:
        print(f"Missing required UCI columns: {missing}")
        print("Make sure you're using student-mat.csv or student-por.csv from UCI.")
        sys.exit(1)

    print(f"Loaded {len(df)} students.\n")

    results = []
    errors = 0

    for idx, row in df.iterrows():
        try:
            metrics = _uci_row_to_metrics(row, int(str(idx)))
            result = calculate_risk_from_metrics(metrics)
            actual = _actual_outcome(row)
            predicted_high = result["risk_level"] == "HIGH"
            actual_high = actual == "HIGH_RISK"
            results.append({
                "student_id": metrics.student_id,
                "predicted": result["risk_level"],
                "predicted_high": predicted_high,
                "actual_high": actual_high,
                "risk_score": result["risk_score"],
                "g3": float(row.get("G3", 0)),
                "absences": int(row.get("absences", 0)),
            })
        except InsufficientDataError:
            errors += 1
        except Exception as exc:
            print(f"  Row {idx} error: {exc}")
            errors += 1

    if not results:
        print("No results — check the dataset format.")
        return

    # ---------------------------------------------------------------------------
    # Summary statistics
    # ---------------------------------------------------------------------------
    total = len(results)
    actual_fail = sum(1 for r in results if r["actual_high"])
    actual_pass = total - actual_fail

    tp = sum(1 for r in results if r["predicted_high"] and r["actual_high"])
    tn = sum(1 for r in results if not r["predicted_high"] and not r["actual_high"])
    fp = sum(1 for r in results if r["predicted_high"] and not r["actual_high"])
    fn = sum(1 for r in results if not r["predicted_high"] and r["actual_high"])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    accuracy  = (tp + tn) / total if total > 0 else 0.0

    print("=" * 55)
    print("  UCI Validation Summary")
    print("=" * 55)
    print(f"  Total students        : {total}")
    print(f"  Actual failures (G3<10): {actual_fail}  ({actual_fail/total*100:.1f}%)")
    print(f"  Actual passes          : {actual_pass}  ({actual_pass/total*100:.1f}%)")
    print(f"  Errors / skipped       : {errors}")
    print()
    print("  Confusion matrix (HIGH predicted vs actual fail):")
    print(f"    True  Positives : {tp}   (flagged HIGH, actually failed)")
    print(f"    True  Negatives : {tn}   (not HIGH, actually passed)")
    print(f"    False Positives : {fp}   (flagged HIGH, but passed)")
    print(f"    False Negatives : {fn}   (not HIGH, but failed)")
    print()
    print(f"  Precision : {precision:.3f}")
    print(f"  Recall    : {recall:.3f}   ← most important: are we catching failures?")
    print(f"  F1 score  : {f1:.3f}")
    print(f"  Accuracy  : {accuracy:.3f}")
    print("=" * 55)

    # ---------------------------------------------------------------------------
    # Risk distribution
    # ---------------------------------------------------------------------------
    low    = sum(1 for r in results if r["predicted"] == "LOW")
    medium = sum(1 for r in results if r["predicted"] == "MEDIUM")
    high   = sum(1 for r in results if r["predicted"] == "HIGH")

    print("\n  Predicted risk distribution:")
    print(f"    LOW    : {low}  ({low/total*100:.1f}%)")
    print(f"    MEDIUM : {medium}  ({medium/total*100:.1f}%)")
    print(f"    HIGH   : {high}  ({high/total*100:.1f}%)")

    # ---------------------------------------------------------------------------
    # Sanity checks
    # ---------------------------------------------------------------------------
    print("\n  Sanity checks:")
    checks = [
        (recall >= 0.50,
         f"Recall >= 0.50 — catching at least half of actual failures ({recall:.2f})"),
        (precision >= 0.40,
         f"Precision >= 0.40 — flagged students are mostly real risk ({precision:.2f})"),
        (high / total <= 0.60,
         f"HIGH rate <= 60% — engine is not over-flagging ({high/total*100:.1f}%)"),
        (low / total >= 0.20,
         f"LOW rate >= 20% — engine is discriminating ({low/total*100:.1f}%)"),
    ]
    for passed, msg in checks:
        mark = "✓" if passed else "✗"
        print(f"    {mark} {msg}")

    print()
    print("  Note: UCI is Portuguese secondary school data — not Indian college context.")
    print("  These numbers validate pipeline logic, not production accuracy.")
    print("  See docs/DATASET_ANALYSIS.md for interpretation guidance.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate VISTA risk engine against UCI Student Performance dataset."
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to student-mat.csv or student-por.csv from UCI",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"File not found: {args.file}")
        print("Download from: https://archive.ics.uci.edu/ml/datasets/student+performance")
        sys.exit(1)

    validate(args.file)


if __name__ == "__main__":
    main()
