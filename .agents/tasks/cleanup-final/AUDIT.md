# Cleanup audit (Phase 2, step 4)

Audit only. Nothing was deleted. Repo state: `main` at `556927ce1` plus untracked files listed below.

## Method

- Tracked: `git ls-files -- <path>`. Last commit date: `git log -1 --format=%cs -- <path>`.
- References: `git grep -l -I -F <basename>` over all tracked text files (code, configs, tests, docs, README, `start_vista.ps1`, `vista/Dockerfile`, `vista/docker-compose.yml`), excluding this audit and the file itself. Python imports checked with `git grep -E "(import|from) .*<stem>"`. The two report .docx files (`3Report (1).docx`, `3Report (1)_updated.docx`) were searched as XML text for every script name below: 0 hits.
- No CI exists (no `.github/`, no pipeline files). Only Dockerfiles and `docker-compose.yml` under `vista/`, none mention any candidate.
- "Agent notes" below means files under `.agents/tasks/`, `DOCS_SYNC_REPORT.md`, `NEEDS_YOUR_INPUT.md`, `VISTA_RESEARCH_AUDIT/*`, which describe the repo but do not run anything.
- Raw scan output: `_ref_scan.json` (same folder), produced by `_ref_scan.ps1`. The helper scripts `_ref_scan.ps1`, `_dup_scan.ps1`, `_bak_hist.ps1`, `_docx_scan.py` and `_ref_scan.json` in this folder are audit scratch and can be removed with the rest.

## Table

Class: KEEP / SAFE TO DELETE (SAFE) / UNSURE (keep). Date is the last commit date, `-` = untracked.

