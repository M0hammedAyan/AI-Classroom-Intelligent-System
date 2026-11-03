# VISTA — Final Audit Report
## Exhibition: 7 Nov 2026 | Audit Run: 2026-11-03 11:54 IST

> **STATUS: IN PROGRESS** — This file is being filled in by the audit workflow.
> Sections marked `[IN PROGRESS]` or `[PENDING]` will be completed by subsequent steps.
>
> **Backup:** 57 .md/.tex files backed up to `docs_backup_final/` before any edits.
>
> **Git state at audit start:**
> Branch: `cleanup/remove-dead-files`
> Dirty: `vista/vision/__pycache__/recognize.cpython-311.pyc` (compiled bytecode — not a source change)
> Untracked: `docs_backup_final/` (created by this audit)

---

## PART 1 — RUN AND VERIFY

> Evidence gathered by actually running the system, not by reading code.

### 1.1 Startup — Backend and Frontend

```
[IN PROGRESS — Step will run: cd vista && .venv/Scripts/activate && python -m uvicorn ... ]
```

| Check | Result | Notes |
|---|---|---|
| Backend starts without error | PENDING | |
| Frontend starts without error | PENDING | |
| Startup warnings | PENDING | |
| Documented commands match reality | PENDING | |

---

### 1.2 Full Test Suite

```
[IN PROGRESS — Step will run: python -m pytest ... ]
```

| Metric | Value |
|---|---|
| Tests collected | PENDING |
| Passed | PENDING |
| Failed | PENDING |
| Errors | PENDING |
| Skipped | PENDING |
| Test command used | PENDING |

---

### 1.3 Face Flow

#### 1.3.1 Enrollment

| Scenario | Result | Notes |
|---|---|---|
| Clear JPEG enrollment | PENDING | |
| Clear PNG enrollment | PENDING | |
| No-face image rejected | PENDING | |
| Duplicate enrollment handled | PENDING | |

#### 1.3.2 Group-photo Attendance

| Check | Result | Notes |
|---|---|---|
| Multiple faces detected | PENDING | |
| Correct identities matched | PENDING | |
| Attendance record created in DB | PENDING | |

#### 1.3.3 Manual Attendance with Audit Record

| Check | Result | Notes |
|---|---|---|
| Teacher can mark manually | PENDING | |
| Audit log entry created | PENDING | |
| Audit log fields (who, when, reason) | PENDING | |

---

### 1.4 Role-Based Access Control

| Role | Login Accepted? | Access Level Correct? |
|---|---|---|
| admin | PENDING | PENDING |
| teacher | PENDING | PENDING |
| student | PENDING | PENDING |
| hos (should be rejected) | PENDING | PENDING |
| hop (should be rejected) | PENDING | PENDING |
| mentor (should be rejected) | PENDING | PENDING |

---

### 1.5 Student Portal

| Check | Result | Notes |
|---|---|---|
| Attendance % in range [0, 100] | PENDING | |
| All 5 subjects visible | PENDING | |
| CIE 1 marks + eligibility text shown | PENDING | |
| CIE 2 marks + eligibility text shown | PENDING | |
| CIE 3 marks + eligibility text shown | PENDING | |
| Subject drill-down works | PENDING | |

---

### 1.6 Notifications

| Check | Result | Notes |
|---|---|---|
| Admin can send to all roles | PENDING | |
| Teacher send restricted to own subject | PENDING | |
| Student in another subject cannot see teacher's notification | PENDING | |
| Students cannot send notifications | PENDING | |

---

### 1.7 Study Coach

| Check | Result | Notes |
|---|---|---|
| Response with configured LLM provider | PENDING | |
| Rule-based fallback (no key / no internet) | PENDING | |
| No raw error shown to user | PENDING | |
| Fallback triggers correctly | PENDING | |

---

### 1.8 Security Checks

| Check | Result | Notes |
|---|---|---|
| `.env` in .gitignore (`git check-ignore .env`) | PENDING | |
| API keys in git history | PENDING | |
| API keys in log files | PENDING | |
| Student A reading Student B's data via API | PENDING | |
| Rate limiting active | PENDING | |
| XSS in notification text | PENDING | |

