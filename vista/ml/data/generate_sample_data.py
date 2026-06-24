"""
Generate synthetic training data for the VISTA risk engine.

Produces 200 student records with features matching the run_pipeline() input schema.
Labels are derived from the rule-based thresholds in risk_engine.py so that the
XGBoost model learns a consistent decision surface.

Usage (from project root):
    python vista/ml/data/generate_sample_data.py
    python -m vista.ml.data.generate_sample_data

Output: vista/ml/data/student_data.csv
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

SEED = 42
N_STUDENTS = 200
OUT_PATH = Path(__file__).parent / "student_data.csv"


def _derive_label(
    overall_attendance: float,
    recent_attendance: float,
    avg_score: float,
    recent_score: float,
    failed_subjects: int,
) -> str:
    """Mirror the rule-based override + threshold logic from risk_engine.py."""
    attendance_drop = overall_attendance - recent_attendance
    score_decline = avg_score - recent_score

    # Override rules → HIGH
    if overall_attendance < 50:
        return "HIGH"
    if avg_score < 35:
        return "HIGH"
    if failed_subjects >= 3:
        return "HIGH"

    # Score-based HIGH
    if overall_attendance < 60 and avg_score < 50:
        return "HIGH"

    # Override rules → MEDIUM from LOW
    if attendance_drop > 25 or score_decline > 20:
        return "MEDIUM"

    # Threshold-based MEDIUM
    if overall_attendance < 75 or avg_score < 60 or failed_subjects >= 1:
        return "MEDIUM"

    # Declining trend pushes borderline cases to MEDIUM
    if recent_attendance < overall_attendance - 10 or recent_score < avg_score - 10:
        return "MEDIUM"

    return "LOW"


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def generate(n: int = N_STUDENTS, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []

    # Target roughly 35% LOW, 40% MEDIUM, 25% HIGH
    profiles = (
        ["low"] * 70
        + ["medium"] * 80
        + ["high"] * 50
    )
    rng.shuffle(profiles)

    for i, profile in enumerate(profiles[:n]):
        student_id = f"S{i+1:03d}"

        if profile == "low":
            overall_att = rng.uniform(78, 98)
            avg_sc = rng.uniform(62, 88)
            att_delta = rng.uniform(-5, 8)        # slight improvement or stable
            sc_delta = rng.uniform(-8, 10)
            failed = 0

        elif profile == "medium":
            overall_att = rng.uniform(60, 80)
            avg_sc = rng.uniform(48, 68)
            att_delta = rng.uniform(-15, 5)       # possible drop
            sc_delta = rng.uniform(-15, 5)
            failed = rng.choice([0, 0, 1, 1, 2])

        else:  # high
            overall_att = rng.uniform(35, 65)
            avg_sc = rng.uniform(25, 55)
            att_delta = rng.uniform(-25, -5)      # worsening
            sc_delta = rng.uniform(-25, -5)
            failed = rng.choice([1, 2, 2, 3, 4])

        recent_att = _clamp(overall_att - att_delta, 0, 100)
        recent_sc = _clamp(avg_sc - sc_delta, 0, 100)

        # Add small noise so samples aren't perfectly clustered
        overall_att = _clamp(overall_att + rng.gauss(0, 2), 0, 100)
        avg_sc = _clamp(avg_sc + rng.gauss(0, 2), 0, 100)
        recent_att = _clamp(recent_att + rng.gauss(0, 2), 0, 100)
        recent_sc = _clamp(recent_sc + rng.gauss(0, 2), 0, 100)

        label = _derive_label(overall_att, recent_att, avg_sc, recent_sc, failed)

        rows.append({
            "student_id": student_id,
            "overall_attendance": round(overall_att, 2),
            "recent_attendance": round(recent_att, 2),
            "avg_score": round(avg_sc, 2),
            "recent_score": round(recent_sc, 2),
            "failed_subjects": failed,
            "risk_label": label,
        })

    return rows


def save(rows: list[dict], path: Path = OUT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "student_id", "overall_attendance", "recent_attendance",
        "avg_score", "recent_score", "failed_subjects", "risk_label",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = generate()
    save(rows)

    label_counts: dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for r in rows:
        label_counts[r["risk_label"]] += 1

    print(f"Generated {len(rows)} student records -> {OUT_PATH}")
    print("Label distribution:")
    for level, count in label_counts.items():
        print(f"  {level:6s}: {count:3d}  ({count/len(rows)*100:.1f}%)")


if __name__ == "__main__":
    main()