| path | tracked? | last commit | references found | class | reason |
|---|---|---|---|---|---|
| `tests/*`, `vista/backend/tests/*`, `vista/vision/test_*.py`, `vista/ml/test_risk_engine.py` | yes | 2026-11 | pytest suites | KEEP | real test suites |
| `vista/backend/mock_server/`, `vista/backend/app/routes/mentor.py` | yes | - | - | KEEP | user decided earlier |
| `train_from_npz.py` | yes | 2026-09-12 | 18 (CLAIMS_TABLE, PAPER_TODO, audit docs) | KEEP | reproduces baseline numbers cited in docs |
| `train_expanded_v3.py`, `build_npz_v3.py`, `regenerate_aug_v3.py`, `audit_v3_a.py`, `audit_v3_b.py` | yes | 2026-11-16/17 | run_chain.ps1, run_splitB.ps1, FIX_LOG, make_report_graphs.py (imports), evaluate_v3.py (imports) | KEEP | produce final 29-class results |
| `training_results/expanded_v3/{evaluate_v3,threshold_check,make_report_graphs,make_graphs_v3,make_gallery_chart,make_risk_chart,make_report_inputs_md,check_unenrolled_photos}.py` | yes | 2026-11-17 | REPORT_INPUTS_FINAL.md, COMPARISON_REPORT.md, REPORT_CHARTS_RISK_GALLERY.md, make_report_inputs_md.py | KEEP | reproduce report numbers and graphs |
| `training_results/expanded_v3/{run_chain,run_splitB}.ps1`, `regen_progress.json`, `e2e_decider.json`, `e2e_results.json`, `eval_results.json`, `history_split*.json`, `splits_*.json`, `diagnosis/*`, `graphs_report/*` (tracked) | yes | 2026-11-17 | FIX_LOG, COMPARISON_REPORT, PROMOTION_LOG, regenerate_aug_v3.py | KEEP | training launchers, results and data artifacts |
| `evaluation/*.py`, `evaluation/results/*.json` | yes | 2026-11 | - | KEEP | reproduces gallery and risk-model numbers |
| `regenerate_npz.py` | yes | 2026-09-12 | 9 (train_from_npz.py, audit docs, s4-npz.md) | KEEP | builds baseline npz used by `train_from_npz.py` |
| `vista/vision/facial_pipeline.py`, `vista/ml/*`, `vista/backend/*`, `start_vista.ps1`, `start_vista.bat`, `vista/Dockerfile`, `docker-compose.yml`, `.env.example`, `.gitignore`, `.gitattributes`, `scripts/backup_db.ps1`, `scripts/seed_demo_data.py`, `scripts/setup_7th_sem_subjects.py`, `scripts/seed_timetable.py` | yes | various | tests/conftest.py imports seed_demo_data; seed_demo_data imports setup_7th_sem_subjects; tests/test_timetable.py imports seed_timetable; `start_vista.bat` is the Windows entry point | KEEP | entry points, app code, config, test helpers, DB backup utility |
| `1report/apply_report_updates.py` | yes | 2026-11-17 | none; imports only numpy, matplotlib, PIL, python-docx (no scratch scripts) | KEEP | reproducible report edit |
| `1report/3Report (1).docx`, `_updated.docx`, `_updated.pdf`, `EDIT_PLAN.md`, `CHANGELOG_REPORT_UPDATE.md` | yes | 2026-11-17 | - | KEEP | report and its change log |
| `paper/*`, `figures/*.png`, `evaluation/*`, `vista/docs/*`, `vista/md-docs/*`, `README.md`, root `*.md` reports | yes | various | - | KEEP | docs and data (see UNSURE for duplicates) |
| `scripts/check_classes_and_assignments.py` | yes | 2026-11-07 | 0 | SAFE | one-off sqlite check, hardcoded `vista_dev.db` |
| `scripts/check_teacher_subjects.py` | yes | 2026-11-07 | 0 | SAFE | one-off sqlite check |
| `scripts/check_teachers.py` | yes | 2026-11-16 | 0 | SAFE | one-off sqlite check, prints teacher rows |
| `scripts/search_db_3rd_year.py` | yes | 2026-11-07 | 0 | SAFE | ad hoc DB search |
| `scripts/search_frontend_3rd.py` | yes | 2026-11-07 | 0 | SAFE | ad hoc source search |
| `scripts/verify_attendance_stats.py` | yes | 2026-11-16 | 0 | SAFE | one-off verification against dev DB |
| `scripts/fix_attendance_logic.py` | yes | 2026-11-07 | 0 | SAFE | one-shot source patcher, already applied |
| `scripts/fix_attendance_stats.py` | yes | 2026-11-07 | 0 | SAFE | one-shot source patcher |
| `scripts/fix_security_tests.py`, `scripts/fix_security_tests_v2.py` | yes | 2026-11-16 | 0 | SAFE | one-shot patchers that rewrite `tests/test_security_part5.py` |
| `scripts/add_academic_record_test.py` | yes | 2026-11-07 | 0 | SAFE | one-shot patcher that inserts a test into `tests/test_audit_fixes.py` |
| `scripts/patch_db.py` | yes | 2026-11-16 | 0 | SAFE | one-shot patcher; result lives in `app/db.py` (`_run_migrations`) |
| `scripts/patch_reports_part4.py`, `scripts/patch_reports_v2.py` | yes | 2026-11-16 | 0 | SAFE | one-shot patchers for `routes/reports.py`; re-running could duplicate code |
| `scripts/register_timetable.py`, `scripts/update_models.py` | yes | 2026-11-16 | 0 | SAFE | one-shot patchers for `routes/__init__.py` and `models/timetable.py` |
| `scripts/run_db_migration.py` | yes | 2026-11-16 | 0 | SAFE | same column list is now applied by `app/db.py::_run_migrations` at startup |
| `update_audit_and_viva.py`, `update_part_b.py` | yes | 2026-11-04 | 0 | SAFE | one-off doc rewriters; their output is committed |
| `pytest_final.txt` | yes | 2026-11-07 | 0 | SAFE | pasted pytest output (Python 3.11 system install) |
| `.agents/tasks/vista-part-a-2026-11-07/final-test-run.txt` | yes | 2026-11-03 | 0 | SAFE | pytest output dump |
| `.agents/tasks/dataset-expansion/s1_audit.py` | yes | 2026-11-17 | 0 (its output `s1-audit.md` is kept) | SAFE | one-off agent script, superseded by `audit_v3_a/b.py` |
| `.agents/tasks/dataset-expansion/s3-progress-advanced.old1.json` | yes | 2026-11-17 | 0 | SAFE | `.old1` progress snapshot |
| `train_expanded.py` | yes | 2026-11-17 | agent notes (s4-npz, s5-launch) and v2 diagnosis docs/`diag_split.py` (text mention only). No import, no README, no docs, no report, no v3 code | SAFE | trainer of the failed v1 32-class run, superseded by `train_expanded_v3.py` |
| `regenerate_npz_expanded.py` | yes | 2026-11-17 | agent notes (s4-npz.md, part_e.md) only | SAFE | npz builder of the failed v1 run, superseded by `build_npz_v3.py` |
| `training_results/expanded/smoke/{history_expanded_splitA.json,results_expanded_splitA.txt,confusion_matrix_expanded_splitA.png,training_curve_expanded_splitA.png}` | yes | 2026-11-17 | only `train_expanded.py` (also SAFE) | SAFE | smoke-run outputs of the failed run |
| `training_results/expanded_v3/smoke/history_splitA.json` | yes | 2026-11-17 | one agent note | SAFE | smoke-run output |
| `training_results/expanded_v3/e2e_cleanup.py` | yes | 2026-11-17 | 0 | SAFE | one-off DB cleanup of test rows |
| `training_results/expanded_v3/e2e_cleanup2.py` | yes | 2026-11-17 | PROMOTION_LOG.md (commit-hash note only) | SAFE | one-off DB cleanup of test rows |
| `training_results/expanded_v3/poll.log` | yes | 2026-11-17 | 0 | SAFE | training poller log |
| `training_results/expanded_v3/e2e_backend.pid`, `splitB.pid` | yes | 2026-11-17 | launch scripts write them at run time | SAFE | stale process-id files |
| `figures/.mplconfig/fontlist-v390.json` | yes | 2026-11-04 | `render_all_diagrams.py` sets `MPLCONFIGDIR` to this folder | SAFE | matplotlib font cache, regenerated automatically |
| `vista/ml/__pycache__/*.pyc` (11), `vista/vision/__pycache__/*.pyc` (9), `vista/backend/tests/__pycache__/*.pyc` (15) | yes | 2026-11-03 | 0 | SAFE | compiled bytecode committed by mistake (35 files) |
| `1report/dump_docx.py`, `find_pages.py`, `fix2.py`, `fix3.py`, `fix_and_log.py`, `fmt_probe.py`, `montage.py`, `render.ps1`, `verify_report.py` | no (`??`, not ignored) | - | only `EDIT_PLAN.md` mentions `dump_docx.py` and `fmt_probe.py` in prose; no code imports them | SAFE | scratch from the report edit session |
| `1report/_x/`, `1report/_x.zip`, `1report/_dump.txt`, `1report/_fmt.txt` | no (ignored) | - | 0 | SAFE | unzipped docx and text dumps |
| `1report/3Report (1)_original_backup.docx` | no (ignored) | - | 0 | SAFE | MD5 identical to tracked `1report/3Report (1).docx` |
| `training_results/expanded_v3/graphs_report/_old_gallery_chart_extracted.png`, `_old_risk_chart_extracted.png` | no (ignored) | - | 0 | SAFE | images extracted from the old report |
| `training_results/expanded_v3/e2e_backend.log`, `e2e_backend.err.log`, `regen_out.log`, `regen_err.log` | no (ignored) | - | 0 | SAFE | run logs |
| `.agents/tasks/dataset-expansion/s4-regen.log` | no (ignored) | - | 0 | SAFE | run log |
| `backup/` | no (empty dir) | - | `.gitignore` only | SAFE | empty folder, the only empty folder found (outside `.venv`, `node_modules`, `.git`) |
| `.pytest_cache/` | no (ignored) | - | - | SAFE | cache, regenerated |
| `training_results/train.py` | yes | 2026-09-12 | 25; imported by `train_from_npz.py`, `train_expanded_v3.py`, `train_expanded.py` | KEEP | shared module of the live trainers |
| `training_results/train_splitA.py` | yes | 2026-09-12 | only an agent inventory note and its own output `results_splitA.txt` | UNSURE | no doc references it, but it is the twin of `train_splitB.py` and the user said to keep all three until confirmed |
| `training_results/train_splitB.py` | yes | 2026-09-12 | `DOCS_SYNC_REPORT.md:40,59`, `NEEDS_YOUR_INPUT.md:23`, 2 audit notes | UNSURE | referenced by docs; superseded by `train_from_npz.py` and v3 but doc references remain. Not deleted per the rule |
| `training_results/{data_split_log,data_split_npz_log,image_count_report,results_splitA,results_splitB,results_npz_splitA,results_npz_splitB}.txt` | yes | 2026-09-12/15 | audit docs, `train_from_npz.py`, `train_splitA/B.py` | UNSURE | baseline result logs cited by `VISTA_RESEARCH_AUDIT/*` |
| `augment_missing.py` | yes | 2026-11-17 | agent notes only (s3-augment.md, part_e.md). v3 code does not import or call it | UNSURE | not referenced by v3, but it may have produced the augmented data folder v3 reads |
| `training_results/expanded_v2/diagnosis/{diag_split,split_v2,part_b_analyze,part_b_quality,part_d,part_e_check,part_e_orig}.py` | yes | 2026-11-17 | each cited only by its own sibling diagnosis `.md` | UNSURE | scripts of the superseded v2 diagnosis; they reproduce the kept diagnosis docs |
| `training_results/expanded_v2/diagnosis/*.md/*.csv`, `expanded_v1_failed/*`, `expanded/*.json`, `baseline_before_expansion/*`, `expanded/smoke/data_split_expanded_log.txt` | yes | 2026-11-17 | COMPARISON_REPORT.md, diag_split.py, part_a_c_f.md | UNSURE | history of failed runs; cited by kept docs |
| `training_results/expanded_v3/e2e_test.py`, `e2e_launch.ps1`, `promo_check.py` | yes | 2026-11-17 | PROMOTION_LOG.md (e2e_test), PROMOTION_ASSESSMENT.md (promo_check); `e2e_launch.ps1` 0 | UNSURE | reproducibility of the promotion check |
| `scripts/seed_multi_classes.py` | yes | 2026-11-16 | 0 | UNSURE | demo-data seeder, may still be used by hand |
| `build_final_report_suite.py` | yes | 2026-11-04 | 0 | UNSURE | generates `FINAL_REPORT.md`, which is tracked |
| `render_all_diagrams.py` | yes | 2026-11-04 | 0 | UNSURE | generates `figures/fig_4_*.png` that are tracked |
| `Model,algorithmpages.txt` | yes | 2026-11-07 | 0 | UNSURE | badly named, mojibake text listing `vista/ml` functions; content may be wanted |
| `z_next_update.md`, `connectingfrontend.MD` | yes | 2026-11-07 / 2026-10-30 | `connectingfrontend.MD` in DOCS_SYNC_REPORT; `z_next_update.md` 0 | UNSURE | roadmap and integration notes |
| `new_students.csv` | yes | 2026-11-17 | PROMOTION_LOG.md | UNSURE | contains USNs and names (PII); referenced by a log |
| `.agents/tasks/dataset-expansion/pip_freeze_before_cuda.txt`, `train_status.json`, `train_status_v3.json` | yes | 2026-11-17 | cuda_ready.md, s5-launch.md | UNSURE | referenced by agent notes |
| `vista/DEMO_SCRIPT.md` vs `vista/docs/DEMO_SCRIPT.md`; `vista/PROJECT_REPORT.md` vs `vista/docs/PROJECT_REPORT.md` | yes | 2026-10-30 / 2026-11-04 | README.md, VIVA_QA.md, FINAL_AUDIT.md, CHANGELOG_FINAL.md | UNSURE | duplicates by name but content differs (MD5, sizes 3886/3604 B and 15108/16974 B); README links them |
| `REPORT.md` / `REPORT_ch*.md` / `FINAL_REPORT.md`; `AUDIT.md` / `FINAL_AUDIT.md` | yes | 2026-11 | README, CHANGELOGs | UNSURE | overlapping reports, contents differ; not safe to merge unreviewed |
| `dataset/1DA23AI004/TEMP`, `1DA23AI011/TEMP`, `1DA23AI024/TEMP`, `1DA23AI036/TEMP`, `1DA23AI049/TEMP` | yes | 2026-08-26 | `audit_v3_b.py:271` says non-image `TEMP` files are ignored by the image filter; no code reads them | UNSURE | each is a 2-byte file (`0D 0A`), not a folder and not an image; harmless, but the dataset is protected |
| `docs_backup_final/` (57 files, 0.91 MB) | no (ignored, `.gitignore:80`) | - | doc-update-plan.md, FINAL_AUDIT.md, PART_A_PROGRESS.md (prose) | UNSURE | 14 files identical to tracked docs, 27 of the 29 differing files exist in git history, but `DEMO_SCRIPT.md` and `PROJECT_REPORT.md` copies do not; 14 files have no tracked counterpart (third-party doc copies, PAPER.md/PAPER.tex) |
| `vista/backend/vista_dev_preA3.db`, `vista_dev_BACKUP_before_tests.db`, `vista_dev_pre_v3_promotion.db` | no (ignored) | - | PROMOTION_LOG.md names `vista_dev_pre_v3_promotion.db` | UNSURE | untracked DB backups, do not delete |
| `db_backup/*` (tracked `.sql`, ignored `.db` dirs `20231104_1403`, `backup_20261031_0540`, `backup_20261031_0725`), `test_vista.db`, `vista_dev.db`, `vista/vista_dev.db`, `vista/backend/vista_dev.db` | mixed | 2026-10-31 | `scripts/backup_db.ps1`, `tests/conftest.py`, `.env.example` | UNSURE | databases, do not delete |
| `training_results/**/*.pth`, `training_results/expanded*/smoke/*.pth`, `data/processed/*.npz`, `vista/ml/model.pkl` | mixed | - | - | KEEP | model and data artifacts, off limits |
| `training_results/expanded_v3/{train_split*.log,train_split*.err.log,build_npz_v3.log}`, `training_results/expanded*/train_split*.log` | no (ignored) | - | train_log_split*.txt, COMPARISON_REPORT.md | UNSURE | raw training logs of the final and failed runs |
| `training_results/expanded_v3/graphs_report/USN_to_ID_PRIVATE.csv` | no (ignored) | - | make_report_graphs.py | KEEP | private ID mapping, must stay ignored |
| `.kiro/` | no (ignored) | - | - | KEEP | tool configuration |