---

### 1.9 Counts from Code

| Item | Count | Source File |
|---|---|---|
| API routes | PENDING | PENDING |
| DB tables | PENDING | PENDING |
| Tests | PENDING | PENDING |
| Roles | PENDING | PENDING |
| Python modules | PENDING | PENDING |

---

## PART 2 — FINAL AUDIT

---

### Section A — Scorecard

> Feature | Status | Evidence | Demo-safe?

| Feature | Status | Evidence | Demo-safe? |
|---|---|---|---|
| Face detection | PENDING | PENDING | PENDING |
| Embedding / matching (512-d) | PENDING | PENDING | PENDING |
| Classifier cascade | PENDING | PENDING | PENDING |
| Liveness detection | PENDING | PENDING | PENDING |
| Tracking | PENDING | PENDING | PENDING |
| Attendance (face-based) | PENDING | PENDING | PENDING |
| Manual override | PENDING | PENDING | PENDING |
| Audit log | PENDING | PENDING | PENDING |
| CIE policy engine | PENDING | PENDING | PENDING |
| Risk engine | PENDING | PENDING | PENDING |
| SHAP explainability | PENDING | PENDING | PENDING |
| Notifications | PENDING | PENDING | PENDING |
| Study coach | PENDING | PENDING | PENDING |
| 3-role RBAC (admin/teacher/student) | PENDING | PENDING | PENDING |
| Scheduler | PENDING | PENDING | PENDING |
| Student portal | PENDING | PENDING | PENDING |
| Admin portal | PENDING | PENDING | PENDING |
| Teacher portal | PENDING | PENDING | PENDING |

---

### Section B — Strong Points

[IN PROGRESS — To be filled after Part 1 evidence gathering]

1. [PENDING]
2. [PENDING]
3. [PENDING]
4. [PENDING]
5. [PENDING]

---

### Section C — Weak Points (Ranked by Exhibition Risk)

[IN PROGRESS — To be filled after Part 1 evidence gathering]

| Rank | Weakness | What an examiner would say | Honest answer |
|---|---|---|---|
| 1 | PENDING | PENDING | PENDING |
| 2 | PENDING | PENDING | PENDING |
| 3 | PENDING | PENDING | PENDING |
| 4 | PENDING | PENDING | PENDING |
| 5 | PENDING | PENDING | PENDING |

---

### Section D — Bugs and Risks Found in Part 1

[IN PROGRESS]

| # | Description | Severity | Steps to Reproduce | Demo Workaround |
|---|---|---|---|---|
| — | PENDING | — | — | — |

---

### Section E — Consistency Check Across Documents

[IN PROGRESS — Documents to compare: REPORT.md, REPORT_ch*.md, PAPER.tex, README.md, AUDIT.md, TODO_FOR_ME.md]

| Claim / Number | REPORT.md | REPORT_ch*.md | PAPER.tex | README.md | AUDIT.md | Verdict |
|---|---|---|---|---|---|---|
| PENDING | — | — | — | — | — | — |

---

### Section F — Exhibition Readiness Checklist

[IN PROGRESS]

| Item | Status | Notes |
|---|---|---|
| Laptop charged + charger packed | PENDING | |
| Offline mode / local LLM fallback works | PENDING | |
| Backup demo video recorded | PENDING | |
| Test images prepared (clear, group, no-face) | PENDING | |
| All demo accounts created (admin/teacher/student) | PENDING | |
| Ports confirmed open (backend, frontend) | PENDING | |
| `.env` present and not committed | PENDING | |
| Models present locally | PENDING | |
| Demo script printed / available | PENDING | |
| Slide deck / poster ready | PENDING | |

---

### Section G — "Do Before 7 Nov" Priority List

[IN PROGRESS — Max 10 items, ordered by impact]

| Priority | Task | Estimated Time |
|---|---|---|
| 1 | PENDING | PENDING |
| 2 | PENDING | PENDING |
| 3 | PENDING | PENDING |
| 4 | PENDING | PENDING |
| 5 | PENDING | PENDING |

---

*This file will be fully populated by the audit workflow steps. Last updated: 2026-11-03 11:54 IST*
