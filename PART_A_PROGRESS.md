# VISTA Part A Progress

## Baseline Commit
Hash: 01d28dfbdb8197543e691ed402c5d561b78002ac

---

## Task 2: Test Fixes

12 failing tests fixed in commit `8528afa6`.

| Test | Fix Description | File:Line Changed |
|------|----------------|-------------------|
| `test_task1_and_task2_all_7th_sem_subjects_visible` | Added `_seed_7th_sem_curriculum(db)` call in conftest so 22AIU7xx subjects exist | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_task1_student_authorization_strict_own_data` | Same conftest fix — subject 22AIU701 now found in test DB | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_task1_subject_drilldown_marks_and_source_badges` | Same conftest fix + `_ensure_real_face_session` inserts required face record | `tests/conftest.py` — new file |
| `test_task5_future_date_rejected` | `rajeshwari@vista.local` role set to `teacher` by `_seed_7th_sem_curriculum`; role guard now passes, future-date check returns 400 | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_task5_manual_attendance_creates_audit_log` | Subject 22AIU701 seeded; `_normalize_subject_id` resolves it | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_task5_marks_mandatory_reason` | Rajeshwari role fix → hits REASON_REQUIRED check | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_task5_marks_out_of_range` | Rajeshwari role fix → hits SCORE_OUT_OF_RANGE check | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_task5_teacher_subject_scope_enforcement` | Rajeshwari now `teacher`; attempt on 22AIU702 (not her subject) correctly returns SUBJECT_SCOPE 403 | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_teacher_subject_notification_visibility` | Rajeshwari role fix → `create_notification` role guard passes | `vista/backend/tests/conftest.py` — `setup_db` fixture |
| `test_mark_attendance_accepts_personal_model_result` | Added `skip_liveness=False` param to monkeypatch lambda | `vista/backend/tests/test_personal_model_attendance.py:24` |
| `test_mark_batch_accepts_personal_model_results` | Added `skip_liveness=False` param to monkeypatch lambda | `vista/backend/tests/test_personal_model_attendance.py:43` |
| `test_recompute_risk` | Added missing `notify_high_risk()` function to notifications.py (ImportError fix) | `vista/backend/app/routes/notifications.py` — end of file |

**Production bug fixes applied:**
- `vista/backend/app/routes/notifications.py` — added `notify_high_risk(db, student_id, student_name, risk_level, reasons)` internal helper (fixes ImportError in risk.py)
- `vista/backend/tests/test_personal_model_attendance.py` — two lambda signatures fixed (test infrastructure bug with production API signature mismatch)
- `tests/conftest.py` — new root-level conftest with `_seed_7th_sem_curriculum`, `_run_demo_seed`, `_ensure_real_face_session`
- `vista/backend/tests/conftest.py` — added `_seed_7th_sem_curriculum(db)` to seed 7th-sem subjects + set rajeshwari's role to `teacher`

---

## Task 3: Attendance % Fix

File changed: `vista/backend/app/routes/students.py:251`

Before:
```python
"attendance_pct": round(present / len(session_dates) * 100, 1) if session_dates else 0,
```

After:
```python
"attendance_pct": min(100.0, round(present / len(session_dates) * 100, 1)) if session_dates else 0,
```

Verification: Regression test `test_attendance_pct_never_exceeds_100` added in `tests/test_audit_fixes.py` — all students att_pct <= 100 confirmed. Test passes in final run.

---

## Task 4: Legacy Subjects Deactivated

Deactivated: 22CDN709, ML101, DBMS, CN, OS, SE

Active subjects (5):
| Code | Name |
|------|------|
| 22AIU701 | Deep Learning |
| 22AIU702 | Generative AI |
| 22AIT703 | Data Engineering and Analytics |
| 22AIT704C | Data Security and Privacy |
| 22AIP706 | Major Project Phase-II |

Legacy subjects set to `is_active=0` in `vista_dev.db` via `_seed_7th_sem_curriculum` / `reconcile_current_roster` called at startup and in test conftest. Confirmed via direct DB query: all 6 legacy subjects have `is_active=0`.

---

## Task 5: Coach Fallback

coach can 500: NO

Evidence: `vista/backend/app/routes/coach_service.py:370-389` — both `_call_openrouter` and `_call_ollama` already swallow all exceptions internally and return `None`. The route handler wraps `chat_with_coach` in try/except → HTTP 400 (not 500) on any exception that escapes.

Fix applied: YES — commit `b8aa01df` added outer try/except inside `chat_with_coach` so any exception escaping the callers (e.g. json.dumps serialization failure building prompt context) logs a warning and sets `coach_reply = None`, triggering the existing deterministic fallback (`if not coach_reply: coach_reply = generate_rule_based_reply(...)`) instead of propagating to the route handler.

The deterministic engine and all existing fallback logic are preserved unchanged. Verified: all coach tests pass in final run (3 tests in `TestCoachService`).

---

## Task 6: Repo Hygiene

docs_backup_final tracked: YES — removed from git tracking (commit `762a7baa`). All 69 files under `docs_backup_final/` removed from the index; directory itself remains on disk but is now gitignored.

.gitignore entries added:
- `docs_backup_final/`
- `baseline_test_run.txt`
- `test_baseline.txt`
- `PART_A_PROGRESS.md`

---

## Task 7: Final Test Run

Collected: 78, Passed: 78, Failed: 0

All suites GREEN — no remaining failures.

| Test File | Tests | Result |
|-----------|-------|--------|
| `tests/test_audit_fixes.py` | 12 | PASS |
| `tests/test_features_1_and_2.py` | 16 | PASS |
| `vista/backend/tests/test_attendance.py` | 5 | PASS |
| `vista/backend/tests/test_auth.py` | 7 | PASS |
| `vista/backend/tests/test_dashboard.py` | 4 | PASS |
| `vista/backend/tests/test_enroll.py` | 3 | PASS |
| `vista/backend/tests/test_export.py` | 3 | PASS |
| `vista/backend/tests/test_personal_model_attendance.py` | 2 | PASS |
| `vista/backend/tests/test_risk.py` | 8 | PASS |
| `vista/backend/tests/test_students.py` | 4 | PASS |
| `vista/vision/test_recognize.py` | 7 | PASS |
| `vista/ml/test_risk_engine.py` | 7 | PASS |

Non-fatal warnings only (PendingDeprecationWarning python_multipart, DeprecationWarning on_event×3, PytestReturnNotNoneWarning in test_recognize.py×7).

---

## Verified Numbers

- students: total=70, active=65, enrolled_with_embeddings=39
- tables=27, subjects_all=11 (6 legacy deactivated, 5 active)
- routes=122

---

## Face Enrollment Table

| USN | Name | Has Embedding |
|-----|------|---------------|
| 1DA23AI042 | Saheel Pradhan | YES |
| 1DA24AI403 | Mohammed Ayan | YES |
| 1DA23AI050 | Sujal Agrahari | YES |
| 1DA23AI009 | Aryan Raj Singh | YES |
