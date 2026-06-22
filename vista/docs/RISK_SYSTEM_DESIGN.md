# VISTA Risk System Design

**Module:** `ml/`  
**Owner:** Risk AI Lead  
**Status:** Approved — pilot design, rule-based engine. ML upgrade path documented in Section 7.

---

## 1. Problem Definition

A student is "at risk" when their academic trajectory — based on measurable behavioural and performance signals — makes them statistically likely to fail, drop out, or require remedial intervention before the end of the semester.

Risk is not a single bad test score. It is a pattern: sustained low attendance, declining marks over consecutive assessments, missing assignments, or a sudden sharp drop in any one dimension after a previously stable period. The engine must distinguish a one-off bad week from a structural decline.

The engine answers one question per student per computation:
> "Given what we know about this student's recent attendance and academic performance, how likely are they to need teacher intervention in the next 2–4 weeks?"

The output is not a diagnosis — it is a triage signal for the teacher.

---

## 2. Risk Indicators

| # | Indicator | Description | Data Source |
|---|---|---|---|
| 1 | **Attendance %** | Total sessions attended ÷ total sessions held × 100 | `attendance` table |
| 2 | **Attendance drop %** | Decline in attendance rate between the first half and second half of the observation window | `attendance` table |
| 3 | **Internal marks average** | Mean score across all internal assessments (normalised to 0–100) | `scores` table |
| 4 | **Marks decline %** | Percentage fall from best recent score to current score | `scores` table |
| 5 | **Assignment completion %** | Assignments submitted ÷ assignments issued × 100 | `scores` table (assignment type) |
| 6 | **Consecutive absences** | Longest unbroken run of absent days in the observation window | `attendance` table |
| 7 | **Academic trend** | Direction of score change across the last 3 assessments: IMPROVING / STABLE / DECLINING | `scores` table |
| 8 | **Engagement score** | Composite of attendance regularity + assignment completion — proxy for active participation | `attendance` + `scores` tables |

---

## 3. Risk Levels

### LOW — Score 0–39

The student is performing within acceptable bounds. No intervention required, but the teacher should continue regular monitoring.

| Attribute | Value |
|---|---|
| Score range | 0 – 39 |
| Attendance | ≥ 75% |
| Marks | ≥ 60% average |
| Trend | Stable or improving |
| Teacher action | No immediate action. Flag for review only if trend turns negative over next 2 weeks. |

---

### MEDIUM — Score 40–69

The student shows one or more warning signals: attendance slipping, marks declining, or engagement dropping. Intervention is recommended before the situation becomes critical.

| Attribute | Value |
|---|---|
| Score range | 40 – 69 |
| Attendance | 60–74% OR recent drop of 10–20% |
| Marks | 45–59% average OR declining trend |
| Trend | Declining or mixed |
| Teacher action | Schedule a one-on-one check-in. Notify mentor. Monitor weekly. |

---

### HIGH — Score 70–100

The student is in active academic distress. Multiple indicators are in the danger zone simultaneously. Immediate intervention is required.

| Attribute | Value |
|---|---|
| Score range | 70 – 100 |
| Attendance | < 60% OR drop > 20% in recent weeks |
| Marks | < 45% average OR sharp recent decline |
| Trend | Consistently declining |
| Teacher action | Immediate counselling referral. Notify HOD. Create intervention plan. |

---

## 4. Risk Scoring Formula

The engine produces a 0–100 risk score. Higher = more at risk.

### Weights

```
attendance_weight         = 0.30   # Most reliable daily signal
marks_weight              = 0.25   # Core academic outcome
attendance_drop_weight    = 0.15   # Detects sudden behavioural change
marks_decline_weight      = 0.15   # Detects sudden academic change
consecutive_absence_weight = 0.10  # Early dropout signal
engagement_weight         = 0.05   # Weak but useful secondary signal
```

**Total weight = 1.00**

### Component Scores (each 0–100, higher = more at risk)

```
attendance_score      = max(0, 100 - attendance_pct)
                        # 75% attendance → score 25; 50% → score 50

marks_score           = max(0, 100 - marks_avg)
                        # 60 avg → score 40; 35 avg → score 65

drop_score            = min(100, attendance_drop_pct * 3)
                        # 10% drop → score 30; 25% drop → score 75

decline_score         = min(100, marks_decline_pct * 2.5)
                        # 20% decline → score 50; 40% decline → score 100

consec_absence_score  = min(100, consecutive_absences * 12)
                        # 5 consecutive → score 60; 8+ → score 96+

engagement_score_inv  = max(0, 100 - engagement_score)
                        # engagement 80 → risk 20
```

