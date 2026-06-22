from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Input schema
# ---------------------------------------------------------------------------

@dataclass
class StudentMetrics:
    student_id: str

    # Attendance
    total_sessions: int
    sessions_attended: int
    attendance_by_week: list[float]       # weekly attendance %, chronological
    consecutive_absences: int

    # Scores — raw values, chronological; paired 1:1 with assessment_max_scores
    assessment_scores: list[float]
    assessment_max_scores: list[float]

    # Assignments — None if not tracked this semester
    assignments_submitted: int | None = None
    assignments_total: int | None = None

    observation_window_days: int = 90


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

@dataclass
class FeatureVector:
    student_id: str

    attendance_percentage: float           # 0–100
    attendance_drop_percentage: float      # positive = worsening, negative = improving
    internal_marks_average: float          # 0–100, normalised
    marks_decline_percentage: float        # 0–100, clamped at 0 (no negative decline)
    assignment_completion_rate: float | None  # 0–100, None if data unavailable
    consecutive_absence_count: int
    performance_trend: str                 # "IMPROVING" | "STABLE" | "DECLINING" | "INSUFFICIENT_DATA"
    engagement_score: float                # 0–100

    # Flags used by override rules in risk_engine.py
    has_critical_absence_streak: bool      # consecutive_absence_count >= 7
    has_critical_low_attendance: bool      # attendance_percentage < 50
    has_critical_low_marks: bool           # internal_marks_average < 35


# ---------------------------------------------------------------------------
# Individual feature functions
# ---------------------------------------------------------------------------

def compute_attendance_percentage(
    sessions_attended: int,
    total_sessions: int,
) -> float:
    """Percentage of sessions attended out of total sessions held."""
    if total_sessions <= 0:
        return 0.0
    return round((sessions_attended / total_sessions) * 100.0, 2)


def compute_attendance_drop(attendance_by_week: list[float]) -> float:
    """
    Difference between first-half and second-half mean weekly attendance.
    Positive value means attendance is getting worse.
    Returns 0.0 when fewer than 2 data points are available.
    """
    if len(attendance_by_week) < 2:
        return 0.0

    mid = len(attendance_by_week) // 2
    first_half = attendance_by_week[:mid]
    second_half = attendance_by_week[mid:]

    first_mean = sum(first_half) / len(first_half)
    second_mean = sum(second_half) / len(second_half)

    return round(first_mean - second_mean, 2)


def compute_marks_average(
    scores: list[float],
    max_scores: list[float],
) -> float:
    """
    Mean of per-assessment normalised scores (0–100).
    Assessments with max_score <= 0 are skipped to avoid division by zero.
    Returns 0.0 when no valid assessments exist.
    """
    if not scores or not max_scores:
        return 0.0

    normalised = [
        (s / m) * 100.0
        for s, m in zip(scores, max_scores)
        if m > 0
    ]
    if not normalised:
        return 0.0
    return round(sum(normalised) / len(normalised), 2)


def compute_marks_decline(
    scores: list[float],
    max_scores: list[float],
) -> float:
    """
    Percentage fall from the peak of the last 3 normalised scores to the latest score.
    Clamped at 0 — improvement (negative decline) is reported as 0.
    Returns 0.0 when fewer than 2 assessments exist.
    """
    if len(scores) < 2 or not max_scores:
        return 0.0

    recent_raw = list(zip(scores, max_scores))[-3:]
    normalised = [(s / m) * 100.0 for s, m in recent_raw if m > 0]

    if len(normalised) < 2:
        return 0.0

    peak = max(normalised)
    latest = normalised[-1]

    if peak <= 0:
        return 0.0

    decline = ((peak - latest) / peak) * 100.0
    return round(max(0.0, decline), 2)


def compute_assignment_completion(
    submitted: int | None,
    total: int | None,
) -> float | None:
    """
    Percentage of issued assignments submitted.
    Returns None when assignment data is not available.
    """
    if submitted is None or total is None:
        return None
    if total <= 0:
        return None
    return round((submitted / total) * 100.0, 2)


def compute_consecutive_absences(attendance_sequence: list[str]) -> int:
    """
    Longest unbroken streak of absent/liveness_failed sessions.
    attendance_sequence is a chronological list of status strings.
    """
    max_streak = 0
    current = 0
    for status in attendance_sequence:
        if status in {"absent", "liveness_failed"}:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0
    return max_streak


def compute_performance_trend(
    scores: list[float],
    max_scores: list[float],
) -> str:
    """
    Direction of score change across the last 3 assessments.
    Returns IMPROVING / STABLE / DECLINING / INSUFFICIENT_DATA.
    +/- 5 point threshold prevents noise-driven flips.
    """
    if len(scores) < 2 or not max_scores:
        return "INSUFFICIENT_DATA"

    recent_raw = list(zip(scores, max_scores))[-3:]
    normalised = [(s / m) * 100.0 for s, m in recent_raw if m > 0]

    if len(normalised) < 2:
        return "INSUFFICIENT_DATA"

    delta = normalised[-1] - normalised[0]
    if delta > 5.0:
        return "IMPROVING"
    if delta < -5.0:
        return "DECLINING"
    return "STABLE"


def compute_engagement_score(
    attendance_pct: float,
    completion_rate: float | None,
) -> float:
    """
    Composite of attendance regularity (60%) and assignment completion (40%).
    When completion data is unavailable, uses attendance only.
    """
    att = max(0.0, min(100.0, attendance_pct)) / 100.0

    if completion_rate is None:
        return round(att * 100.0, 2)

    comp = max(0.0, min(100.0, completion_rate)) / 100.0
    return round((0.6 * att + 0.4 * comp) * 100.0, 2)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def compute_features(metrics: StudentMetrics) -> FeatureVector:
    """Compute all risk features from raw student metrics."""
    att_pct = compute_attendance_percentage(
        metrics.sessions_attended, metrics.total_sessions
    )
    att_drop = compute_attendance_drop(metrics.attendance_by_week)
    marks_avg = compute_marks_average(
        metrics.assessment_scores, metrics.assessment_max_scores
    )
    marks_decline = compute_marks_decline(
        metrics.assessment_scores, metrics.assessment_max_scores
    )
    assignment_rate = compute_assignment_completion(
        metrics.assignments_submitted, metrics.assignments_total
    )
    consec = metrics.consecutive_absences
    trend = compute_performance_trend(
        metrics.assessment_scores, metrics.assessment_max_scores
    )
    engagement = compute_engagement_score(att_pct, assignment_rate)

    return FeatureVector(
        student_id=metrics.student_id,
        attendance_percentage=att_pct,
        attendance_drop_percentage=att_drop,
        internal_marks_average=marks_avg,
        marks_decline_percentage=marks_decline,
        assignment_completion_rate=assignment_rate,
        consecutive_absence_count=consec,
        performance_trend=trend,
        engagement_score=engagement,
        has_critical_absence_streak=consec >= 7,
        has_critical_low_attendance=att_pct < 50.0,
        has_critical_low_marks=marks_avg < 35.0,
    )
