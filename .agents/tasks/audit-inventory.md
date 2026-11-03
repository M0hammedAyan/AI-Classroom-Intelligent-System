# VISTA Project — Complete Repository Inventory
**Generated:** Phase 1 Research Audit  
**Repository root:** `d:\CipherTECH\Projects\AI-Classroom-Intelligent-System`  
**Project full name:** VISTA — Vision-based Intelligent Student Tracking & Academics  
**Institution:** Dr. Ambedkar Institute of Technology, Bengaluru (DSATM)  
**Team:** Mohammed Ayan (1DA24AI403), Saheel Pradhan (1DA23AI042), Aryan Raj Singh (1DA23AI009), Sujala Agrahari (1DA23AI050), Shrujan P (1DA22AI044)

---

## Directory Tree

```
AI-Classroom-Intelligent-System/                    ← project root
│
├── .agents/                                        ← workflow agent artifacts
│   └── tasks/
│       ├── doc-update-plan.md                      ← prior doc-correction planning document
│       └── vista-part-a-2026-11-07/
│           └── test-fix-plan.md                    ← prior test-fix planning document
│
├── .claude/                                        ← Claude AI settings
│   └── settings.local.json
│
├── .cursor/                                        ← Cursor IDE settings (not explored further)
│
├── .git/                                           ← Git repo (hidden)
│
├── .kiro/                                          ← Kiro AI dev environment settings
│   └── settings/
│       └── mcp.json
│
├── .pytest_cache/                                  ← pytest cache (root-level tests)
│
├── .venv/                                          ← primary Python virtual environment
├── .venv_old/                                      ← archived old virtual environment
├── .vscode/                                        ← VS Code editor settings
│
├── agumented data/                                 ← augmented face image dataset (20 student dirs)
│   ├── 1DA22AI402/                                 ← per-student subfolder (subfolders per source img)
│   ├── 1DA23AI001/
│   ├── 1DA23AI004/
│   ├── 1DA23AI005/
│   ├── 1DA23AI009/
│   ├── 1DA23AI011/
│   ├── 1DA23AI024/
│   ├── 1DA23AI025/
│   ├── 1DA23AI031/
│   ├── 1DA23AI033/
│   ├── 1DA23AI036/
│   ├── 1DA23AI042/
│   ├── 1DA23AI044/
│   ├── 1DA23AI047/
│   ├── 1DA23AI049/
│   ├── 1DA23AI050/
│   ├── 1DA23AI055/
│   ├── 1DA23AI059/
│   ├── 1DA24AI403/
│   └── 1DA24AI404/                                 ← 20,130 files total (~225 MB); aug_000.jpg–aug_NNN.jpg
│
├── data/                                           ← processed ML data
│   └── processed/
│       └── facial_pipeline_results.npz             ← LARGE: 1.15 GB compiled embeddings+images+metadata
│
├── dataset/                                        ← raw face image dataset (20 student dirs)
│   ├── 1DA22AI402/                                 ← per-student subfolder; raw camera images (IMG_*.jpg/jpeg)
│   ├── 1DA23AI001/
│   ├── 1DA23AI004/
│   ├── 1DA23AI005/
│   ├── 1DA23AI009/
│   ├── 1DA23AI011/
│   ├── 1DA23AI024/
│   ├── 1DA23AI025/
│   ├── 1DA23AI031/
│   ├── 1DA23AI033/
│   ├── 1DA23AI036/
│   ├── 1DA23AI042/
│   ├── 1DA23AI044/
│   ├── 1DA23AI047/
│   ├── 1DA23AI049/
│   ├── 1DA23AI050/
│   ├── 1DA23AI055/
│   ├── 1DA23AI059/
│   ├── 1DA24AI403/
│   └── 1DA24AI404/                                 ← 680 files total (~1.94 GB); mixed .jpg/.jpeg
│
├── db_backup/                                      ← timestamped database backups
│   ├── backup_20261031_0540/                       ← early backup (4 files: 2×.db + 2×.sql)
│   └── backup_20261031_0725/                       ← later backup (~6.8 MB .db, ~3.8 MB .sql each)
│
├── docs/                                           ← root-level documentation and screenshots
│   └── screenshots/                               ← system screenshots for reports (14 PNG files)
│
├── docs_backup_final/                              ← pre-audit snapshot archive of ALL docs (55 files, DO NOT EDIT)
│
├── evaluation/                                     ← evaluation scripts and results
│   ├── results/                                    ← JSON result artifacts
│   │   ├── cascade_ablation.json
│   │   ├── coach_groundedness.json
│   │   ├── latency_benchmark.json
│   │   ├── recognition_threshold_sweep.json
│   │   └── risk_model_evaluation.json
│   ├── benchmark_latency.py
│   ├── evaluate_coach_groundedness.py
│   ├── evaluate_recognition.py
│   └── evaluate_risk_model.py
│
├── paper/                                          ← research paper draft + figures + bibliography
│   ├── figures/
│   │   ├── architecture.mmd
│   │   ├── cascade_flow.mmd
│   │   ├── fig_cascade_ablation.pdf / .png
│   │   ├── fig_group_photo_latency.pdf / .png
│   │   ├── fig_threshold_sweep.pdf / .png
│   │   └── plot_results.py
│   ├── PAPER.md
│   ├── PAPER.tex
│   └── references.bib
│
├── scripts/                                        ← utility/seeding scripts
│   ├── seed_demo_data.py
│   └── setup_7th_sem_subjects.py
│
├── tests/                                          ← root-level integration test suite
│   ├── conftest.py
│   ├── test_audit_fixes.py
│   └── test_features_1_and_2.py
│
├── training_results/                               ← ResNet-50 training outputs (models, curves, logs)
│   ├── best_model_npz_splitA.pth          (94 MB)
│   ├── best_model_npz_splitB.pth          (94 MB)
│   ├── best_model_splitA.pth              (271 MB)
│   ├── best_model_splitB.pth              (271 MB)
│   ├── confusion_matrix_npz_splitA.png
│   ├── confusion_matrix_npz_splitB.png
│   ├── confusion_matrix_splitA.png
│   ├── confusion_matrix_splitB.png
│   ├── data_split_log.txt
│   ├── data_split_npz_log.txt
│   ├── image_count_report.txt
│   ├── results_npz_splitA.txt
│   ├── results_npz_splitB.txt
│   ├── results_splitA.txt
│   ├── results_splitB.txt
│   ├── train.py                           ← early training script (superseded by train_from_npz.py)
│   ├── train_splitA.py                    ← thin shim invoking train.py for split A
│   └── train_splitB.py                    ← thin shim invoking train.py for split B
│
├── vista/                                          ← main application source package
│   ├── backend/                                    ← FastAPI backend
│   │   ├── app/
│   │   │   ├── models/                             ← SQLAlchemy ORM models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── attendance.py
│   │   │   │   ├── audit.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── intervention.py
│   │   │   │   ├── notification.py
│   │   │   │   ├── organization.py
│   │   │   │   ├── student.py
│   │   │   │   ├── timetable.py
│   │   │   │   └── user.py
│   │   │   ├── routes/                             ← FastAPI route handlers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── academics.py
│   │   │   │   ├── admin.py
│   │   │   │   ├── attendance.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── coach.py
│   │   │   │   ├── dashboards.py
│   │   │   │   ├── enroll.py
│   │   │   │   ├── export.py
│   │   │   │   ├── lms.py
│   │   │   │   ├── mentor.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── risk.py
│   │   │   │   ├── student_portal.py
│   │   │   │   └── students.py
│   │   │   ├── services/
│   │   │   │   └── coach_service.py
│   │   │   ├── __init__.py
│   │   │   ├── audit.py
│   │   │   ├── cache.py
│   │   │   ├── cie_policy.py
│   │   │   ├── db.py
│   │   │   ├── main.py
│   │   │   ├── monitoring.py
│   │   │   ├── permissions.py
│   │   │   ├── scheduler.py
│   │   │   ├── tasks.py
│   │   │   └── websocket.py
│   │   ├── mock_server/
│   │   │   ├── __init__.py
│   │   │   └── server.py
│   │   ├── tests/                                  ← backend unit/integration tests
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_attendance.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_dashboard.py
│   │   │   ├── test_enroll.py
│   │   │   ├── test_export.py
│   │   │   ├── test_personal_model_attendance.py
│   │   │   ├── test_risk.py
│   │   │   └── test_students.py
│   │   ├── .pytest_cache/
│   │   ├── __init__.py
│   │   ├── .env
│   │   ├── .env.example
│   │   ├── CLAUDE.md
│   │   ├── requirements.txt
│   │   └── vista_dev.db                            ← backend-local copy of dev DB (6.8 MB)
│   │
│   ├── docs/                                       ← project technical documentation
│   │   ├── screenshots/
│   │   │   └── fig_7_2_teacher_attendance.png
│   │   ├── API_CONTRACT.md
│   │   ├── CONSENT_FORM.md
│   │   ├── DATASET_ANALYSIS.md
│   │   ├── DB_SCHEMA.md
│   │   ├── DEMO_SCRIPT.md
│   │   ├── FEATURE_ENGINEERING.md
│   │   ├── IEEE_PAPER.md
│   │   ├── INTEGRATION_LOG.md
│   │   ├── PILOT_PROPOSAL.md
│   │   ├── PITCH_DECK.md
│   │   ├── PROJECT_REPORT.md
│   │   ├── RISK_ENGINE_SPEC.md
│   │   └── RISK_SYSTEM_DESIGN.md
│   │
│   ├── frontend/                                   ← React/Vite single-page application
│   │   ├── dist/                                   ← built frontend assets
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   └── client.js
│   │   │   ├── App.jsx                             ← 88 KB monolithic React component
│   │   │   ├── index.css
│   │   │   └── main.jsx
│   │   ├── CLAUDE.md
│   │   ├── Dockerfile
│   │   ├── index.html
│   │   ├── nginx.conf
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   ├── md-docs/                                    ← architecture and design markdown docs
│   │   ├── API_SPEC.md
│   │   ├── ARCHITECTURE.md
│   │   ├── DASHBOARD_INTERACTION_MAP.md
│   │   ├── DATABASE_DESIGN.md
│   │   ├── LMS_ARCHITECTURE.md
│   │   ├── LMS_READINESS_REVIEW.md
│   │   ├── ML_DESIGN.md
│   │   ├── PROJECT_PLAN.md
│   │   ├── READINESS_REVIEW.md
│   │   └── ROADMAP.md
│   │
│   ├── ml/                                         ← risk prediction ML package
│   │   ├── data/
│   │   │   ├── generate_sample_data.py
│   │   │   ├── student_data.csv
│   │   │   └── __init__.py
│   │   ├── CLAUDE.md
│   │   ├── __init__.py
│   │   ├── explainer.py
│   │   ├── features.py
│   │   ├── model.pkl                               ← trained XGBoost model (294 KB)
│   │   ├── risk_engine.py
│   │   ├── test_risk_engine.py
│   │   ├── train.py
│   │   └── validate_uci.py
│   │
│   ├── vision/                                     ← face recognition pipeline package
│   │   ├── CLAUDE.md
│   │   ├── __init__.py
│   │   ├── detect.py
│   │   ├── embed.py
│   │   ├── enroll.py
│   │   ├── facial_pipeline.py
│   │   ├── liveness.py
│   │   ├── match.py
│   │   ├── personal_classifier.py
│   │   ├── recognize.py
│   │   ├── test_personal_classifier.py
│   │   ├── test_recognize.py
│   │   └── tracker.py
│   │
│   ├── __init__.py
│   ├── __pycache__/
│   ├── CLAUDE.md
│   ├── DEMO_SCRIPT.md
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── gunicorn.conf.py
│   ├── PLANB.md
│   ├── PROJECT_REPORT.md
│   ├── README.md
│   ├── requirements.txt
│   └── vista_dev.db                                ← vista-level copy of dev DB (856 KB)
│
├── .env                                            ← live environment file (contains secrets)
├── .env.example                                    ← environment template
├── .gitattributes
├── .gitignore
├── .reticle.json
├── ai.config.json
├── AUDIT.md                                        ← 38 KB technical audit report
├── backend-8003.err.log                            ← error log from port 8003 run
├── backend-8003.log
├── backend-live.err.log                            ← error log from live backend run
├── backend-live.log
├── baseline_test_run.txt                           ← test run baseline output
├── CHANGELOG_DOCS.md
├── CLAIMS_TABLE.md                                 ← 9 KB claims verification table
├── connectingfrontend.MD
├── DOCS_SYNC_REPORT.md
├── EXHIBITION_KIT.md                               ← 33 KB exhibition preparation kit
├── FINAL_AUDIT.md                                  ← 55 KB in-progress final audit report
├── NEEDS_YOUR_INPUT.md
├── PAPER_TODO.md                                   ← 14 KB paper completion checklist
├── PART_A_PROGRESS.md
├── README.md
├── regenerate_npz.py                               ← NPZ regeneration script (root-level)
├── REPORT.md                                       ← 113 KB monolithic full report
├── REPORT_back_matter.md
├── REPORT_ch1.md
├── REPORT_ch2.md
├── REPORT_ch3.md
├── REPORT_ch4.md
├── REPORT_ch5.md
├── REPORT_ch6.md
├── REPORT_ch7.md
├── REPORT_front_matter.md
├── terminal.txt
├── test_baseline.txt                               ← 65 KB test output file
├── test_vista.db                                   ← test SQLite database (424 KB)
├── test_vista.db-journal
├── TODO_FOR_ME.md                                  ← 6 KB action checklist
├── train_from_npz.py                               ← ResNet-50 training script (root-level, 33 KB)
├── vista_dev.db                                    ← root-level copy of dev DB (6.7 MB)
└── VIVA_QA.md                                      ← 77 KB viva/exhibition Q&A bank
```

