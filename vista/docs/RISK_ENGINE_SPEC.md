# VISTA Risk Engine Specification

**Module:** `ml/risk_engine.py`  
**Owner:** Risk AI Lead  
**Depends on:** `RISK_SYSTEM_DESIGN.md`, `FEATURE_ENGINEERING.md`  
**Status:** Approved for pilot — rule-based implementation.

---

## 1. Engine Contract

The engine exposes one public function. This signature is fixed — it does not change when the ML upgrade happens in Phase 2.

```python
def calculate_risk(student_id: str) -> dict:
```

**Input:** `student_id` — college roll number string.

**Output:**
```json
{
  "risk_score": 67,
  "risk_level": "MEDIUM",
  "confidence": "moderate",
  "reasons": [
    "Attendance dropped 18% over the last 3 weeks",
    "Average internal marks at 51% — below the 60% threshold",
    "Declining score trend across last 3 assessments"
  ],
  "recommendations": [
    "Schedule a one-on-one check-in with the student",
    "Notify academic mentor",
    "Monitor attendance weekly for the next 2 weeks"
  ],
  "computed_at": "2026-06-21T10:30:00Z",
  "override_applied": false,
  "override_reason": null
}
```

---

## 2. Scoring Logic

### Step 1 — Load and validate raw data

Pull attendance and score rows for the student from the DB for the current semester window. If student does not exist, raise `StudentNotFoundError`. If fewer than 5 attendance records or 1 score record exist, set `confidence = "low"` and proceed with available data.

### Step 2 — Compute features

Call `features.compute_features(metrics)` to get a `FeatureVector`. See `FEATURE_ENGINEERING.md` for formulas.

### Step 3 — Compute component risk scores (each 0–100, higher = more at risk)

```python
attendance_score      = max(0.0, 100.0 - features.attendance_percentage)
marks_score           = max(0.0, 100.0 - features.internal_marks_average)
drop_score            = min(100.0, features.attendance_drop_percentage * 3.0)
decline_score         = min(100.0, features.marks_decline_percentage * 2.5)
consec_score          = min(100.0, features.consecutive_absence_count * 12.0)
trend_score           = {"DECLINING": 60, "STABLE": 20, "IMPROVING": 0,
                         "INSUFFICIENT_DATA": 30}[features.performance_trend]
engagement_inv_score  = max(0.0, 100.0 - features.engagement_score)
```

### Step 4 — Weighted sum

```python
WEIGHTS = {
    "attendance":   0.30,
    "marks":        0.25,
    "drop":         0.15,
    "decline":      0.15,
    "consecutive":  0.10,
    "engagement":   0.05,
}

raw_score = (
    attendance_score     * WEIGHTS["attendance"] +
    marks_score          * WEIGHTS["marks"] +
    drop_score           * WEIGHTS["drop"] +
    decline_score        * WEIGHTS["decline"] +
    consec_score         * WEIGHTS["consecutive"] +
    engagement_inv_score * WEIGHTS["engagement"]
)

risk_score = round(min(100, max(0, raw_score)))
```

### Step 5 — Assign risk level from score

```python
if risk_score < 40:
    risk_level = "LOW"
elif risk_score < 70:
    risk_level = "MEDIUM"
else:
    risk_level = "HIGH"
```

### Step 6 — Apply override rules

Override rules are checked after the score. They can only upgrade a level (LOW → MEDIUM, LOW/MEDIUM → HIGH), never downgrade.

```python
override_applied = False
override_reason = None

if features.consecutive_absence_count >= 7:
    risk_level = "HIGH"
    override_applied = True
    override_reason = "Consecutive absences >= 7"

elif features.attendance_percentage < 50:
    risk_level = "HIGH"
    override_applied = True
    override_reason = "Attendance below 50%"

elif features.internal_marks_average < 35:
    risk_level = "HIGH"
    override_applied = True
    override_reason = "Marks average below 35%"

elif features.attendance_drop_percentage > 25 and risk_level == "LOW":
    risk_level = "MEDIUM"
    override_applied = True
    override_reason = "Attendance drop > 25%"

elif features.marks_decline_percentage > 30 and risk_level == "LOW":
    risk_level = "MEDIUM"
    override_applied = True
    override_reason = "Marks decline > 30%"
```

### Step 7 — Generate reasons

Reasons are generated from the worst-performing features, ordered by their weighted contribution to the score. Maximum 4 reasons returned.

