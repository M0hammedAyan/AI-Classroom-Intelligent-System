# VISTA — Project-Wide CLAUDE.md

This file is the first thing any agent or team member should read before touching any
file in this repo. It explains what VISTA is, how the team is structured, what has been
built, and what comes next — for everyone, not just one module.

---

## What VISTA Is

**VISTA (Visual Intelligence System for Tracking and Analysis)** is a college academic
monitoring system with two functions:

1. **Automated attendance** — a classroom camera captures an image, the system detects
   and recognizes student faces, and marks attendance without any manual entry.
2. **Academic risk flagging** — students are scored LOW / MEDIUM / HIGH risk based on
   attendance and score trends, with plain-English reasons the teacher can act on.

A role-gated web dashboard (admin / teacher roles) shows attendance logs, risk flags,
and exports.

---

## Pilot Scope — Hard Constraints

This is a **3-month MVP** built by 4 students (~2–3 hrs/day). Hard limits:

| Constraint | Value |
|---|---|
| Classrooms | 1 |
| Students | 20–30 |
| Risk engine | Rule-based thresholds — no supervised ML on real failure labels yet |
| Infrastructure | Dev laptop — no GPU, no cloud, no college server |
| Dashboard | Single role-gated view (admin/teacher) — not separate dashboards per role |
| Auth | JWT, 8-hour expiry — no refresh endpoint |

**If a task requires going beyond any of the above, stop and flag it instead of building
it.** Scope creep is the single biggest risk to this project shipping at all.

---

## Architecture

```
Classroom Camera
       │
       ▼
  vision/              ← detect face → embed → match → liveness check
  recognize()
       │
       ▼
  backend/             ← FastAPI API + PostgreSQL DB
  app/routes/
       │
       ├──▶ ml/        ← calculate_risk(student_id) → risk level + reasons
       │    risk_engine.py
       │
       └──▶ frontend/  ← React dashboard, reads via API
            src/pages/
```

The system is **contract-first**: `docs/API_CONTRACT.md` and `docs/DB_SCHEMA.md` are
frozen after Day 3. All four modules build independently against those contracts.

---

## Team Structure

| Member | Module | Fixed Entry Point |
|---|---|---|
| 1 | `vision/` | `recognize(image_path: str) -> {student_id, confidence, liveness_passed}` |
| 2 | `backend/` | Owns API + DB; wires vision and ML as imported functions |
| 3 | `frontend/` | React dashboard; builds against API contract via `src/api/client.js` |
| 4 | `ml/` | `calculate_risk(student_id: str) -> {risk_level, reasons, confidence}` |

**The two function signatures above are fixed.** Do not propose changing them without
a team sync logged in `docs/INTEGRATION_LOG.md`.

---

## Contract Documents (read before writing any code)

| File | What it is |
|---|---|
| `docs/API_CONTRACT.md` | Every endpoint, request/response schema, error codes |
| `docs/DB_SCHEMA.md` | Every table, column, FK, index, Phase 2 deferral notes |
| `docs/INTEGRATION_LOG.md` | Log of every contract change after Day 3 freeze |
| `docs/RISK_SYSTEM_DESIGN.md` | Risk indicators, scoring formula, override rules, ML upgrade path |
| `docs/FEATURE_ENGINEERING.md` | 8 engineered features with formulas, examples, `features.py` signatures |
| `docs/RISK_ENGINE_SPEC.md` | Full scoring logic, edge cases, 7 unit test cases, `risk_engine.py` architecture |
| `docs/DATASET_ANALYSIS.md` | Public datasets evaluated for Phase 2 ML training |

---

## What Has Been Built

### `vista/ml/`
- `features.py` — feature engineering (attendance %, drop, marks avg, decline, assignment completion, consecutive absences, trend, engagement score)
- `risk_engine.py` — complete pipeline: rule-based engine (`calculate_risk`, `calculate_risk_from_metrics`) + XGBoost inference (`run_pipeline`), DB-wired via `backend/app/db.get_student_metrics()`
- `test_risk_engine.py` — integration tests against 7 student profiles (low, medium, high, override, data-sparse, zero-sessions, improving)
- `train.py` — trains XGBoost + Logistic Regression; XGBoost selected (macro F1 = 0.957)
- `validate_uci.py` — validates rule engine against UCI Student Performance dataset
- `model.pkl` — trained XGBoost model artifact
- `data/student_data.csv` — 200-student synthetic training dataset
- `data/generate_sample_data.py` — reproducible dataset generator
- `__init__.py` — exports public API (`calculate_risk`, `calculate_risk_from_metrics`, `run_pipeline`)