---

## ML and AI Source Files

| Path | Apparent Purpose |
|------|-----------------|
| `vista/vision/facial_pipeline.py` (35 KB) | End-to-end pipeline: SCRFD detection → 160×160 resize → 30-variant augmentation → ArcFace R50 embedding → `.npz` compilation. Entry point for building the face feature dataset. |
| `vista/vision/detect.py` (3 KB) | `FaceDetector` class wrapping InsightFace SCRFD (`det_10g.onnx`); 640×480 input resolution. |
| `vista/vision/embed.py` (1.8 KB) | `FaceEmbedder` class wrapping ArcFace R50 (`w600k_r50.onnx`); outputs 512-dim L2-normalised embeddings. |
| `vista/vision/enroll.py` (5.5 KB) | Student face enrollment flow: capture images → detect → embed → persist gallery embeddings. |
| `vista/vision/match.py` (2.8 KB) | `FaceMatcher` class: cosine similarity matching against in-memory gallery with configurable threshold (production: 0.55). |
| `vista/vision/liveness.py` (3.4 KB) | Heuristic anti-spoofing: EAR (Eye Aspect Ratio) + Laplacian variance blur check. NOT a neural anti-spoofing model. |
| `vista/vision/personal_classifier.py` (3.7 KB) | ResNet-50 PyTorch inference adapter; loads `best_model_npz_splitB.pth`; custom head FC(2048→512)→ReLU→Dropout(0.3)→FC(512→20). |
| `vista/vision/recognize.py` (7.9 KB) | **Public API** for the full cascade pipeline: detect → cosine match (≥0.55 accept) → if miss, ResNet-50 classifier (≥0.60 accept) → liveness check. Returns `{student_id, confidence, liveness_passed}`. |
| `vista/vision/tracker.py` (8.7 KB) | Multi-face tracking across video frames; associates detection boxes over time. |
| `vista/ml/risk_engine.py` (17.8 KB) | Dual-path risk engine: deterministic rule-based `calculate_risk_from_metrics` (production path) + XGBoost inference wrapper `run_pipeline` (diagnostic/auxiliary path). |
| `vista/ml/features.py` (8 KB) | Feature engineering: `StudentMetrics` dataclass, `FeatureVector` computation from raw attendance/score data. 5 features: `overall_attendance`, `recent_attendance`, `avg_score`, `recent_score`, `failed_subjects`. |
| `vista/ml/explainer.py` (8.3 KB) | SHAP TreeExplainer wrapper for XGBoost; produces per-prediction human-readable attribution strings for the `/risk/explain` endpoint. |
| `vista/ml/train.py` (5 KB) | Trains XGBoost vs. Logistic Regression on `student_data.csv`; selects winner by macro F1; saves `model.pkl`. |
| `vista/ml/validate_uci.py` (9.3 KB) | Maps UCI Student Performance dataset columns → `StudentMetrics`; sanity-checks the rule engine against known G3 outcomes; not a training step. |
| `vista/ml/data/generate_sample_data.py` (4.7 KB) | Generates synthetic `student_data.csv` (1000 rows) using deterministic threshold rules that mirror the rule engine. |
| `vista/backend/app/routes/risk.py` (10.9 KB) | REST endpoints for risk assessment: `/api/v1/students/{id}/risk` (rule-based, persisted), `/api/v1/students/{id}/risk/explain` (SHAP diagnostic). |
| `vista/backend/app/routes/attendance.py` (33.2 KB) | Attendance recording endpoints including face-recognition-triggered marking, manual override, batch processing, and CIE policy enforcement. |
| `vista/backend/app/cie_policy.py` (9.3 KB) | VTU CIE rules engine: 75% attendance threshold, 3-test CIE architecture, eligibility evaluation. |
| `vista/backend/app/services/coach_service.py` (20.1 KB) | AI study coach: deterministic fact extraction, LLM fencing via OpenRouter/Ollama with rule-based fallback. |
| `regenerate_npz.py` (root, 13.6 KB) | Re-runs facial pipeline end-to-end from raw `dataset/` images; saves to `data/processed/facial_pipeline_results.npz`. |
| `train_from_npz.py` (root, 33.9 KB) | Loads `.npz`, performs stratified split on original images (Split A: 80/10/10, Split B: 70/15/15), fine-tunes ResNet-50, saves `training_results/best_model_npz_split{A,B}.pth`. Includes `assert_no_leakage` guarantee. |
| `training_results/train.py` (45.4 KB) | Earlier training script operating directly on augmented image files (superseded by `train_from_npz.py`). |