## SAFE TO DELETE

### Tracked files (`git rm`)

```
scripts/check_classes_and_assignments.py
scripts/check_teacher_subjects.py
scripts/check_teachers.py
scripts/search_db_3rd_year.py
scripts/search_frontend_3rd.py
scripts/verify_attendance_stats.py
scripts/fix_attendance_logic.py
scripts/fix_attendance_stats.py
scripts/fix_security_tests.py
scripts/fix_security_tests_v2.py
scripts/add_academic_record_test.py
scripts/patch_db.py
scripts/patch_reports_part4.py
scripts/patch_reports_v2.py
scripts/register_timetable.py
scripts/update_models.py
scripts/run_db_migration.py
update_audit_and_viva.py
update_part_b.py
pytest_final.txt
train_expanded.py
regenerate_npz_expanded.py
.agents/tasks/vista-part-a-2026-11-07/final-test-run.txt
.agents/tasks/dataset-expansion/s1_audit.py
.agents/tasks/dataset-expansion/s3-progress-advanced.old1.json
training_results/expanded/smoke/history_expanded_splitA.json
training_results/expanded/smoke/results_expanded_splitA.txt
training_results/expanded/smoke/confusion_matrix_expanded_splitA.png
training_results/expanded/smoke/training_curve_expanded_splitA.png
training_results/expanded_v3/smoke/history_splitA.json
training_results/expanded_v3/e2e_cleanup.py
training_results/expanded_v3/e2e_cleanup2.py
training_results/expanded_v3/poll.log
training_results/expanded_v3/e2e_backend.pid
training_results/expanded_v3/splitB.pid
figures/.mplconfig/fontlist-v390.json
vista/ml/__pycache__/            (11 .pyc files)
vista/vision/__pycache__/        (9 .pyc files)
vista/backend/tests/__pycache__/ (15 .pyc files)
```