```python
REASON_TEMPLATES = {
    "attendance":  lambda f: f"Attendance at {f.attendance_percentage:.0f}% — below the 75% threshold"
                             if f.attendance_percentage < 75 else None,
    "drop":        lambda f: f"Attendance dropped {f.attendance_drop_percentage:.0f}% recently"
                             if f.attendance_drop_percentage > 10 else None,
    "marks":       lambda f: f"Average internal marks at {f.internal_marks_average:.0f}% — below the 60% threshold"
                             if f.internal_marks_average < 60 else None,
    "decline":     lambda f: f"Marks declined {f.marks_decline_percentage:.0f}% from recent peak"
                             if f.marks_decline_percentage > 15 else None,
    "consecutive": lambda f: f"{f.consecutive_absence_count} consecutive absences detected"
                             if f.consecutive_absence_count >= 3 else None,
    "trend":       lambda f: "Declining score trend across last 3 assessments"
                             if f.performance_trend == "DECLINING" else None,
    "engagement":  lambda f: f"Engagement score at {f.engagement_score:.0f}% — low participation"
                             if f.engagement_score < 60 else None,
}
```

### Step 8 — Generate recommendations

Recommendations are selected based on `risk_level` and active reasons.

```python
RECOMMENDATIONS = {
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

# Attendance-specific additions
if "attendance" in active_reason_keys or "drop" in active_reason_keys:
    add "Review attendance records with student"

if "marks" in active_reason_keys or "decline" in active_reason_keys:
    add "Provide additional academic support resources"
```

### Step 9 — Compute confidence

```python
missing_count = sum([
    features.assignment_completion_rate is None,
    len(assessment_scores) < 3,
    len(attendance_by_week) < 4,
])

if missing_count == 0:
    confidence = "high"
elif missing_count == 1:
    confidence = "moderate"
else:
    confidence = "low"
```

---

## 3. Rule Evaluation Order

Override rules are evaluated in this exact order. The first matching rule wins; subsequent rules are not checked.

1. `consecutive_absence_count >= 7` → HIGH
2. `attendance_percentage < 50` → HIGH
3. `internal_marks_average < 35` → HIGH
4. `attendance_drop_percentage > 25` AND current level is LOW → MEDIUM
5. `marks_decline_percentage > 30` AND current level is LOW → MEDIUM

Rationale: Rules 1–3 represent critical academic distress. Rules 4–5 prevent under-triaging students whose score came out low but a single dramatic signal warrants attention.

---

## 4. Edge Cases

| Scenario | Handling |
|---|---|
| Student has no attendance records | Return `confidence = "low"`, `risk_level = "HIGH"` with reason "No attendance data available — manual review required" |
| Student has no score records | Compute from attendance only; set `marks_score = 50` (neutral); `confidence = "low"` |
| `total_sessions = 0` | Return error: `InsufficientDataError("No sessions recorded for this window")` |
| All assessments have `max_score = 0` | Skip normalisation; use raw scores; add validation warning to reasons |
| `assignments_total = 0` | Set `assignment_completion_rate = None`; exclude from engagement score; use `attendance_component` only |
| `attendance_by_week` has fewer than 2 entries | Set `attendance_drop_percentage = 0`; do not compute drop score |
| `assessment_scores` has fewer than 2 entries | Set `performance_trend = "INSUFFICIENT_DATA"`; set `marks_decline_percentage = 0` |
| Student score is exactly on a threshold boundary (score = 40 or 70) | Lower boundary is inclusive: score 40 → MEDIUM, score 70 → HIGH |
| Override fires but score is already HIGH | No change; `override_applied = False` (override only upgrades) |

---

## 5. Unit Test Cases

### Test 1 — Healthy student → LOW

```python
input = StudentMetrics(
    student_id="CS22B001",
    total_sessions=40, sessions_attended=36,        # 90% attendance
    attendance_by_week=[88, 90, 92, 88, 90],
    consecutive_absences=1,
    assessment_scores=[72, 78, 80], assessment_max_scores=[100, 100, 100],
    assignments_submitted=9, assignments_total=10,
)
expected = {"risk_level": "LOW", "risk_score": range(0, 40)}
```

### Test 2 — Borderline student → MEDIUM

```python
input = StudentMetrics(
    student_id="CS22B002",
    total_sessions=40, sessions_attended=28,        # 70% attendance
    attendance_by_week=[80, 75, 68, 62, 60],        # dropping
    consecutive_absences=3,
    assessment_scores=[58, 54, 51], assessment_max_scores=[100, 100, 100],
    assignments_submitted=6, assignments_total=10,
)
expected = {"risk_level": "MEDIUM", "risk_score": range(40, 70)}
```

### Test 3 — At-risk student → HIGH (score-based)

```python
input = StudentMetrics(
    student_id="CS22B003",
    total_sessions=40, sessions_attended=20,        # 50% attendance
    attendance_by_week=[70, 60, 50, 40, 40],
    consecutive_absences=5,
    assessment_scores=[38, 32, 28], assessment_max_scores=[100, 100, 100],
    assignments_submitted=3, assignments_total=10,
)
expected = {"risk_level": "HIGH", "risk_score": range(70, 101)}
```

