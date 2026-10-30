# VISTA Feature Engineering

**Module:** `ml/features.py`  
**Owner:** Risk AI Lead  
**Depends on:** `RISK_SYSTEM_DESIGN.md`  
**Status:** Approved for pilot.

All features are computed per student over a configurable observation window (default: current semester to date). All percentage values are 0–100. All features are real numbers unless noted.

---

## Feature 1 — `attendance_percentage`

**What it measures:** How regularly the student shows up overall.

**Formula:**
```
attendance_percentage = (sessions_attended / total_sessions) * 100
```

**Data source:** `attendance` table — count rows where `status = "present"` for the student in the window, divided by total session rows.

**Why it matters:** The single strongest standalone predictor of academic failure. A student who is not present cannot learn. Minimum threshold for most colleges is 75%; students below it are often automatically barred from exams.

**Example:**
- `sessions_attended = 34`, `total_sessions = 45`
- `attendance_percentage = (34 / 45) * 100 = 75.56`

---

## Feature 2 — `attendance_drop_percentage`

**What it measures:** Whether attendance is getting worse recently, not just how bad it is overall.

**Formula:**
```
# Split observation window in half
first_half_sessions  = sessions in first 50% of window
second_half_sessions = sessions in second 50% of window

first_half_rate  = (attended_first_half  / first_half_sessions)  * 100
second_half_rate = (attended_second_half / second_half_sessions) * 100

attendance_drop_percentage = first_half_rate - second_half_rate
# Positive = attendance getting worse. Negative = improving.
```

**Data source:** `attendance` table — split rows by `session_date` at the window midpoint.

**Why it matters:** A student at 70% attendance who is trending upward is a different problem from one at 70% trending downward. This feature captures direction, not just level. A sudden 20% drop in the last 2 weeks is a stronger early warning signal than a stable 65% all semester.

**Example:**
- First half: 20/25 attended → 80%
- Second half: 12/20 attended → 60%
- `attendance_drop_percentage = 80 - 60 = 20.0`

---

## Feature 3 — `internal_marks_average`

**What it measures:** The student's average academic performance across all internal assessments in the window.

**Formula:**
```
normalised_scores = [(score_i / max_score_i) * 100 for each assessment i]
internal_marks_average = mean(normalised_scores)
```

**Data source:** `scores` table — all rows for the student in the observation window.

**Why it matters:** Direct measure of academic standing. Students below 60% average are at risk; below 40% is critical. Normalisation to 0–100 ensures comparability across subjects with different maximum marks.

**Example:**
- Scores: `[(45, 60), (38, 50), (72, 100)]` → normalised: `[75.0, 76.0, 72.0]`
- `internal_marks_average = (75.0 + 76.0 + 72.0) / 3 = 74.33`

---

## Feature 4 — `marks_decline_percentage`

**What it measures:** How much marks have fallen from the student's best recent performance to their current performance.

**Formula:**
```
recent_scores = last 3 normalised assessment scores (chronological)
peak_score    = max(recent_scores)
latest_score  = recent_scores[-1]  # most recent

marks_decline_percentage = max(0, ((peak_score - latest_score) / peak_score) * 100)
# Clamped to 0 — we don't report "negative decline" (improvement)
```

**Data source:** `scores` table — last 3 assessments ordered by date.

**Why it matters:** A student who scored 80% then 75% then 55% is in sharper decline than one who has been at 55% all semester. This feature catches the "falling off a cliff" pattern that overall average misses.

**Example:**
- Last 3 normalised scores: `[82, 75, 54]`
- `peak_score = 82`, `latest_score = 54`
- `marks_decline_percentage = ((82 - 54) / 82) * 100 = 34.15`

---

## Feature 5 — `assignment_completion_rate`

**What it measures:** Proportion of issued assignments that the student has submitted.

**Formula:**
```
assignment_completion_rate = (assignments_submitted / assignments_total) * 100
```

**Data source:** `scores` table — filter by a score type label of `"assignment"` (requires that assignment records are stored with a type field). If type field is unavailable in the pilot, this feature defaults to `None` and is excluded from the score computation.

**Why it matters:** Assignment completion is a leading indicator — it shows whether a student is engaging with coursework between assessments. Students who stop submitting assignments typically show mark declines 2–4 weeks later. It also captures effort independent of ability.

**Example:**
- `assignments_submitted = 7`, `assignments_total = 10`
- `assignment_completion_rate = (7 / 10) * 100 = 70.0`

---

## Feature 6 — `consecutive_absence_count`

**What it measures:** The longest unbroken streak of absences in the observation window.

**Formula:**
```
# Walk through attendance records chronologically
max_streak = 0
current_streak = 0

for each session in chronological order:
    if status == "absent" or status == "liveness_failed":
        current_streak += 1
        max_streak = max(max_streak, current_streak)
    else:
        current_streak = 0

consecutive_absence_count = max_streak
```

**Data source:** `attendance` table — all rows for the student in window, ordered by `session_date`.

**Why it matters:** 3–4 consecutive absences often signals a personal crisis (health, family, financial) rather than routine disengagement. It triggers faster escalation than overall percentage alone. A student at 70% attendance with one 7-day streak is more urgent than one who missed evenly spread sessions.

**Example:**
- Attendance sequence: `P P A A A A P P A P`
- Streaks: 4, 1
- `consecutive_absence_count = 4`