Follow-ups for the delete step (not done here):

- After removing the `__pycache__` files and the matplotlib cache, confirm `.gitignore` has `__pycache__/`, `*.pyc` and `figures/.mplconfig/`.
- Text mentions of removed scripts remain in agent notes and `DOCS_SYNC_REPORT.md` / `training_results/expanded_v2/diagnosis/*.md` (`train_expanded.py`). They are history, not links; leave them or add a one-line note.
- `training_results/expanded_v2/diagnosis/diag_split.py` quotes `train_expanded.split_npz` in comments only (no import), so it still runs after removal.

### Untracked scratch from recent agent sessions (`Remove-Item`)

```
1report\dump_docx.py
1report\find_pages.py
1report\fix2.py
1report\fix3.py
1report\fix_and_log.py
1report\fmt_probe.py
1report\montage.py
1report\render.ps1
1report\verify_report.py
1report\_x\                              (directory)
1report\_x.zip
1report\_dump.txt
1report\_fmt.txt
1report\3Report (1)_original_backup.docx (identical to the tracked original)
training_results\expanded_v3\graphs_report\_old_gallery_chart_extracted.png
training_results\expanded_v3\graphs_report\_old_risk_chart_extracted.png
training_results\expanded_v3\e2e_backend.log
training_results\expanded_v3\e2e_backend.err.log
training_results\expanded_v3\regen_out.log
training_results\expanded_v3\regen_err.log
.agents\tasks\dataset-expansion\s4-regen.log
.agents\tasks\cleanup-final\_ref_scan.ps1
.agents\tasks\cleanup-final\_ref_scan.json
.agents\tasks\cleanup-final\_dup_scan.ps1
.agents\tasks\cleanup-final\_bak_hist.ps1
.agents\tasks\cleanup-final\_docx_scan.py
backup\                                  (empty directory)
.pytest_cache\
```

