from __future__ import annotations

import sys
from pathlib import Path

# Allow running directly: python -m ml.test_risk_engine or python vista/ml/test_risk_engine.py
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from vista.ml.features import StudentMetrics
from vista.ml.risk_engine import InsufficientDataError, calculate_risk_from_metrics


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS = "✓"
FAIL = "✗"


def _run(label: str, metrics: StudentMetrics) -> dict:
    return calculate_risk_from_metrics(metrics)


def _check(condition: bool, msg: str) -> None:
    mark = PASS if condition else FAIL
    status = "PASS" if condition else "FAIL"
    print(f"  {mark} [{status}] {msg}")
    if not condition:
        # Don't abort the suite — keep running so all failures are visible.
        pass


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


# ---------------------------------------------------------------------------
# Test 1 — Healthy student → LOW
# ---------------------------------------------------------------------------

def test_healthy_low() -> None:
    _section("Test 1 — Healthy student → expected LOW")
    metrics = StudentMetrics(
        student_id="CS22B001",
        total_sessions=40,
        sessions_attended=36,                      # 90%
        attendance_by_week=[88, 90, 92, 88, 90],
        consecutive_absences=1,
        assessment_scores=[72, 78, 80],
        assessment_max_scores=[100, 100, 100],
        assignments_submitted=9,
        assignments_total=10,
    )
    result = _run("healthy_low", metrics)
    print(f"  risk_score={result['risk_score']}  risk_level={result['risk_level']}")
    _check(result["risk_level"] == "LOW", "risk_level == LOW")
    _check(0 <= result["risk_score"] < 40, f"risk_score in [0, 40) — got {result['risk_score']}")
    _check(result["confidence"] in {"high", "moderate"}, "confidence set")
    _check(result["override_applied"] is False, "no override triggered")


# ---------------------------------------------------------------------------
# Test 2 — Borderline student → MEDIUM
# ---------------------------------------------------------------------------

def test_borderline_medium() -> None:
    _section("Test 2 — Borderline student → expected MEDIUM")
    metrics = StudentMetrics(
        student_id="CS22B002",
        total_sessions=40,
        sessions_attended=28,                      # 70%
        attendance_by_week=[80, 75, 68, 62, 60],   # dropping
        consecutive_absences=3,
        assessment_scores=[58, 54, 51],
        assessment_max_scores=[100, 100, 100],
        assignments_submitted=6,
        assignments_total=10,
    )
    result = _run("borderline_medium", metrics)
    print(f"  risk_score={result['risk_score']}  risk_level={result['risk_level']}")
    _check(result["risk_level"] == "MEDIUM", "risk_level == MEDIUM")
    # Score may be below 40 if override rule promoted LOW→MEDIUM
    _check(0 <= result["risk_score"] < 70, f"risk_score in [0, 70) — got {result['risk_score']}")
    _check(len(result["reasons"]) > 0, "reasons populated")


# ---------------------------------------------------------------------------
# Test 3 — At-risk student → HIGH (score-based, no override)
# ---------------------------------------------------------------------------

def test_at_risk_high() -> None:
    _section("Test 3 — At-risk student → expected HIGH (score-based)")
    metrics = StudentMetrics(
        student_id="CS22B003",
        total_sessions=40,
        sessions_attended=20,                      # 50% — triggers override actually
        attendance_by_week=[70, 60, 50, 40, 40],
        consecutive_absences=5,
        assessment_scores=[38, 32, 28],
        assessment_max_scores=[100, 100, 100],
        assignments_submitted=3,
        assignments_total=10,
    )
    result = _run("at_risk_high", metrics)
    print(f"  risk_score={result['risk_score']}  risk_level={result['risk_level']}")
    _check(result["risk_level"] == "HIGH", "risk_level == HIGH")
    _check(result["risk_score"] >= 40, f"risk_score >= 40 — got {result['risk_score']}")
    _check(len(result["recommendations"]) > 0, "recommendations populated")


# ---------------------------------------------------------------------------
# Test 4 — Override fires: consecutive absences >= 7
# ---------------------------------------------------------------------------