---

## Dataset Directories

| Path | Apparent Contents |
|------|------------------|
| `dataset/` | **Raw face image dataset.** 20 student subdirectories (USN-named: 1DA22AI402, 1DA23AI001–1DA23AI059, 1DA24AI403–404). Each contains ~30–40 raw camera images (`.jpg`/`.jpeg`, ~2–4 MB each). 680 files total, ~1.94 GB. Filenames: `IMG_YYYYMMDD_HHMMSS.jpg`. Represents actual enrolled AI&ML department students. |
| `agumented data/` (sic) | **Augmented face image dataset.** Same 20 student USN directories, but each source image expands into a subdirectory of augmented variants (`aug_000.jpg` through `aug_NNN.jpg`, ~8–25 KB each). 20,130 files total, ~225 MB. Generated by Albumentations: HorizontalFlip, ColorJitter, RandomRotate(±10°), GaussianNoise. Note: this directory mirrors the intermediate step before `.npz` compilation. |
| `data/processed/` | **Compiled .npz embedding store.** `facial_pipeline_results.npz` (1.15 GB). Contains numpy arrays: `images` (N, 160, 160, 3) uint8 face crops, `embeddings` (N, 512) float32 L2-normalised ArcFace embeddings, `labels` (N,) USN strings, `metadata` (N,) dicts with `source_image`, `student_id`, `augmentation_index` (0–29), `original_bbox`, `det_score`. 20 gallery classes, 107–202 usable test samples (unaugmented originals). |
| `vista/ml/data/` | **Synthetic risk prediction training data.** `student_data.csv` (36 KB, ~1000 rows) generated by `generate_sample_data.py`. Columns include `overall_attendance`, `recent_attendance`, `avg_score`, `recent_score`, `failed_subjects`, `risk_label` (LOW/MEDIUM/HIGH). Labels are deterministically generated using the same rules as the rule engine, causing class imbalance (distribution: ~10.7% LOW, 40.5% MEDIUM, 48.8% HIGH in training split). |