## UNSURE (keep)

- `training_results/train_splitA.py`, `training_results/train_splitB.py`: `train_splitB.py` is named in `DOCS_SYNC_REPORT.md` and `NEEDS_YOUR_INPUT.md`; the user's earlier instruction was to keep them until confirmed. They are superseded by `train_from_npz.py` and the v3 trainer, and neither is named in the two report .docx files or in README, so they can go once the user confirms and those two doc lines are edited.
- `training_results/*.txt` baseline logs (7 files), `training_results/train.py` stays KEEP (imported).
- `augment_missing.py`
- `training_results/expanded_v2/diagnosis/*.py` (7 scripts) and the v2/v1 diagnosis docs and logs
- `training_results/expanded_v3/e2e_test.py`, `e2e_launch.ps1`, `promo_check.py`
- `scripts/seed_multi_classes.py`, `build_final_report_suite.py`, `render_all_diagrams.py`
- `Model,algorithmpages.txt`, `z_next_update.md`, `connectingfrontend.MD`
- `new_students.csv` (names and USNs)
- Duplicate-named docs: `vista/DEMO_SCRIPT.md` vs `vista/docs/DEMO_SCRIPT.md`; `vista/PROJECT_REPORT.md` vs `vista/docs/PROJECT_REPORT.md`; `REPORT*.md` vs `FINAL_REPORT.md`; `AUDIT.md` vs `FINAL_AUDIT.md`
- `.agents/tasks/dataset-expansion/{pip_freeze_before_cuda.txt,train_status.json,train_status_v3.json}`
- `dataset/1DA23AI004|011|024|036|049/TEMP` (2-byte non-image files, harmless, dataset protected)
- `docs_backup_final/` (two files not recoverable from git)
- Untracked DB backups: `vista/backend/vista_dev_preA3.db`, `vista/backend/vista_dev_BACKUP_before_tests.db`, `vista/backend/vista_dev_pre_v3_promotion.db`, plus `db_backup/*`, `test_vista.db`, `vista_dev.db`, `vista/vista_dev.db`, `vista/backend/vista_dev.db`
- Raw training logs and smoke `.pth` checkpoints (models: untouched)