### Test 4 — Override fires: consecutive absences

```python
input = StudentMetrics(
    student_id="CS22B004",
    total_sessions=40, sessions_attended=30,        # 75% — would be LOW/MEDIUM
    attendance_by_week=[80, 80, 75, 40, 40],
    consecutive_absences=8,                         # triggers override
    assessment_scores=[65, 62, 60], assessment_max_scores=[100, 100, 100],
    assignments_submitted=8, assignments_total=10,
)
expected = {"risk_level": "HIGH", "override_applied": True,
            "override_reason": "Consecutive absences >= 7"}
```

### Test 5 — Missing score data → LOW confidence

```python
input = StudentMetrics(
    student_id="CS22B005",
    total_sessions=40, sessions_attended=32,
    attendance_by_week=[80, 80, 80],
    consecutive_absences=0,
    assessment_scores=[],                            # no scores yet
    assessment_max_scores=[],
    assignments_submitted=None, assignments_total=None,
)
expected = {"confidence": "low"}
```

### Test 6 — Zero sessions → error

```python
input = StudentMetrics(student_id="CS22B006", total_sessions=0, ...)
expected = raises InsufficientDataError
```

### Test 7 — Improving student → LOW, IMPROVING trend

```python
input = StudentMetrics(
    student_id="CS22B007",
    total_sessions=40, sessions_attended=32,        # 80%
    attendance_by_week=[70, 74, 78, 82, 84],        # improving
    consecutive_absences=0,
    assessment_scores=[55, 62, 71], assessment_max_scores=[100, 100, 100],
    assignments_submitted=9, assignments_total=10,
)
expected = {"risk_level": "LOW", "performance_trend": "IMPROVING"}
```

---

## 6. `risk_engine.py` Architecture

### Classes

```python
class StudentNotFoundError(Exception): ...
class InsufficientDataError(Exception): ...

@dataclass
class RiskResult:
    student_id: str
    risk_score: int                  # 0–100
    risk_level: str                  # "LOW" | "MEDIUM" | "HIGH"
    confidence: str                  # "high" | "moderate" | "low"
    reasons: list[str]               # max 4
    recommendations: list[str]       # max 3
    computed_at: str                 # ISO 8601 UTC
    override_applied: bool
    override_reason: str | None
```

### Functions

```python
# Public entry point — signature never changes
def calculate_risk(student_id: str) -> dict:
    """
    Load student data, compute features, score, apply overrides,
    generate reasons and recommendations, return serialised RiskResult.
    """

# Data loading
def _load_student_metrics(student_id: str) -> StudentMetrics:
    """Query attendance and scores tables; raise StudentNotFoundError if absent."""

# Scoring
def _compute_component_scores(features: FeatureVector) -> dict[str, float]:
    """Return {attendance, marks, drop, decline, consecutive, trend, engagement} scores."""

def _weighted_sum(component_scores: dict[str, float]) -> int:
    """Apply WEIGHTS dict, clamp to 0–100, return integer score."""

def _score_to_level(score: int) -> str:
    """Map 0–39 → LOW, 40–69 → MEDIUM, 70–100 → HIGH."""

# Override rules
def _apply_overrides(
    level: str, features: FeatureVector
) -> tuple[str, bool, str | None]:
    """Evaluate override rules in order; return (adjusted_level, applied, reason)."""

# Output generation
def _generate_reasons(
    features: FeatureVector, component_scores: dict[str, float]
) -> list[str]:
    """Build reason strings for features above threshold, ordered by severity."""

def _generate_recommendations(
    risk_level: str, active_reason_keys: list[str]
) -> list[str]:
    """Select recommendations from RECOMMENDATIONS dict, add context-specific items."""

def _compute_confidence(features: FeatureVector) -> str:
    """Count missing inputs; return high/moderate/low."""
```

### Data Flow

```
calculate_risk(student_id)
        │
        ▼
_load_student_metrics()       ← DB: attendance + scores tables
        │
        ▼
features.compute_features()   ← FEATURE_ENGINEERING.md
        │
        ▼
_compute_component_scores()
        │
        ▼
_weighted_sum()  ──▶  risk_score (0–100)
        │
        ▼
_score_to_level()  ──▶  risk_level (initial)
        │
        ▼
_apply_overrides()  ──▶  risk_level (final), override_applied, override_reason
        │
        ├──▶  _generate_reasons()       ──▶  reasons[]
        ├──▶  _generate_recommendations()  ──▶  recommendations[]
        └──▶  _compute_confidence()     ──▶  confidence
                │
                ▼
        RiskResult  ──▶  .to_dict()  ──▶  return to caller
```