---

## Model Files and Checkpoints

| Path | Type | Size | Details |
|------|------|------|---------|
| `training_results/best_model_npz_splitA.pth` | PyTorch state dict | 94 MB | ResNet-50 face classifier trained from `.npz`, Split A (80/10/10). 8 epochs run, best at epoch 1. |
| `training_results/best_model_npz_splitB.pth` | PyTorch state dict | 94 MB | ResNet-50 face classifier trained from `.npz`, Split B (70/15/15). **This is the production model.** Used in `personal_classifier.py`. |
| `training_results/best_model_splitA.pth` | PyTorch state dict | 271 MB | ResNet-50 trained directly from augmented image files (older method), Split A. 19 epochs, best at epoch 12. Test accuracy: 78.48%. |
| `training_results/best_model_splitB.pth` | PyTorch state dict | 271 MB | ResNet-50 trained from image files, Split B. Slightly different split. |
| `vista/ml/model.pkl` | Pickle (XGBoost) | 294 KB | Trained XGBoost 3-class classifier. Config: `n_estimators=300`, `max_depth=4`, `learning_rate=0.1`, `objective=multi:softprob`, `num_classes=3`. 5 input features. |
| `data/processed/facial_pipeline_results.npz` | NumPy archive | 1.15 GB | Not a model but the compiled feature/embedding store used for training and evaluation. |
| InsightFace ONNX models | ONNX (external) | — | `det_10g.onnx` (SCRFD detector) and `w600k_r50.onnx` (ArcFace R50 recognizer) are downloaded by InsightFace at first use into the system's InsightFace cache directory. Not present in the repo itself. |

---

## Training and Evaluation Scripts

### Training Scripts