---

## Feature 7 — `performance_trend`

**What it measures:** The direction of academic performance across the last 3 assessments.

**Formula:**
```
recent_scores = last 3 normalised assessment scores (chronological)

if len(recent_scores) < 2:
    trend = "INSUFFICIENT_DATA"
elif recent_scores[-1] > recent_scores[0] + 5:
    trend = "IMPROVING"
elif recent_scores[-1] < recent_scores[0] - 5:
    trend = "DECLINING"
else:
    trend = "STABLE"

# The +/- 5 threshold avoids noise-driven trend flips for small changes
```

**Data source:** `scores` table — last 3 assessments.

**Output type:** Categorical — `"IMPROVING"`, `"STABLE"`, `"DECLINING"`, `"INSUFFICIENT_DATA"`.

**Encoding for scoring:** `DECLINING = 1`, `STABLE = 0`, `IMPROVING = -1` (negative = lowers risk score).

**Why it matters:** Context for the marks average. A student at 58% average who is improving is less urgent than one who is declining. Trend is cheap to compute and high signal.

**Example:**
- Last 3 normalised scores: `[62, 58, 54]`
- `recent_scores[-1] (54) < recent_scores[0] (62) - 5` → `trend = "DECLINING"`

---

## Feature 8 — `engagement_score`

**What it measures:** A composite proxy for active participation — how consistently the student shows up AND submits work.

**Formula:**
```
attendance_component   = attendance_percentage / 100          # 0–1
completion_component   = assignment_completion_rate / 100     # 0–1, or 0.5 if unavailable

engagement_score = (0.6 * attendance_component + 0.4 * completion_component) * 100
# Result: 0–100. Higher = more engaged.
```

**Data source:** Derived from `attendance_percentage` and `assignment_completion_rate`.

**Why it matters:** A student can have decent marks but be coasting on past knowledge while disengaging (high marks, low attendance, no assignments). Engagement score captures this decoupling. It also provides a softer signal when marks data is sparse early in semester.

**Example:**
- `attendance_percentage = 72`, `assignment_completion_rate = 60`
- `engagement_score = (0.6 * 0.72 + 0.4 * 0.60) * 100 = (0.432 + 0.240) * 100 = 67.2`

---

## `features.py` Structure

### Input Schema

```python
@dataclass
class StudentMetrics:
    student_id: str

    # Attendance
    total_sessions: int
    sessions_attended: int
    attendance_by_week: list[float]       # weekly attendance %, chronological
    consecutive_absences: int

    # Scores
    assessment_scores: list[float]        # raw scores, chronological
    assessment_max_scores: list[float]    # max possible per assessment

    # Assignments (optional — None if not tracked)
    assignments_submitted: int | None
    assignments_total: int | None

    # Window
    observation_window_days: int = 90
```

### Output Schema

```python
@dataclass
class FeatureVector:
    student_id: str

    attendance_percentage: float          # 0–100
    attendance_drop_percentage: float     # positive = worsening
    internal_marks_average: float         # 0–100
    marks_decline_percentage: float       # 0–100, clamped at 0
    assignment_completion_rate: float | None  # None if data unavailable
    consecutive_absence_count: int
    performance_trend: str                # "IMPROVING" | "STABLE" | "DECLINING" | "INSUFFICIENT_DATA"
    engagement_score: float               # 0–100

    # Derived flags for override rules (used by risk_engine.py)
    has_critical_absence_streak: bool     # consecutive_absence_count >= 7
    has_critical_low_attendance: bool     # attendance_percentage < 50
    has_critical_low_marks: bool          # internal_marks_average < 35
```

### Function Signatures

```python
def compute_features(metrics: StudentMetrics) -> FeatureVector:
    """
    Main entry point. Computes all features from raw student metrics.
    Calls each sub-function below and assembles FeatureVector.
    """

def compute_attendance_percentage(
    sessions_attended: int,
    total_sessions: int
) -> float: ...

def compute_attendance_drop(
    attendance_by_week: list[float]
) -> float: ...

def compute_marks_average(
    scores: list[float],
    max_scores: list[float]
) -> float: ...

def compute_marks_decline(
    scores: list[float],
    max_scores: list[float]
) -> float: ...

def compute_assignment_completion(
    submitted: int | None,
    total: int | None
) -> float | None: ...

def compute_consecutive_absences(
    attendance_sequence: list[str]   # list of "present"/"absent" strings
) -> int: ...

def compute_performance_trend(
    scores: list[float],
    max_scores: list[float]
) -> str: ...

def compute_engagement_score(
    attendance_pct: float,
    completion_rate: float | None
) -> float: ...
```

### Data Flow

```
StudentMetrics
     │
     ├── compute_attendance_percentage()  ──▶ attendance_percentage
     ├── compute_attendance_drop()        ──▶ attendance_drop_percentage
     ├── compute_marks_average()          ──▶ internal_marks_average
     ├── compute_marks_decline()          ──▶ marks_decline_percentage
     ├── compute_assignment_completion()  ──▶ assignment_completion_rate
     ├── compute_consecutive_absences()   ──▶ consecutive_absence_count
     ├── compute_performance_trend()      ──▶ performance_trend
     └── compute_engagement_score()       ──▶ engagement_score
                                                │
                                          FeatureVector
                                                │
                                         risk_engine.py
```
