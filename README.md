# VISTA: AI Classroom Intelligent System

VISTA is a classroom monitoring platform for an engineering college. It marks attendance from classroom photos using face recognition, tracks marks and attendance, estimates academic risk, and gives students a study coach. The backend is FastAPI, the frontend is React with Vite, and the default database is SQLite.

## Roles

Three roles are active: **admin**, **teacher** and **student**. The older HOS, HOP and Mentor roles are deprecated and rejected at login (HTTP 403 `ROLE_DEPRECATED`).

## Features

- **Face attendance** from single photos, batches or video.
  - Detection: InsightFace SCRFD (buffalo_l model pack).
  - Matching: ArcFace gallery matching at cosine similarity 0.55.
  - Fallback: a ResNet-50 classifier with 29 classes, accepted at confidence 0.60.
  - Liveness: heuristic checks (detection confidence, face width, texture variance), applied to webcam capture only.
- **Manual attendance** with an audit log of every change.
- **CIE policy** handling for internal assessment marks.
- **Risk engine**: rule-based risk scoring, with an XGBoost model and SHAP explanations.
- **Role-scoped notifications**: users see only notifications meant for their role and scope.
- **Study coach**: LLM-backed (OpenRouter or Ollama), with a deterministic rule-based fallback when no LLM is configured or reachable.
- Timetable, assignments, study materials, announcements, PDF student reports, and a WebSocket dashboard.

## Verified results and caveats

| Component | Result | Caveat |
|---|---|---|
| ResNet-50 classifier, Split B (654/138/138) | 99.28% test accuracy (137/138), Wilson 95% CI 96.01-99.87% | Clean single-face closed-set test crops. Small test set. |
| ResNet-50 classifier, Split A (740/95/95) | 97.89% (93/95) | Same caveats. |
| ArcFace gallery, threshold 0.55 (138 probes) | precision 1.0000, recall 0.9058 | From a threshold sweep on the same test crops. |
| Risk model (synthetic data) | XGBoost 50.00% accuracy, macro F1 0.3286. Logistic Regression 36.50%, macro F1 0.3183. | Below the 53.50% majority baseline. The model is not predictive. The rule-based engine is the working risk path. |

The classifier numbers come from small test sets. Rejection of unknown (non-enrolled) faces was not tested for the classifier. Do not read these as classroom accuracy. A real classroom with varied pose, lighting and group photos will score lower.

## Current system counts

Recounted from the code and database:

- **API routes:** 145 entries in `app.routes` (144 with HTTP methods).
- **Database tables:** 28 (`sqlite_master`, `vista\backend\vista_dev.db`).
- **Tests:** 150 collected by pytest.
- **Students in the demo DB:** 75 active, of which 49 have a stored face embedding.

## Setup

Requirements: Windows, Python 3.11, Node.js, Git LFS.

```powershell
git lfs pull                      # some augmented images are LFS stubs until pulled
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r vista\requirements.txt
cd vista\frontend
npm install
```

PyTorch: `vista\requirements.txt` pins `torch` and `torchvision` and documents the CUDA index line in its comments (the dev environment uses the `cu132` build). CPU builds work: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`.

InsightFace downloads the `buffalo_l` model pack on first use into `%USERPROFILE%\.insightface\models\buffalo_l`. Face features need this folder, so the first run needs internet access (or copy the folder from another machine).

Copy `.env.example` to `.env` and edit it. Keys go in `.env` only. `.env` is never committed.

## Run

Easiest: `.\start_vista.ps1` (works from any folder; uses the project `.venv`). It sets the database path, selects the 29-class classifier at threshold 0.60, and opens the backend (port 8002) and frontend (port 5173) in two windows.

Manually:

```powershell
# Backend (from vista\)
cd vista
..\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002

# Frontend (from vista\frontend\)
npm run dev
```

API docs: http://127.0.0.1:8002/docs. Frontend: http://localhost:5173.

Note: without `VISTA_FACE_MODEL`, the backend loads the older 20-class checkpoint `training_results\best_model_npz_splitB.pth`. To use the 29-class model, set `VISTA_FACE_MODEL` to `training_results\expanded_v3\best_model_expanded_v3_splitB.pth` (as an absolute path; `start_vista.ps1` does this).

## Environment variables

| Variable | Purpose |
|---|---|
| `VISTA_DB_URL` | SQLAlchemy database URL (default: `vista\backend\vista_dev.db`) |
| `VISTA_FACE_MODEL` | Path to the classifier checkpoint (`.pth`) |
| `VISTA_FACE_MODEL_THRESHOLD` | Classifier acceptance confidence (0.60 in `start_vista.ps1`) |
| `VISTA_FACE_MATCH_THRESHOLD` | ArcFace gallery cosine threshold (default 0.55) |
| `VISTA_FACE_MODEL_DEVICE` | Set to `cuda` to run the classifier on GPU; CPU otherwise |
| `VISTA_DEV_MODE` | Set to `1` to allow developer mode (default off; see below) |
| `VISTA_JWT_SECRET` | JWT signing secret. Set it outside development. |
| `LLM_USE_API`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL` | Study coach through OpenRouter |
| `LLM_USE_OLLAMA`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Study coach through a local Ollama server |