### Final Score

```
risk_score = (
    attendance_score      * 0.30 +
    marks_score           * 0.25 +
    drop_score            * 0.15 +
    decline_score         * 0.15 +
    consec_absence_score  * 0.10 +
    engagement_score_inv  * 0.05
)
```

### Override Rules (applied after score)

These hard rules can upgrade a risk level regardless of score, because some patterns are critical even if other indicators look acceptable:

| Condition | Override |
|---|---|
| Consecutive absences ≥ 7 | Force HIGH |
| Attendance % < 50 | Force HIGH |
| Marks average < 35 | Force HIGH |
| Attendance drop > 25% in 2 weeks | Force at least MEDIUM |
| Marks decline > 30% in last 2 assessments | Force at least MEDIUM |

---

## 5. Risk Engine Inputs

All inputs are per-student, for a specified observation window (default: current semester to date).

| Input | Type | Required | Notes |
|---|---|---|---|
| `student_id` | string | yes | College roll number |
| `total_sessions` | integer | yes | Sessions held in observation window |
| `sessions_attended` | integer | yes | Sessions attended |
| `assessment_scores` | list of floats | yes | Chronological, normalised to 0–100 |
| `max_scores` | list of floats | yes | Max possible for each assessment |
| `assignment_submitted` | integer | yes | Count of submitted assignments |
| `assignment_total` | integer | yes | Count of issued assignments |
| `attendance_by_week` | list of floats | yes | Weekly attendance %, chronological |
| `consecutive_absences` | integer | yes | Current or longest recent streak |
| `observation_window_days` | integer | no | Default 90 (one semester segment) |

---

## 6. Risk Engine Outputs

```json
{
  "student_id": "CS22B001",
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

| Field | Type | Notes |
|---|---|---|
| `student_id` | string | Echoed from input |
| `risk_score` | integer | 0–100 |
| `risk_level` | string | `"LOW"`, `"MEDIUM"`, `"HIGH"` |
| `confidence` | string | `"high"` (all inputs present), `"moderate"` (some missing), `"low"` (many missing) |
| `reasons` | list of strings | Max 4, ordered by severity |
| `recommendations` | list of strings | Max 3, matched to risk level and reasons |
| `computed_at` | string | ISO 8601 UTC datetime |
| `override_applied` | boolean | True if a hard override rule changed the final level |
| `override_reason` | string or null | Which override triggered, if any |

---

## 7. Future ML Upgrade Path

The rule-based engine is designed so the function signature does not change when the model underneath is replaced. The backend calls `calculate_risk(student_id)` — the internals are invisible to it.

### Phase 2 — Logistic Regression

When: once 1–2 semesters of pilot data are collected (200–400 student-semester records with actual outcomes).

- Features from `FEATURE_ENGINEERING.md` become the input vector.
- Target label: `failed` (0/1) based on end-of-semester results.
- Logistic Regression is interpretable — coefficients map directly to feature importance, which preserves the "reasons" output.
- Replace the weighted formula with `model.predict_proba(feature_vector)`.

### Phase 3 — Random Forest

When: dataset grows to 500+ records and linear assumptions no longer hold.

- Handles non-linear interactions (e.g. attendance matters more when marks are also low).
- Feature importance from `feature_importances_` feeds the reasons list.
- More robust to missing features than logistic regression.

### Phase 4 — XGBoost

When: dataset has 1000+ records and Random Forest accuracy plateaus.

- Gradient boosting captures complex patterns and handles class imbalance natively via `scale_pos_weight`.
- SHAP values (already implemented in `ml/risk_engine.py`) provide per-prediction explanations.
- This is the production target model — already partially scaffolded in the existing codebase.

### Design Invariant

The function signature is fixed across all phases:

```python
def calculate_risk(student_id: str) -> dict:
    # returns: risk_level, reasons, confidence
    # internals swap; contract never changes
```

The feature engineering layer (`features.py`) is shared across all phases — the same features feed both the rule engine now and the ML models later. This means the pilot is not throwaway work; it builds the training pipeline.
