# VISTA Part A — Test Fix Review
2025-07-14

**Verdict**: APPROVED

All 12 failing tests are addressed. The coder deviated from the plan's `reconcile_current_roster()` prescription and instead implemented a standalone `_seed_7th_sem_curriculum()` helper in both conftest files. This avoids deactivating `CS22B001–CS22B005` (CSE-3A students), which `reconcile_current_roster` would have done, breaking the pre-existing export and attendance tests. The production ImportError in `risk.py` is fixed by adding `notify_high_risk` to `notifications.py` (Plan Option A). No tests were skipped or marked xfail.

**Watch for:**
- `_run_demo_seed` in `tests/conftest.py` will produce no attendance rows for the real students (confirmed) — the filter `class_ == "4th Year AIML"` never matches `class_="AIML-4A"`. Tests pass currently because `_ensure_real_face_session` inserts the single face record the test requires, but any future test asserting more than one attendance record or a non-None CIE score will fail.
- Both conftest files define `scope="session", autouse=True` fixtures that call `Base.metadata.drop_all` on the same SQLite file. Running both test trees in one invocation would cause one fixture to wipe the database the other just populated (possible — depends on invocation order).

---

## High-level view

The substitute for `reconcile_current_roster` is a purpose-built helper that creates the `class-aiml-4a` section, all five 7th-sem subjects, five teacher accounts with `role="teacher"`, and their `TeacherSubjectAssignment` rows. This gives `rajeshwari@vista.local` the `teacher` role and a `22AIU701` assignment, unblocking the nine tests that were hitting the `mentor`-role 403 guard.

`_run_demo_seed` in `tests/conftest.py` intends to seed bulk attendance and CIE scores for the real students, but its filter `Student.class_ == "4th Year AIML" | Student.classroom_id == "class-aiml-4a"` never matches them (`class_="AIML-4A"`, `classroom_id="CSE-3A"`). The tests that depend on attendance data for `1DA24AI403` pass only because `_ensure_real_face_session` directly inserts the one face record the tests check. This is a fragile foundation for any future test that needs richer attendance data.

The `notify_high_risk` addition to `notifications.py` resolves the ImportError in `risk.py`. The two lambda fixes in `test_personal_model_attendance.py` are a one-token change each and require no further comment.

---

<details>
<summary>Issues (2)</summary>

1. **`_run_demo_seed` student filter mismatch** — `Student.class_ == "4th Year AIML"` never matches the seeded value `"AIML-4A"`, and `classroom_id == "class-aiml-4a"` never matches `"CSE-3A"`. Bulk attendance and CIE scores for `1DA24AI403` are not seeded. Current tests pass because of `_ensure_real_face_session`, but any test asserting more than one attendance record or a non-None `cie1`/`cie2` score will fail. Fix: add `Student.class_ == "AIML-4A"` to the filter.

2. **Double-fixture DB drop risk** — `tests/conftest.py` (`seed_test_db_for_root_tests`) and `vista/backend/tests/conftest.py` (`setup_db`) both call `Base.metadata.drop_all` on `sqlite:///./test_vista.db`. Running both directories in one `pytest` invocation causes the second fixture to destroy the first's setup. Currently latent because the plan runs them separately, but will surface if CI runs the full suite as one command. Fix: coordinate the two fixtures or gate the drop on whether tables already exist.

</details>

<details>
<summary>Details</summary>

### `_run_demo_seed` student filter mismatch (confirmed)

In `tests/conftest.py`, `_run_demo_seed` filters students with:

```python
students = db.query(Student).filter(
    (Student.class_ == "4th Year AIML") | (Student.classroom_id == "class-aiml-4a")
).all()
```

`seed_demo_data` in `db.py` creates the real students with `class_="AIML-4A"` and `classroom_id="CSE-3A"`. Neither condition matches. The function returns an empty list and seeds nothing.

`test_task1_subject_drilldown_marks_and_source_badges` asserts `len(att_records) > 0` and that the 2026-10-30 record has `source="face"`. This passes only because `_ensure_real_face_session` directly inserts that single `Attendance` row. The marks assertions (`cie1`/`cie2` key existence) pass because `evaluate_cie` always returns both keys regardless of whether scores exist in the database.

### Double-fixture DB drop conflict

`tests/conftest.py` defines `seed_test_db_for_root_tests` (scope=session, autouse). `vista/backend/tests/conftest.py` defines `setup_db` (scope=session, autouse). Both call `Base.metadata.drop_all(bind=engine)` and both point to `sqlite:///./test_vista.db`. When pytest collects both trees together, whichever fixture runs second will drop the database the first just populated. The two fixtures also diverge in setup depth: the root-level one runs `_run_demo_seed` and `_ensure_real_face_session`; the backend one does not. This means the two trees are not interchangeable, and running them together would produce different test results depending on collection order.

</details>

---

<details>
<summary>File map</summary>

| File | What changed |
|------|-------------|
| `tests/conftest.py` | New file — root-level test DB setup with `_seed_7th_sem_curriculum`, `_run_demo_seed`, `_ensure_real_face_session` |
| `vista/backend/tests/conftest.py` | Added `_seed_7th_sem_curriculum(db)` call and helper function to `setup_db` fixture |
| `vista/backend/app/routes/notifications.py` | Added `notify_high_risk()` internal helper function |
| `vista/backend/tests/test_personal_model_attendance.py` | Added `skip_liveness=False` parameter to both monkeypatch lambdas |

Full diff: `git diff HEAD~1 HEAD`

</details>