Set exactly one of `LLM_USE_API` or `LLM_USE_OLLAMA` to true. Otherwise the rule-based coach is used. API keys belong in `.env` and must never be committed.

## Developer mode

Developer mode lets you test face recognition by uploading or capturing a photo without choosing a class, subject, period or date.

- **Start it:** run `.\start_vista_dev.ps1`. This is `start_vista.ps1 -Dev`, which sets `VISTA_DEV_MODE=1` for the backend. `.\start_vista.ps1` keeps developer mode off, so use it for demos. With the flag off, the toggle is hidden and the server refuses developer requests.
- **Who can use it:** admin and teacher accounts. Students never see the toggle and the server returns 403 to them.
- **Use it:** switch on the "Developer mode" toggle (top right of the login page and of the admin and teacher workspaces). A banner shows while it is on. The setting is stored in the browser and switching it off restores normal behaviour at once.
- **What it disables:** class, subject, timetable period and session date/time checks, the teacher subject-scope check, the liveness check and duplicate filtering.
- **What it saves:** nothing. It is a dry run through `POST /api/v1/dev/recognize`. No attendance rows, capture events or score and risk changes are written. The request is logged to the server log only. Each detected face is returned with student ID, name, confidence and whether the gallery or the classifier decided.
- **Face boxes:** after Recognise, the preview shows a numbered box on every detected face, and the results list uses the same numbers. Green is a recognised student ("Name · 0.72"), amber and dashed is a best guess rejected by the threshold ("? Name · 0.41", not accepted), red is unknown. Boxes appear only in developer mode and work for uploaded photos and camera captures. Photos with EXIF rotation are handled because the server and the browser both apply it.

## Demo logins

- Admin: `admin@vista.local` / `admin123`
- Teacher: `teacher@vista.local` / `teacher123` (the account exists in the DB)
- Students: `<usn>@vista.local` / `student123`, where `<usn>` is the student's lowercase university serial number

These are development credentials. Change them before any real deployment.

## Tests

```powershell
.venv\Scripts\python.exe -m pytest
```

The suite collects 150 tests. Five errors in `tests\test_timetable.py` are known and predate the latest changes. Frontend build check: `cd vista\frontend; npm run build`.

## Repository structure

| Folder | Contents |
|---|---|
| `vista\backend` | FastAPI app (`app\routes`, models, services) and the dev SQLite DB |
| `vista\frontend` | React 18 + Vite dashboard |
| `vista\vision` | SCRFD detection, ArcFace embedding and matching, ResNet-50 classifier, liveness, tracker |
| `vista\ml` | Risk engine, XGBoost training, SHAP explainer |
| `vista\scripts` | Seed and backup scripts |
| `vista\docs`, `vista\md-docs` | Project documentation |
| `tests` | Backend test suite |
| `scripts` | Seed and backup scripts |
| `training_results` | Classifier training code, checkpoints, split files and logs |
| `evaluation` | Evaluation scripts and recorded results (`evaluation\results`) |
| `figures` | Architecture, DFD and result figures for the report |
| `dataset`, `data`, `agumented data` | Source photos, processed arrays, augmented images (LFS) |
| `paper`, `docs`, `1report` | Paper draft, documents and the final report working files |

## Where results live

- Classifier training results, splits and logs: `training_results\expanded_v3\` (`history_split*.json`, `splits_*.json`, `eval_results.json`).
- Final report graphs: `training_results\expanded_v3\graphs_report\`.
- Gallery threshold sweep, risk model and latency results: `evaluation\results\`.
- Diagrams and report figures: `figures\`.

## Known limitations

- Classifier accuracy was measured on clean, single-face, closed-set crops from small test sets. Unknown-face rejection was not tested.
- The default classifier path is the older 20-class checkpoint unless `VISTA_FACE_MODEL` is set.
- Liveness is heuristic and does not stop a determined spoof. It applies to webcam only.
- The risk model was trained on synthetic data and does not beat the majority baseline. Use the rule-based engine for decisions.
- Five tests in `tests\test_timetable.py` error out.
- Parent alerts are queued in the database. No SMS or email gateway is connected.
- The demo DB contains development data. Do not use it for production.