| Path | Purpose |
|------|---------|
| `train_from_npz.py` (root) | **Primary ResNet-50 trainer.** Loads `facial_pipeline_results.npz`, stratified-splits on unique `(usn, source_image)` pairs, fine-tunes ResNet-50 (ImageNet pretrained), saves split A and B models. Runs `assert_no_leakage` before training. Output: `training_results/best_model_npz_split{A,B}.pth`. |
| `regenerate_npz.py` (root) | Re-runs SCRFD detection + ArcFace embedding on raw `dataset/` images to regenerate `facial_pipeline_results.npz`. Prerequisite for `train_from_npz.py`. |
| `vista/vision/facial_pipeline.py` | Standalone end-to-end pipeline script; earlier version of the same logic now split across `regenerate_npz.py` and `train_from_npz.py`. |
| `training_results/train.py` | Older training script: reads augmented image files directly from `agumented data/`, no `.npz` intermediate. Superseded. |
| `training_results/train_splitA.py` | Thin shim: calls `train.py` with `--split A`. |
| `training_results/train_splitB.py` | Thin shim: calls `train.py` with `--split B`. |
| `vista/ml/train.py` | Trains XGBoost vs. Logistic Regression on `vista/ml/data/student_data.csv`; saves winner to `vista/ml/model.pkl`. |
| `vista/ml/data/generate_sample_data.py` | Generates synthetic `student_data.csv` (1000 rows). Must be run before `vista/ml/train.py`. |

### Evaluation Scripts

| Path | Purpose |
|------|---------|
| `evaluation/evaluate_recognition.py` | Threshold sweep on `facial_pipeline_results.npz`; computes Accuracy, Precision, Recall, F1, FAR, FRR across thresholds; outputs `evaluation/results/recognition_threshold_sweep.json`. |
| `evaluation/benchmark_latency.py` | Latency benchmarks for: cosine matching at gallery sizes 30/100/500, ResNet-50 CPU inference, InsightFace SCRFD+ArcFace pipeline, multi-face group photo scaling (1→45 faces). Outputs `evaluation/results/latency_benchmark.json`. |
| `evaluation/evaluate_risk_model.py` | Evaluates XGBoost model on 200-sample test split; reports accuracy, macro F1, per-class metrics, confusion matrix. Outputs `evaluation/results/risk_model_evaluation.json`. |
| `evaluation/evaluate_coach_groundedness.py` | Tests AI study coach LLM for hallucination: 10 factual queries with known expected values; checks responses for grounded facts. Outputs `evaluation/results/coach_groundedness.json`. |
| `vista/ml/validate_uci.py` | Sanity-checks the deterministic rule engine against UCI Student Performance dataset. Not a model evaluation — tests the rule logic against external ground truth. |
| `paper/figures/plot_results.py` | Generates publication-quality figures from evaluation JSON files: threshold sweep curve, cascade ablation bar chart, group photo latency curve. Outputs PDFs and PNGs to `paper/figures/`. |

---

## Configuration Files

