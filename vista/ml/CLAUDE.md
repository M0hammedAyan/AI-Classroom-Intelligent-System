# CLAUDE.md — ml/ (Member 4: Risk AI Model & Project Lead)

## Project Context
VISTA is a 4-person college MVP: face-recognition attendance + academic risk flagging.
**Current scope: pilot only — one classroom, 20–30 students.** The original report's
full XGBoost/Logistic Regression model trained on real failure/dropout labels is
Phase 2 — it needs a college partnership with consented historical data, which doesn't
exist yet. Don't claim or build toward that accuracy number prematurely.

## Your Module's Job (technical)
Build a **rule-based** risk flagging engine for the pilot — not supervised ML yet.
Flag students based on trend/threshold deviation from their own baseline:
- Attendance % drop over a rolling window
- Score decline across recent assessments
- Volatility/inconsistency in performance

This needs zero historical failure labels and works with just current-semester data,
which a college will actually hand over.

## Entry Point Contract — do not change the signature without updating the team
```python
# ml/risk_engine.py
def calculate_risk(student_id: str) -> dict:
    """
    Returns: {
        "risk_level": "low" | "medium" | "high",
        "reasons": list[str],         # e.g. ["Attendance dropped 20% in 3 weeks"]
        "confidence": "high" | "moderate" | "low"
    }
    """
```

## Structure
- `features.py` — pulls attendance %, score trend, volatility from the DB
  (per `docs/DB_SCHEMA.md`)
- `risk_engine.py` — threshold logic, wired to the entry point above
- `test_risk_engine.py` — validate against your own batch's real attendance/score data,
  not synthetic data

## Validation Note
Public datasets (OULAD, UCI Student Performance) can be used to sanity-check feature
engineering approach and model logic — not as a stand-in for "trained on real Indian
college data." Don't conflate the two in documentation or the pitch.

## Hard Rules
- Reasons output must be readable by a non-technical teacher — no raw feature names
  or scores without context.
- Don't silently move to supervised ML (Logistic Regression/XGBoost) without flagging
  to the team that it requires real labeled outcome data first.

## Explicitly Out of Scope Right Now
- Supervised ML trained on real failure/dropout labels (needs college data partnership)
- Weekly dynamic re-scoring automation (manual trigger is fine for pilot)
- Multi-college model generalization

## Your Other Job: Project Lead
- Enforce the API contract — no endpoint/field changes without a team sync logged in
  `docs/INTEGRATION_LOG.md`.
- Run a short weekly sync, track the integration checkpoints in the team plan.
- Pitch deck, market research, pricing, patent drafting, documentation: **split across
  all 4 members in weeks 9–12, not solo.** This was the single biggest risk in the
  original work distribution — don't let it quietly slide back onto you.

## File/Naming Conventions
snake_case for all Python files and function names.

## Current Module State (as of last build)

| File | Status | Notes |
|---|---|---|
| `features.py` | Done | `StudentMetrics` → `FeatureVector`, 8 features, all functions per `FEATURE_ENGINEERING.md` |
| `risk_engine.py` | Done | Rule-based engine, `calculate_risk()` public entry point, `calculate_risk_from_metrics()` for direct use |
| `test_risk_engine.py` | Done | 7 test cases from `RISK_ENGINE_SPEC.md` — run with `python -m ml.test_risk_engine` |
| `validate_uci.py` | Done | UCI dataset sanity checker — run with `python -m ml.validate_uci --file path/to/student-mat.csv` |
| DB wiring (`_load_student_metrics`) | Pending | Blocked on `backend/app/db.py` — stub raises `NotImplementedError` until Member 2 delivers DB layer |

---

## Open Questions

These were hit during implementation. Review before the next team sync.

**OQ-ML-1: `calculate_risk()` vs `calculate_risk_from_metrics()`**  
The public contract function `calculate_risk(student_id)` currently raises `NotImplementedError`
because `backend/app/db.py` does not exist yet. Tests and the backend route must use
`calculate_risk_from_metrics(metrics)` until Task 4 (DB wiring) is complete.
Member 2 needs to provide a `get_student_metrics(student_id)` helper in `backend/app/db.py`
that returns a `StudentMetrics` object — then `_load_student_metrics()` in `risk_engine.py`
can call it and `calculate_risk()` becomes fully functional.

**OQ-ML-2: `consecutive_absences` field in `StudentMetrics`**  
`StudentMetrics.consecutive_absences` is currently an integer passed in by the caller.
When DB wiring happens, this needs to be computed from raw attendance rows (sequence of
present/absent statuses) using `compute_consecutive_absences(attendance_sequence)` in
`features.py`. The caller should not compute it manually — `_load_student_metrics()`
should fetch the raw sequence and call that function internally.

**OQ-ML-3: `attendance_by_week` granularity**  
The `attendance_by_week` field expects weekly attendance percentages. The `attendance`
table stores per-session rows with a `session_date` column. The DB loader will need to
group sessions by ISO week number and compute weekly attendance %. Confirm with Member 2
that `session_date` is always a proper DATE type (not a string) so grouping works cleanly.

**OQ-ML-4: Assignment data availability**  
`assignments_submitted` and `assignments_total` are typed as `int | None`. If the
`scores` table does not include an assignment type label, these will always be `None`
and `assignment_completion_rate` will always be excluded from the engagement score.
Confirm with Member 2 whether assignment records are tracked separately or folded into
the general `scores` table with a type field.

---

## Agent Response Convention

After completing any task in this module, always end your response with this block:

**Built:** [1–2 sentences — what was just implemented or changed in `ml/`]  
**Next:** [1–2 specific actionable next steps for this module]

Keep it short. One short paragraph maximum per section. No long summaries unless the user explicitly asks for one.
