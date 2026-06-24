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
| `train.py` | Done | Trains XGBoost + LR on synthetic data; XGBoost selected (macro F1 = 0.957) |
| `data/generate_sample_data.py` | Done | 200-student synthetic dataset generator |
| `__init__.py` | Done | Exports public API: `calculate_risk`, `calculate_risk_from_metrics`, `run_pipeline` |
| DB wiring (`_load_student_metrics`) | Done | Calls `backend/app/db.get_student_metrics()` — fully functional when DB is available |

---

## Open Questions

These were hit during implementation. All resolved as of 2026-06-22.

**OQ-ML-1: `calculate_risk()` vs `calculate_risk_from_metrics()` — RESOLVED**  
`_load_student_metrics()` now calls `backend/app/db.get_student_metrics(student_id, db)`
which builds a `StudentMetrics` object from the attendance and scores tables.
`calculate_risk(student_id)` is fully functional when the DB is seeded.

**OQ-ML-2: `consecutive_absences` field in `StudentMetrics` — RESOLVED**  
`get_student_metrics()` in `backend/app/db.py` fetches raw attendance rows, extracts
the status sequence, and calls `compute_consecutive_absences(attendance_sequence)` from
`features.py` to derive the value. The caller does not compute it manually.

**OQ-ML-3: `attendance_by_week` granularity — RESOLVED**  
`get_student_metrics()` groups attendance rows by ISO week number using
`datetime.strptime(session_date, "%Y-%m-%d").date().isocalendar()` and computes
weekly attendance percentages. `session_date` is stored as `TEXT` in `YYYY-MM-DD` format.

**OQ-ML-4: Assignment data availability — RESOLVED (N/A for pilot)**  
The `scores` table does not include a type field distinguishing assignments from exams.
`assignments_submitted` and `assignments_total` are set to `None` in the DB loader.
The engagement score uses attendance-only mode when assignment data is unavailable.

---

## Agent Response Convention

After completing any task in this module, always end your response with this block:

**Built:** [1–2 sentences — what was just implemented or changed in `ml/`]  
**Next:** [1–2 specific actionable next steps for this module]

Keep it short. One short paragraph maximum per section. No long summaries unless the user explicitly asks for one.