| Path | Purpose |
|------|---------|
| `.env.example` (root) | Environment template: `PORT`, `DATABASE_URL`, `LLM_USE_API`, `LLM_USE_OLLAMA`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`, `OLLAMA_BASE_URL`. |
| `.env` (root) | **Live environment file.** Contains actual secrets (API keys). Not inspected. |
| `vista/backend/.env.example` | Backend-local env template (mirrors root, 725 B). |
| `vista/backend/.env` | Backend-local live env (881 B). Contains secrets. Not inspected. |
| `vista/backend/requirements.txt` | Backend Python dependencies: FastAPI, uvicorn, SQLAlchemy, bcrypt, PyJWT, httpx, reportlab, pydantic, numpy, pandas, scikit-learn, xgboost, shap, pytest. |
| `vista/requirements.txt` | Top-level requirements: adds gunicorn, redis, celery, psycopg2-binary. May be outdated/aspirational vs. backend-specific file. |
| `vista/docker-compose.yml` | Docker Compose for backend + frontend services. |
| `vista/Dockerfile` | Backend Docker image definition. |
| `vista/frontend/Dockerfile` | Frontend nginx Docker image. |
| `vista/frontend/package.json` | Frontend Node.js dependencies (React, Vite). |
| `vista/frontend/vite.config.js` | Vite build configuration with API proxy. |
| `vista/frontend/nginx.conf` | Nginx configuration for serving SPA in Docker. |
| `vista/gunicorn.conf.py` | Gunicorn production server configuration. |
| `.kiro/settings/mcp.json` | Kiro MCP tool server configuration. |
| `.gitignore` (root) | Git ignore rules. |
| `.gitattributes` | Git attributes (LF line endings etc.). |
| `ai.config.json` | Kiro AI assistant configuration (2.5 KB). |
| `.reticle.json` | Reticle tool configuration (48 B). |

---

## Documentation Files

### Root-Level Documents

| Path | Purpose |
|------|---------|
| `README.md` (root, 7 KB) | Project overview, setup instructions, quick-start guide. (Note: some counts were incorrect per doc-update-plan — e.g., "114 endpoints" should be 120, "24 tables" should be 27.) |
| `AUDIT.md` (38 KB) | Technical audit report dated 2026-10-30; verified 3-role RBAC, 120 endpoints, 27 tables, system workflow. |
| `FINAL_AUDIT.md` (55 KB) | In-progress final audit for exhibition 7 Nov 2026; run 2026-11-03; contains live system verification data, health check output, endpoint counts, claims cross-references. |
| `CLAIMS_TABLE.md` (9.7 KB) | 30+ row evidence table: every quantitative claim mapped to source file and result artifact with verified/not-verified status. |
| `EXHIBITION_KIT.md` (33 KB) | Exhibition preparation: 12-slide PPT outline, demo script, team bios, poster layout, Q&A pre-prep. |
| `VIVA_QA.md` (77 KB) | Comprehensive viva/examination Q&A bank (~50+ questions across all system components). |
| `PAPER_TODO.md` (14 KB) | Research paper completion checklist: 10 hardest reviewer questions with honest answers, open experiments, submission checklist. |
| `TODO_FOR_ME.md` (6 KB) | Personal action checklist: submission guide, candidate details, academic-year info. |
| `NEEDS_YOUR_INPUT.md` (3.8 KB) | Items requiring human confirmation before submission (e.g., parent alert delivery, paper submission venue). |
| `CHANGELOG_DOCS.md` (12.7 KB) | Documentation change log. |
| `DOCS_SYNC_REPORT.md` (13.7 KB) | Documentation synchronization audit report. |
| `PART_A_PROGRESS.md` (942 B) | Progress tracker for Part A deliverables. |
| `connectingfrontend.MD` (5 KB) | Notes on connecting frontend to backend. |
| `REPORT.md` (113 KB) | **Monolithic full academic report** (all 7 chapters combined). |
| `REPORT_front_matter.md` (11.6 KB) | Report front matter: title page, abstract, acknowledgements, table of contents. |
| `REPORT_ch1.md` (7.9 KB) | Chapter 1: Introduction, problem statement, objectives. |
| `REPORT_ch2.md` (10.8 KB) | Chapter 2: Literature review. |
| `REPORT_ch3.md` (5.9 KB) | Chapter 3: System design and architecture. |
| `REPORT_ch4.md` (14 KB) | Chapter 4: Implementation. |
| `REPORT_ch5.md` (17 KB) | Chapter 5: Results and evaluation. |
| `REPORT_ch6.md` (13.4 KB) | Chapter 6: Discussion. |
| `REPORT_ch7.md` (25.8 KB) | Chapter 7: Conclusions and future work. |
| `REPORT_back_matter.md` (9.7 KB) | Report back matter: references, appendices. |

### vista/docs/ (Technical Documentation)

| Path | Purpose |
|------|---------|
| `vista/docs/API_CONTRACT.md` (10 KB) | API contract between backend and frontend: endpoint shapes, request/response schemas. |
| `vista/docs/DB_SCHEMA.md` (9.9 KB) | Database schema documentation: 27 tables (verified). |
| `vista/docs/DATASET_ANALYSIS.md` (9 KB) | Analysis of face and risk datasets used; includes UCI dataset cross-validation notes. |
| `vista/docs/FEATURE_ENGINEERING.md` (11.9 KB) | Feature engineering documentation for the risk model: definitions, computations. |
| `vista/docs/RISK_ENGINE_SPEC.md` (14.4 KB) | Formal specification of the rule-based risk engine logic. |
| `vista/docs/RISK_SYSTEM_DESIGN.md` (10.4 KB) | Risk system design: integration with backend, alert thresholds. |
| `vista/docs/IEEE_PAPER.md` (13.4 KB) | IEEE conference paper draft (earlier version; note: contains outdated numbers per NEEDS_YOUR_INPUT). |
| `vista/docs/DEMO_SCRIPT.md` (3.6 KB) | Demo walkthrough script for live demonstration. |
| `vista/docs/CONSENT_FORM.md` (3 KB) | Student biometric data consent form template. |
| `vista/docs/INTEGRATION_LOG.md` (2.1 KB) | Log of integration events between components. |
| `vista/docs/PILOT_PROPOSAL.md` (2.8 KB) | Pilot deployment proposal document. |
| `vista/docs/PITCH_DECK.md` (4.5 KB) | Pitch deck outline. |
| `vista/docs/PROJECT_REPORT.md` (16.7 KB) | Earlier project report version. |

### vista/md-docs/ (Architecture Docs)

| Path | Purpose |
|------|---------|
| `vista/md-docs/ARCHITECTURE.md` (10.3 KB) | System architecture overview. |
| `vista/md-docs/API_SPEC.md` (6.4 KB) | API specification (alternate/earlier version). |
| `vista/md-docs/DASHBOARD_INTERACTION_MAP.md` (34.6 KB) | Detailed UI/UX interaction map for all dashboards. |
| `vista/md-docs/DATABASE_DESIGN.md` (9.6 KB) | Database design document. |
| `vista/md-docs/LMS_ARCHITECTURE.md` (17.3 KB) | LMS (Learning Management System) module architecture. |
| `vista/md-docs/LMS_READINESS_REVIEW.md` (3.7 KB) | LMS readiness review. |
| `vista/md-docs/ML_DESIGN.md` (6 KB) | ML subsystem design document. |
| `vista/md-docs/PROJECT_PLAN.md` (6.5 KB) | Project timeline and planning. |
| `vista/md-docs/READINESS_REVIEW.md` (8.3 KB) | Overall system readiness review. |
| `vista/md-docs/ROADMAP.md` (8.3 KB) | Development roadmap. |

### Agent/AI Tool Docs

| Path | Purpose |
|------|---------|
| `vista/CLAUDE.md` (18.2 KB) | Top-level Claude AI context: architecture, conventions, startup commands, known bugs, DB facts. |
| `vista/backend/CLAUDE.md` (3.9 KB) | Backend-specific Claude context: routes, models, test commands. |
| `vista/frontend/CLAUDE.md` (4.1 KB) | Frontend-specific Claude context. |
| `vista/vision/CLAUDE.md` (3.8 KB) | Vision module Claude context. |
| `vista/ml/CLAUDE.md` (6 KB) | ML module Claude context. |

---

## Research and Paper Draft Files

| Path | Purpose |
|------|---------|
| `paper/PAPER.md` (31.8 KB) | **Primary IEEE conference paper draft** (Markdown). Uses verified numbers: 120 endpoints, 27 tables, 3-role RBAC, cascade F1=0.9246. Title: "VISTA: An Integrated On-Premise Vision and Explainable Risk-Scoring Platform for Classroom Academics." |
| `paper/PAPER.tex` (33 KB) | **LaTeX version** of same paper. Ready for IEEE template submission. |
| `paper/references.bib` (3.4 KB) | BibTeX bibliography: ArcFace (CVPR 2019), SCRFD (ICLR 2022), ResNet (CVPR 2016), XGBoost (KDD 2016), and others. |
| `paper/figures/architecture.mmd` (3 KB) | Mermaid diagram source for system architecture figure. |
| `paper/figures/cascade_flow.mmd` (1 KB) | Mermaid diagram source for cascade decision flow. |
| `paper/figures/fig_cascade_ablation.pdf/.png` | Publication figure: cascade ablation comparison (cosine-only vs. cascade). Generated from `evaluation/results/cascade_ablation.json`. |
| `paper/figures/fig_group_photo_latency.pdf/.png` | Publication figure: multi-face group photo latency scaling. |
| `paper/figures/fig_threshold_sweep.pdf/.png` | Publication figure: threshold sweep F1/FAR/FRR curves. |
| `paper/figures/plot_results.py` (8.3 KB) | Script to regenerate all three publication figures from JSON evaluation artifacts. |
| `vista/docs/IEEE_PAPER.md` (13.4 KB) | Earlier IEEE draft (contains outdated figures: 114 endpoints, 24 tables, 6 roles — **superseded** by `paper/PAPER.md`). |
| `PAPER_TODO.md` (14 KB) | Paper action checklist, 10 hardest reviewer Q&As with honest answers, open experiments (open-set testing, class-weighted retraining, real longitudinal data). |
| `VIVA_QA.md` (77 KB) | Viva Q&A bank grounded in `FINAL_AUDIT.md` evidence. |

---

## Existing Experiment Outputs and Logs

### Evaluation Result Artifacts

| Path | Purpose / Key Numbers |
|------|----------------------|
| `evaluation/results/recognition_threshold_sweep.json` | ArcFace cosine threshold sweep on 107 test samples, 20 classes. Optimal τ=0.30 (F1=0.9246). Production τ=0.55 (Acc=85.98%, F1=0.9246 best point). |
| `evaluation/results/cascade_ablation.json` | Cascade vs. cosine-only on 202 samples. Cosine-only @0.55: Acc=77.72%, FAR=5.45%. Full cascade: Acc=92.57%, FAR=5.45%, FRR=1.98%. |
| `evaluation/results/latency_benchmark.json` | SCRFD+ArcFace: 71.23ms; ResNet-50 CPU: 32.5ms (30.8 FPS); cosine match (100 gallery): 1.07ms. Group photo: 1 face=77ms, 45 faces=311ms. |
| `evaluation/results/risk_model_evaluation.json` | XGBoost: Acc=50.0%, Macro F1=0.3286. Majority baseline: 53.5%. LOW F1=0.0000, MEDIUM F1=0.3893, HIGH F1=0.5966. Trained on synthetic data. |
| `evaluation/results/coach_groundedness.json` | LLM coach: 10/10 queries grounded, 0 hallucinations. Model: `nvidia/nemotron-3.5-super-vl:free` via OpenRouter. |

### Training Logs and Curves

| Path | Purpose |
|------|---------|
| `training_results/results_npz_splitA.txt` | ResNet-50 (from .npz) Split A results: 8 epochs, best at epoch 1. Train: 16,080 aug samples; Val/Test: 67/68 originals only. |
| `training_results/results_npz_splitB.txt` | ResNet-50 (from .npz) Split B results. |
| `training_results/results_splitA.txt` | ResNet-50 (from image files) Split A: 19 epochs, best at epoch 12. Test acc=78.48%, train/test gap=17.90%. |
| `training_results/results_splitB.txt` | ResNet-50 (from image files) Split B. |
| `training_results/data_split_log.txt` (396 KB) | Detailed image-by-image split assignment log (older method). |
| `training_results/data_split_npz_log.txt` (4.2 MB) | Detailed sample-by-sample split log for .npz-based training. |
| `training_results/image_count_report.txt` (4 KB) | Per-student image count summary. |
| `training_results/confusion_matrix_*.png` | Confusion matrix visualisations for all 4 training runs. |
| `training_results/training_curve_*.png` | Training/validation loss+accuracy curves for all 4 runs. |

### Backend Logs

| Path | Purpose |
|------|---------|
| `backend-8003.err.log` (1.7 KB) | Stderr from a backend run on port 8003. |
| `backend-8003.log` (0 B) | Empty stdout log from same run. |
| `backend-live.err.log` (10.5 KB) | Stderr from the live backend run (port 8002). Contains startup info, request logs. |
| `backend-live.log` (0 B) | Empty stdout log. |
| `baseline_test_run.txt` (7.2 KB) | Baseline test run output for reference. |
| `test_baseline.txt` (65 KB) | Full pytest output file from a prior test run (likely the run that identified the 12 failing tests). |
| `terminal.txt` (592 B) | Short terminal session notes. |

### Database Files

| Path | Purpose |
|------|---------|
| `vista_dev.db` (root, 6.7 MB) | Root-level development SQLite database. |
| `vista/vista_dev.db` (856 KB) | vista/-level copy (older/smaller). |
| `vista/backend/vista_dev.db` (6.8 MB) | Backend-level copy (production-current). |
| `test_vista.db` (root, 424 KB) | Test database used by root-level pytest. |
| `test_vista.db-journal` | SQLite rollback journal for test DB. |
| `db_backup/backup_20261031_0540/*.db` | Early DB backup (small: ~600 KB — before seeding). |
| `db_backup/backup_20261031_0725/*.db` | Later DB backup (~6.8 MB — post full seeding). Both backups include `.sql` dumps. |

---

## Prior Planning and Audit Documents

### `.agents/tasks/doc-update-plan.md` (30.8 KB)

**Summary:** Document correction plan generated ~3 Nov 2026 by a planning agent. Identifies and specifies exact text corrections for 8 files (README.md, AUDIT.md, TODO_FOR_ME.md, REPORT.md, REPORT_ch1.md, REPORT_ch3.md, paper/PAPER.md, paper/PAPER.tex). Core errors targeted:
- Wrong endpoint count: "114 (110+4)" → "120 registered routes"  
- Wrong table count: "24" → "27"  
- Wrong role count: "6-role" → "3-role"  
- Wrong startup CWD: `cd vista/backend` → `cd vista`  
- Missing synthetic-data caveat for dashboard data  
- Guide name exposed in two report files  
- MiniFASNet described as current when it's a future enhancement  

The plan notes that REPORT_ch5–ch7 exist only under `docs_backup_final/` (not at project root), so only REPORT.md (the monolith) needs root-level corrections.

### `.agents/tasks/vista-part-a-2026-11-07/test-fix-plan.md` (21.6 KB)

**Summary:** Test fix plan generated for the Part A exhibition (7 Nov 2026) by a planning agent after running `python -m pytest tests/ vista/backend/tests/ --tb=line -q` and finding 12 failing tests. Each failure is categorised as TEST BUG or PRODUCTION BUG with root cause and exact code fix. Key bugs documented:
1. **conftest.py missing `reconcile_current_roster(db)`** — 7th-sem subjects never seeded in test DB (affects 5 tests)
2. **`rajeshwari@vista.local` has role=`mentor` not `teacher`** — hits RBAC guard before validation checks (affects 5 tests)
3. **`_call_vision`/`_call_vision_all` monkeypatch arity mismatch** — `skip_liveness` keyword arg not accepted (2 tests)
4. **`notify_high_risk` ImportError** — function called but does not exist in `notifications.py` → 500 error (1 test)

It is **not confirmed** whether all 12 fixes were applied; the test output file (`test_baseline.txt`) should be checked to verify current pass/fail state.

---

## Key Observations

### 1. Duplicate / Triplicate Database Files
Three copies of `vista_dev.db` exist at different locations (root: 6.7 MB, `vista/`: 856 KB, `vista/backend/`: 6.8 MB). The backend copy appears canonical (largest, most recent). The root copy and `vista/` copy may be stale. Test database `test_vista.db` also exists at root. This creates risk of working against the wrong DB.

### 2. Model Performance Gap — Critical for Paper
The XGBoost risk model accuracy (50.0%) falls **below the majority-class baseline** (53.5%). `CLAIMS_TABLE.md` row C-20 explicitly flags this. The production system correctly uses the **deterministic rule engine** (not XGBoost) for actual risk decisions; XGBoost is auxiliary for SHAP explanations only. This distinction is thoroughly documented in `PAPER_TODO.md` (Q1) and `CLAIMS_TABLE.md` but must be precisely stated in any paper/report.

### 3. Face Recognition Evaluation is Closed-Set Only
No open-set (impostor) test data exists in the `.npz`. The evaluation covers only the 20 enrolled students. `CLAIMS_TABLE.md` row C-16 marks this as "Not Verified (Absent)" and lists it as a paper limitation. `PAPER_TODO.md` lists open-set testing as a required future experiment.

### 4. Small Dataset Scale
- Face recognition: 20 students, ~680 raw images, 107–202 unaugmented test samples  
- Risk model: 1000 synthetic samples (no real longitudinal data)  
- These are explicitly acknowledged as pilot-scale limitations in both the paper and VIVA_QA.md

### 5. Outdated Document — `vista/docs/IEEE_PAPER.md`
This file contains incorrect numbers (114 endpoints, 24 tables, 6 roles). It is superseded by `paper/PAPER.md` and `paper/PAPER.tex`. The doc-update-plan confirms the authoritative paper source is `paper/PAPER.md`.

### 6. 12 Test Failures — Unknown Current State
`test_baseline.txt` (65 KB) records failing tests from a prior run. The test-fix-plan in `.agents/tasks/` documents all 12 failures with exact fixes but does not confirm they were applied. The current state of the test suite needs verification before any audit claims about test coverage.

### 7. `agumented data/` Spelling
The augmented data directory is spelled `agumented data` (missing 'g'). This is consistent across all references in the codebase. `facial_pipeline.py` and `regenerate_npz.py` reference paths appropriately for Windows.

### 8. LLM Coach Dependency
The AI study coach requires `OPENROUTER_API_KEY` in `.env` for LLM-backed responses. The groundedness evaluation used `nvidia/nemotron-3.5-super-vl:free` (OpenRouter). Without a key, the system falls back to deterministic rule-based responses — this fallback is properly coded in `coach_service.py`.

### 9. ResNet-50 Model Size Discrepancy
The `.npz`-trained models (`best_model_npz_splitA/B.pth`, 94 MB each) are significantly smaller than the image-file-trained models (`best_model_splitA/B.pth`, 271 MB each). This is because the `.npz` pipeline uses the full ResNet-50 backbone from ImageNet, while the image-file version may have stored optimizer state or additional metadata. The production model is `best_model_npz_splitB.pth`.

### 10. `docs_backup_final/` Archive
55 files backed up before the Nov 2026 audit run. This directory must NOT be modified — it is a pre-audit snapshot. The doc-update-plan explicitly states this.

### 11. Git Branch
At audit start, the active branch was `cleanup/remove-dead-files`. This is important context: some dead files may have been removed, which could affect any code that referenced them.

### 12. Multiple Overlapping Requirements Files
`vista/requirements.txt` includes Redis, Celery, and psycopg2 which are not in `vista/backend/requirements.txt`. The backend requirements appear to be the operational file. The `vista/requirements.txt` may be an aspirational or Docker-deployment variant.