### `vista/docs/`
- `API_CONTRACT.md` — 15 endpoints across auth / students / attendance / risk / reports
- `DB_SCHEMA.md` — 5 tables: `classrooms`, `students`, `attendance`, `scores`, `risk_flags`, `users`
- `INTEGRATION_LOG.md` — 5 resolved open questions logged as founding entries
- `RISK_SYSTEM_DESIGN.md` — problem definition, 8 indicators, 3 risk levels, weighted 0–100 formula
- `FEATURE_ENGINEERING.md` — all 8 features with formulas, examples, and `features.py` structure
- `RISK_ENGINE_SPEC.md` — 9-step scoring logic, override rules, edge cases, test cases, architecture
- `DATASET_ANALYSIS.md` — UCI recommended for Phase 2; OULAD and Kaggle dropout also evaluated

### `vista/` (all 4 module CLAUDE.md files)
- Each module has its own CLAUDE.md with: project context, job description, entry point contract, hard rules, out-of-scope list, naming conventions, and the agent response convention below.

### Not yet built
- `vision/` — detect, embed, match, liveness, recognize (Member 1)
- `frontend/` — Login, Dashboard, AttendanceLog, RiskFlags pages (Member 3)

---

## Key Decisions (locked — do not reopen without a team sync)

| # | Decision |
|---|---|
| 1 | Liveness failure writes a DB row with candidate `student_id` (nullable) — does not mark present. Captures spoofing data cheaply. |
| 2 | Unrecognized faces write no DB row. False-reject rate measured in `test_recognize.py` against a labeled test set. |
| 3 | Risk recompute is manual, admin-only. No scheduled automation in pilot. |
| 4 | JWT expiry 8 hours. No refresh endpoint in pilot. |
| 5 | Absent marking is derived at read time in `GET /attendance/log` — backend diffs full roster against present records. No "close session" endpoint. |

---

## Module-Specific CLAUDE.md Files

Each module has its own CLAUDE.md with finer-grained instructions:

| File | For |
|---|---|
| `vision/CLAUDE.md` | Member 1 — face recognition pipeline |
| `backend/CLAUDE.md` | Member 2 — FastAPI app, DB, mock server |
| `ml/CLAUDE.md` | Member 4 — risk engine, feature engineering |
| `frontend/CLAUDE.md` | Member 3 — React dashboard |

Read your module's CLAUDE.md after this file, not instead of it.

---

## Rules That Apply to Every Module

1. **Read `docs/API_CONTRACT.md` and `docs/DB_SCHEMA.md` fully before writing any code.**
2. **Build one feature at a time.** Implement, then stop for human review before continuing.
3. **Handle failure cases.** A feature is not done until it handles bad input, not just happy-path input.
4. **Do not modify files outside your own module folder.** If your work seems to require a contract change, stop and flag it — don't edit it yourself.
5. **Log ambiguities.** If something is unclear and the docs don't resolve it, make the most reasonable choice, implement it, and add a note under an "Open Questions" section in your module's CLAUDE.md.
6. **Do not add dependencies beyond what your module's CLAUDE.md lists.**

---

## What NOT to Build (project-wide — Phase 2 and later)

- Multi-classroom or multi-college support
- Message queues, vector DBs (FAISS/pgvector), or any scale infrastructure
- Edge device deployment (Raspberry Pi/Jetson) or GPU provisioning
- Supervised ML risk model trained on real outcome labels (needs college data partnership)
- Real-time alerts, LMS integration, or weekly auto-rescoring automation
- Separate Teacher/Mentor/Admin dashboards
- Token refresh endpoint

---

## Agent Response Convention (applies to all modules)

After completing any task anywhere in this repo, end your response with:

**Built:** [1–2 sentences — what was just implemented or changed]  
**Next:** [1–2 specific actionable next steps]

Short. Factual. No long summaries unless explicitly asked for.

---

## Integration Checkpoints (rough timeline)

| Week | Checkpoint |
|---|---|
| 1–2 | Contracts frozen (API + DB). Mock server live. Vision enrollment working. |
| 3–4 | Face detection + matching working on real classroom photos. Risk engine rule logic complete. |
| 5–6 | Backend routes wired. Auth working. Frontend consuming mock server. |
| 7–8 | Frontend swapped to real backend. End-to-end attendance flow working. |
| 9–10 | Risk flags visible on dashboard. Export working. |
| 11–12 | Pilot demo with real classroom. Pitch deck + documentation split across team. |

Any checkpoint that is hit, missed, or delayed gets logged in `docs/INTEGRATION_LOG.md`.