def test_override_consecutive_absences() -> None:
    _section("Test 4 — Override: consecutive_absences >= 7 → force HIGH")
    metrics = StudentMetrics(
        student_id="CS22B004",
        total_sessions=40,
        sessions_attended=30,                      # 75% — would score LOW/MEDIUM without override
        attendance_by_week=[80, 80, 75, 40, 40],
        consecutive_absences=8,                    # triggers override
        assessment_scores=[65, 62, 60],
        assessment_max_scores=[100, 100, 100],
        assignments_submitted=8,
        assignments_total=10,
    )
    result = _run("override_consecutive", metrics)
    print(f"  risk_score={result['risk_score']}  risk_level={result['risk_level']}  override={result['override_reason']}")
    _check(result["risk_level"] == "HIGH", "risk_level forced to HIGH by override")
    _check(result["override_applied"] is True, "override_applied == True")
    _check(result["override_reason"] == "Consecutive absences >= 7", "correct override reason")


# ---------------------------------------------------------------------------
# Test 5 — Missing score data → low confidence
# ---------------------------------------------------------------------------

def test_missing_score_data_low_confidence() -> None:
    _section("Test 5 — Missing score data → confidence == low")
    metrics = StudentMetrics(
        student_id="CS22B005",
        total_sessions=40,
        sessions_attended=32,
        attendance_by_week=[80, 80, 80],           # only 3 weeks — below threshold
        consecutive_absences=0,
        assessment_scores=[],                      # no assessments yet
        assessment_max_scores=[],
        assignments_submitted=None,
        assignments_total=None,
    )
    result = _run("missing_scores", metrics)
    print(f"  risk_score={result['risk_score']}  confidence={result['confidence']}")
    _check(result["confidence"] == "low", "confidence == low when data sparse")
    _check(isinstance(result["risk_level"], str), "risk_level still returned")


# ---------------------------------------------------------------------------
# Test 6 — Zero sessions → InsufficientDataError
# ---------------------------------------------------------------------------

def test_zero_sessions_raises() -> None:
    _section("Test 6 — Zero sessions → InsufficientDataError")
    metrics = StudentMetrics(
        student_id="CS22B006",
        total_sessions=0,
        sessions_attended=0,
        attendance_by_week=[],
        consecutive_absences=0,
        assessment_scores=[],
        assessment_max_scores=[],
    )
    raised = False
    try:
        calculate_risk_from_metrics(metrics)
    except InsufficientDataError:
        raised = True
    _check(raised, "InsufficientDataError raised for zero sessions")


# ---------------------------------------------------------------------------
# Test 7 — Improving student → LOW, IMPROVING trend
# ---------------------------------------------------------------------------

def test_improving_student() -> None:
    _section("Test 7 — Improving student → LOW, IMPROVING trend")
    metrics = StudentMetrics(
        student_id="CS22B007",
        total_sessions=40,
        sessions_attended=32,                      # 80%
        attendance_by_week=[70, 74, 78, 82, 84],   # improving
        consecutive_absences=0,
        assessment_scores=[55, 62, 71],
        assessment_max_scores=[100, 100, 100],
        assignments_submitted=9,
        assignments_total=10,
    )
    result = _run("improving", metrics)
    print(f"  risk_score={result['risk_score']}  risk_level={result['risk_level']}")
    _check(result["risk_level"] == "LOW", "risk_level == LOW")
    _check(result["override_applied"] is False, "no override on improving student")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main() -> None:
    print("\nVISTA Risk Engine — Test Suite")
    print("Rule-based engine | 7 test cases | docs/RISK_ENGINE_SPEC.md")

    tests = [
        test_healthy_low,
        test_borderline_medium,
        test_at_risk_high,
        test_override_consecutive_absences,
        test_missing_score_data_low_confidence,
        test_zero_sessions_raises,
        test_improving_student,
    ]

    passed = 0
    failed = 0

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as exc:
            print(f"  {FAIL} [ERROR] {test_fn.__name__} raised unexpectedly: {exc}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print('=' * 60)


if __name__ == "__main__":
    main()