## Deleted

Deleted in the commit "chore: remove dead scratch scripts and files". Tracked files were removed with `git rm` (recoverable from history). Untracked scratch was removed with `Remove-Item`.

### Tracked (git rm, 71 files)

```nscripts/check_classes_and_assignments.py
scripts/check_teacher_subjects.py
scripts/check_teachers.py
scripts/search_db_3rd_year.py
scripts/search_frontend_3rd.py
scripts/verify_attendance_stats.py
scripts/fix_attendance_logic.py
scripts/fix_attendance_stats.py
scripts/fix_security_tests.py
scripts/fix_security_tests_v2.py
scripts/add_academic_record_test.py
scripts/patch_db.py
scripts/patch_reports_part4.py
scripts/patch_reports_v2.py
scripts/register_timetable.py
scripts/update_models.py
scripts/run_db_migration.py
update_audit_and_viva.py
update_part_b.py
pytest_final.txt
train_expanded.py
regenerate_npz_expanded.py
.agents/tasks/vista-part-a-2026-11-07/final-test-run.txt
.agents/tasks/dataset-expansion/s1_audit.py
.agents/tasks/dataset-expansion/s3-progress-advanced.old1.json
training_results/expanded/smoke/history_expanded_splitA.json
training_results/expanded/smoke/results_expanded_splitA.txt
training_results/expanded/smoke/confusion_matrix_expanded_splitA.png
training_results/expanded/smoke/training_curve_expanded_splitA.png
training_results/expanded_v3/smoke/history_splitA.json
training_results/expanded_v3/e2e_cleanup.py
training_results/expanded_v3/e2e_cleanup2.py
training_results/expanded_v3/poll.log
training_results/expanded_v3/e2e_backend.pid
training_results/expanded_v3/splitB.pid
figures/.mplconfig/fontlist-v390.json
vista/backend/tests/__pycache__/__init__.cpython-311.pyc
vista/backend/tests/__pycache__/conftest.cpython-311-pytest-8.2.0.pyc
vista/backend/tests/__pycache__/conftest.cpython-311-pytest-8.2.2.pyc
vista/backend/tests/__pycache__/test_attendance.cpython-311-pytest-8.2.0.pyc
vista/backend/tests/__pycache__/test_attendance.cpython-311-pytest-8.2.2.pyc
vista/backend/tests/__pycache__/test_auth.cpython-311-pytest-8.2.0.pyc
vista/backend/tests/__pycache__/test_auth.cpython-311-pytest-8.2.2.pyc
vista/backend/tests/__pycache__/test_dashboard.cpython-311-pytest-8.2.0.pyc
vista/backend/tests/__pycache__/test_dashboard.cpython-311-pytest-8.2.2.pyc
vista/backend/tests/__pycache__/test_export.cpython-311-pytest-8.2.0.pyc
vista/backend/tests/__pycache__/test_export.cpython-311-pytest-8.2.2.pyc
vista/backend/tests/__pycache__/test_risk.cpython-311-pytest-8.2.0.pyc
vista/backend/tests/__pycache__/test_risk.cpython-311-pytest-8.2.2.pyc
vista/backend/tests/__pycache__/test_students.cpython-311-pytest-8.2.0.pyc
vista/backend/tests/__pycache__/test_students.cpython-311-pytest-8.2.2.pyc
vista/ml/__pycache__/__init__.cpython-311.pyc
vista/ml/__pycache__/__init__.cpython-314.pyc
vista/ml/__pycache__/explainer.cpython-311.pyc
vista/ml/__pycache__/features.cpython-311.pyc
vista/ml/__pycache__/features.cpython-314.pyc
vista/ml/__pycache__/risk_engine.cpython-311.pyc
vista/ml/__pycache__/risk_engine.cpython-314.pyc
vista/ml/__pycache__/test_risk_engine.cpython-311.pyc
vista/ml/__pycache__/test_risk_engine.cpython-314.pyc
vista/ml/__pycache__/train.cpython-311.pyc
vista/ml/__pycache__/train.cpython-314.pyc
vista/vision/__pycache__/__init__.cpython-311.pyc
vista/vision/__pycache__/detect.cpython-311.pyc
vista/vision/__pycache__/embed.cpython-311.pyc
vista/vision/__pycache__/enroll.cpython-311.pyc
vista/vision/__pycache__/liveness.cpython-311.pyc
vista/vision/__pycache__/match.cpython-311.pyc
vista/vision/__pycache__/recognize.cpython-311.pyc
vista/vision/__pycache__/test_recognize.cpython-311.pyc
vista/vision/__pycache__/tracker.cpython-311.pyc
```n
### Untracked (Remove-Item)

Everything listed under 'Untracked scratch from recent agent sessions' above, including the audit helper scripts, `backup\` and `.pytest_cache\`.

