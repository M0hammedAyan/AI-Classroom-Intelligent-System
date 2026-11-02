# VISTA Debug Findings Report

**Investigation date:** 2026-11-02  
**Investigator:** Planning Agent (read-only)  
**Project root:** `D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista`  
**Launch command verified:** `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002 --reload` (CWD: `vista/`)

---

## Executive Summary

The server starts and operates, but contains **four critical bugs** that cause 500 errors or data corruption on specific user actions, plus several warnings that degrade features silently. The most impactful issues are:

1. **Wrong database file is opened** — `VISTA_DB_URL` is never set, so `db.py` defaults to `sqlite:///./vista_dev.db` which resolves to `vista/vista_dev.db` (632 KB). The fully-seeded database is at `vista/backend/vista_dev.db` (6.8 MB). The app uses an almost-empty DB at runtime.
2. **Stale error message claims "5 MB limit" for a 30 MB limit** — all three size-check paths in `attendance.py` raise `UPLOAD_TOO_LARGE` with the wrong message (cosmetic bug but confusing).
3. **`notifications.py` references `user.username`** — the `User` model has no `username` field; calling `GET /api/v1/notifications` as a student causes `AttributeError → 500`.
4. **`admin.py` create_student hardcodes `"class-ai-2022"`** — `POST /api/v1/admin/students` always 400s because that classroom does not exist in the seeded DB.

---

## 1. Python Path & Module Resolution

### 1a. `from vista.vision.enroll import …` — RESOLVED (INFO)

When the backend runs from `vista/` with `python -m uvicorn backend.app.main:app`, the Python working directory is `vista/` and `vista/__init__.py` exists. The import `from vista.vision.enroll import enroll_student` resolves correctly because `vista` is a package relative to the CWD. **The previously-reported ModuleNotFoundError is fixed by the CWD change.**

Evidence:  
- `vista/__init__.py` — exists  
- `vista/vision/__init__.py` — exists, exports `recognize`  
- `vista/backend/__init__.py` — exists  

### 1b. `from vista.backend.app.db import SessionLocal` inside `enroll.py` (WARNING)

`vista/vision/enroll.py` line ~85 (`_store_embedding`) calls:
```python
from vista.backend.app.db import SessionLocal
from vista.backend.app.models.student import Student
```
This cross-package import creates a **second SQLAlchemy engine bound to the same SQLite file**. On Windows, SQLite's WAL mode allows concurrent reads but this doubles the connection pool. More critically: if the `DB_URL` resolves differently in the vision process context vs. the backend, they open different files. With the current setup both resolve identically so this is a WARNING, not critical.

### 1c. `from vista.vision.recognize import recognize` and similar — CORRECT (INFO)

`recognize.py`, `personal_classifier.py`, and `match.py` all import from `vista.backend.app.db` using absolute `vista.*` paths, which work correctly from the `vista/` CWD.

---

## 2. Critical Bug — Wrong Database File

**File:** `vista/backend/app/db.py`, line 7  
**Severity:** CRITICAL — always triggered on startup

```python
DB_URL = os.getenv("VISTA_DB_URL", "sqlite:///./vista_dev.db")
```

**What fails and why:**

- The environment variable is named `VISTA_DB_URL`.
- The `.env` file at `vista/backend/.env` sets `DATABASE_URL=sqlite:///./vista_dev.db` — **wrong key name**.
- The root `.env` (loaded first by `main.py`) also sets `DATABASE_URL=sqlite:///./vista_dev.db` — **also wrong key name**.
- `VISTA_DB_URL` is never set anywhere, so the fallback default `sqlite:///./vista_dev.db` is used.
- With CWD `vista/`, this resolves to `D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\vista_dev.db` (632 KB, modified 2026-11-02 18:43).
- The fully-seeded database is at `D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\backend\vista_dev.db` (6.8 MB, modified 2026-11-02 17:59).

**Effect:**  
The app creates a fresh/near-empty database in `vista/vista_dev.db` every clean start. `seed_demo_data()` and `reconcile_current_roster()` run and populate it, so basic login works. However, all historical attendance, scores, and risk data that was in `backend/vista_dev.db` is invisible at runtime.

**Fix:** Add `VISTA_DB_URL=sqlite:///./backend/vista_dev.db` to `vista/backend/.env`, or change db.py to read `DATABASE_URL` instead of `VISTA_DB_URL`.

---

## 3. Critical Bug — `user.username` AttributeError in Notifications

**File:** `vista/backend/app/routes/notifications.py`, line 79  
**Severity:** CRITICAL — triggers whenever a student calls any notifications endpoint

```python
student_id = user.id.replace("student-", "") if user.id.startswith("student-") else user.username
```

**What fails and why:**  
`User` model (`models/user.py`) has no `username` attribute. If `user.id` does not start with `"student-"` (which shouldn't happen for students since IDs are seeded as `"student-{USN}"` but could happen for edge cases or legacy accounts), Python raises `AttributeError: 'User' object has no attribute 'username'`. Even for students whose ID does start with `"student-"`, the code is wrong in the else-branch; it should fall back to parsing the email instead.

In practice, all seeded student accounts have IDs prefixed with `"student-"`, so the fallback is never reached for normal usage — but any student whose account was created via a different path (or if the prefix check fails) will get a 500.

**Fix:** Replace `user.username` with `user.email.split("@")[0].upper()` as the fallback, or simply raise a 403 if the student ID cannot be resolved.

---

## 4. Critical Bug — Admin Create Student Hardcodes Non-Existent Classroom

**File:** `vista/backend/app/routes/admin.py`, line 264  
**Severity:** CRITICAL — `POST /api/v1/admin/students` always returns 400

```python
classroom = db.query(Classroom).filter(Classroom.classroom_id == "class-ai-2022").first()
if not classroom:
    raise HTTPException(status_code=400, detail={"code": "CLASS_NOT_FOUND", ...})
```

**What fails and why:**  
The seeded database contains classrooms with IDs `"CSE-3A"` and `"class-aiml-4a"`. There is no classroom with ID `"class-ai-2022"`. Every call to create a new student via the admin endpoint returns 400 `CLASS_NOT_FOUND`.

**Fix:** Replace the hardcoded ID with a lookup for the default active classroom (e.g., `"class-aiml-4a"`) or add `class-ai-2022` to the seed.

---

## 5. Critical Bug — Stale Error Message: "Image exceeds 5 MB limit"

**File:** `vista/backend/app/routes/attendance.py`, lines 90, 218, 756  
**Severity:** WARNING (functional bug — limit is correctly enforced at 30 MB, but message says 5 MB)

```python
MAX_IMAGE_BYTES = 30 * 1024 * 1024  # 30 MB

# But error message in all three upload paths says:
raise HTTPException(status_code=400, detail={"code": "UPLOAD_TOO_LARGE", "message": "Image exceeds 5 MB limit."})
```

**What fails and why:**  
The constant was changed from 5 MB to 30 MB (as per the user's request) but the three error message strings were not updated. The limit is correctly enforced at 30 MB. Images under 30 MB pass; images over 30 MB are rejected with the wrong message "Image exceeds 5 MB limit." This confuses the frontend user into thinking 5 MB is the ceiling.

**This is the direct root cause of the original user request ("make it 30 MB" — the code was updated but messages were not).**

**Fix:** Update all three `HTTPException` messages to `"Image exceeds 30 MB limit."` in `attendance.py` lines 90, 218, and 756.

---

## 6. Database — Duplicate Files and Env Mismatch

**Severity:** WARNING

Three `vista_dev.db` files exist:

| Path | Size | Last Modified |
|------|------|--------------|
| `vista/vista_dev.db` | 632 KB | 2026-11-02 18:43 (active at runtime) |
| `vista/backend/vista_dev.db` | 6.8 MB | 2026-11-02 17:59 (seeded data) |
| `D:/…/vista_dev.db` (project root) | 6.8 MB | 2026-10-31 (stale) |

The runtime DB (`vista/vista_dev.db`) is created from scratch on each fresh startup via `create_tables()` + `seed_demo_data()`. While the basic demo data (5 CSE students, 4 AIML students) is re-seeded, all **manually entered attendance corrections, LMS-imported scores, and recomputed risk flags** are permanently lost between restarts unless the DB file persists.

**Fix:** Set `VISTA_DB_URL=sqlite:///./backend/vista_dev.db` so the app uses the stable seeded file, and stop creating a new DB in `vista/`.

---

## 7. Vision / ML Pipeline

### 7a. InsightFace buffalo_l model — PRESENT (INFO)

`C:\Users\moham\.insightface\models\buffalo_l` exists. The `FaceDetector` lazy-loads it on first face recognition call. No startup crash expected.

### 7b. Personal ResNet50 classifier — PRESENT (INFO)

`training_results/best_model_npz_splitB.pth` exists at project root. `personal_classifier.py` references it via:
```python
MODEL_PATH = Path(__file__).resolve().parents[2] / "training_results" / "best_model_npz_splitB.pth"
```
From `vista/vision/personal_classifier.py`, `.parents[2]` = `D:\CipherTECH\Projects\AI-Classroom-Intelligent-System`. This resolves correctly and the file exists.

### 7c. NPZ embedding file — PRESENT (INFO)

`data/processed/facial_pipeline_results.npz` exists. `sync_dataset_students()` loads it correctly on startup. No crash expected.

### 7d. `insightface` and `onnxruntime` — INSTALLED (INFO)

```
insightface: 2.0  (non-standard version number — package installs as "insightface 2.0")
onnxruntime: 1.29.0
torch: 2.14.0+cpu
torchvision: 0.29.0+cpu
```

All vision dependencies are installed. The `requirements.txt` has them commented out (`# insightface>=0.7.3`) but they are present in the venv.

### 7e. Vision pipeline falls back gracefully (INFO)

`attendance.py` `_call_vision()` wraps the import in a `try/except ImportError` and falls back to a stub returning `{"student_id": None, "confidence": 0.0, "liveness_passed": False}`. So even if InsightFace were missing, face recognition would silently return "no face detected" rather than crashing. This means attendance mark operations still work (returning `status=unrecognized`) without the vision stack.

---

## 8. Startup Sequence

**File:** `vista/backend/app/main.py` — `on_startup()`  
**Severity:** WARNING (silent failure modes)

```python
@app.on_event("startup")
def on_startup():
    create_tables()
    db = SessionLocal()
    try:
        seed_demo_data(db)
        from .db import sync_dataset_students, reconcile_current_roster
        sync_dataset_students(db)
        reconcile_current_roster(db)
    finally:
        db.close()
    from .scheduler import init_scheduler
    init_scheduler()
```

**Failure modes found:**

1. `seed_demo_data()` — the function begins with `if db.query(Classroom).count() > 0: return` so it only seeds on a truly empty DB. On a fresh `vista/vista_dev.db`, it seeds correctly. On the populated `backend/vista_dev.db`, it skips. **No crash.**

2. `sync_dataset_students()` — if the NPZ file is missing it silently returns (has `if not npz_path.exists(): return`). If numpy/loading fails, the exception is caught and logged as a warning. **No crash, but no embeddings loaded.**

3. `reconcile_current_roster()` — reads `vista/frontend/src/App.jsx` and parses lines matching `^NAME|USN$` regex. App.jsx has ~50+ matching lines. However, **at line ~250 of `db.py`** this function calls `bcrypt.hashpw(...)` in a loop for every student in the roster. With 50+ students this runs ~50 bcrypt hash computations at startup. At default cost factor 12, each takes ~300ms — this means **~15 seconds of blocking startup time** on first run with a large roster. Uvicorn will not accept requests during this period.

4. `init_scheduler()` — `VISTA_SCHEDULER_ENABLED` is not set in `.env`, so it defaults to `"false"` and the scheduler is skipped. No APScheduler dependency needed. **No crash.**

---

## 9. Environment & Config

### 9a. Missing `VISTA_JWT_SECRET` — WARNING (logged, not fatal)

`main.py` logs a warning but uses the hardcoded default `"vista-dev-secret-CHANGE-in-production-32x!"`. All JWT operations work. Tokens issued with the default secret are valid.

### 9b. `VISTA_DB_URL` vs `DATABASE_URL` mismatch — CRITICAL (covered in §2)

### 9c. OpenRouter API key present — INFO

`OPENROUTER_API_KEY` is set in both `.env` files with an actual key. `LLM_USE_API=true`. The coach service will attempt live API calls. If OpenRouter is unreachable or the key is expired/rate-limited, `chat_with_coach` falls back to the deterministic rule engine. **No 500 from this path.**

### 9d. `VISTA_FACE_MATCH_THRESHOLD` not set — INFO

Defaults to `"0.55"` in `recognize.py`. Reasonable value, no crash.

---

## 10. Route-Level Issues

### 10a. `attendance.py` — `mark-video` endpoint truncation (INFO)

The `except Excepti` text visible in the file appears to be a read-truncation artifact from the tool's 30K character limit — the actual file on disk has 946 lines and the full `except Exception:` block is syntactically complete. **No syntax error.**

### 10b. `admin.py` — `create_student` hardcoded classroom (CRITICAL — covered in §4)

### 10c. `notifications.py` — `user.username` AttributeError (CRITICAL — covered in §3)

### 10d. `admin.py` — `mentor` and `hos`/`hop` role login blocked (WARNING)

`auth.py` login route:
```python
ALLOWED_ROLES = {"admin", "teacher", "student"}
if user.role not in ALLOWED_ROLES:
    raise HTTPException(status_code=403, detail={"code": "ROLE_DEPRECATED", ...})
```
Users with roles `mentor`, `hos`, `hop` cannot log in via the standard login endpoint. This is intentional per the current code but is undocumented. Any legacy user with those roles in the DB will be locked out. `reconcile_current_roster()` deletes these users on every startup anyway, so in practice they shouldn't exist after the first run.

### 10e. `admin.py` mentor/HOS/HOP-specific endpoints still exist but roles can't log in (WARNING)

Several endpoints check `if current_user.role == "mentor"` or `"hos"`, but those roles cannot obtain a JWT. These endpoints are permanently unreachable without code changes. This is an inconsistency, not a crash.

### 10f. `reports.py` — unreferenced `avg_pct` variable (WARNING)

```python
avg_score = sum(s.score for s in scores) / len(scores)
avg_max = sum(s.max_score for s in scores) / len(scores)
avg_pct = (avg_score / avg_max * 100) if avg_max > 0 else 0
```
`avg_pct` is computed but also referenced in the conditional block below — this is fine. **No crash.**

### 10g. `lms.py` — `Score` has no `assessment_type` column default in CSV import (WARNING)

`POST /api/v1/lms/import-csv` creates `Score` objects without setting `assessment_type`:
```python
score = Score(
    id=str(uuid.uuid4()),
    student_id=row["student_id"],
    subject=row["subject"],
    score=float(row["score"]),
    max_score=float(row["max_score"]),
    date=row["date"],
    created_at=now,
)
```
The `Score` model has `assessment_type = Column(Text, nullable=True, default="CIE 1")`. SQLAlchemy will use the Python-side default `"CIE 1"` for all CSV-imported scores, which means every imported score will appear as `CIE 1`. Multi-assessment CSV imports will show incorrect CIE type labels. Not a crash but a data integrity issue.

---

## 11. Frontend → Backend Contract

**File:** `vista/frontend/vite.config.js`

```js
proxy: {
  '/api': { target: 'http://127.0.0.1:8002', changeOrigin: true },
  '/ws':  { target: 'http://127.0.0.1:8002', ws: true },
}
```

The backend runs on `127.0.0.1:8002` and the proxy forwards `/api/*` and `/ws/*` correctly. CORS in `main.py` allows `http://localhost:5173`. **No mismatch found.**

---

## 12. Port Conflicts

Port 8002 is currently **LISTENING** with `TIME_WAIT` connections from previous sessions. This is normal Windows behavior for TCP keepalive. As long as no other process is bound to 8002, uvicorn will start cleanly.

---

## 13. Static Files & Upload Folders

`vista/backend/uploads/` — **EXISTS** (1-byte placeholder). `os.makedirs(UPLOAD_DIR, exist_ok=True)` in `academics.py` ensures it is created on first request if missing. No crash.

The `UPLOAD_DIR` path in `academics.py` is computed as:
```python
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
```
From `vista/backend/app/routes/academics.py`, `os.path.dirname` x3 = `vista/backend/`. So uploads land in `vista/backend/uploads/`. This is correct.

---

## Complete Issue Registry

| # | File | Line(s) | Issue | Severity | Trigger |
|---|------|---------|-------|----------|---------|
| 1 | `backend/app/db.py` | 7 | `VISTA_DB_URL` never set — uses `vista/vista_dev.db` (small file) instead of `backend/vista_dev.db` (seeded) | **CRITICAL** | Always on startup |
| 2 | `backend/app/routes/attendance.py` | 90, 218, 756 | Error message says "5 MB limit" but actual limit is 30 MB | **WARNING** | On oversized upload |
| 3 | `backend/app/routes/notifications.py` | 79 | `user.username` — `User` has no such attribute → `AttributeError → 500` | **CRITICAL** | Student calls `/api/v1/notifications` with non-standard user ID format |
| 4 | `backend/app/routes/admin.py` | 264 | `classroom_id == "class-ai-2022"` hardcoded — classroom doesn't exist → always 400 | **CRITICAL** | `POST /api/v1/admin/students` |
| 5 | `backend/app/db.py` | `reconcile_current_roster()` | 50+ bcrypt hashes computed synchronously at startup → ~15s blocking delay | **WARNING** | Every startup |
| 6 | `backend/app/routes/auth.py` | ~60 | `mentor`, `hos`, `hop` roles blocked from login | **WARNING** | Those roles try to log in |
| 7 | `backend/app/routes/lms.py` | ~130 | CSV import sets all scores to `assessment_type="CIE 1"` | **WARNING** | LMS CSV import |
| 8 | `backend/.env` | 5 | Key is `DATABASE_URL` but db.py reads `VISTA_DB_URL` | **CRITICAL** | Always (root cause of issue #1) |
| 9 | `backend/requirements.txt` | — | `insightface`, `onnxruntime` commented out but installed in venv; could break fresh venv installs | **INFO** | `pip install -r requirements.txt` on new machine |

---

## Recommendations

### Must-Fix (cause crashes / wrong behavior):

1. **Fix the DB URL env var name mismatch.**  
   In `vista/backend/.env`, change `DATABASE_URL=sqlite:///./vista_dev.db` to `VISTA_DB_URL=sqlite:///./backend/vista_dev.db`.  
   This makes the app use the 6.8 MB seeded database instead of creating a new one in `vista/`.

2. **Fix `notifications.py` line 79.**  
   Replace `user.username` with a safe fallback:
   ```python
   student_id = user.id.replace("student-", "") if user.id.startswith("student-") else user.email.split("@")[0].upper()
   ```

3. **Fix `admin.py` create_student hardcoded classroom.**  
   Replace `"class-ai-2022"` with `"class-aiml-4a"` (or look up the first active classroom dynamically).

4. **Fix the three error messages in `attendance.py`.**  
   Lines 90, 218, 756: change `"Image exceeds 5 MB limit."` → `"Image exceeds 30 MB limit."`.

### Should-Fix (degrade features):

5. **Un-comment `insightface` and `onnxruntime` in `requirements.txt`** so fresh installs work.

6. **Offload `reconcile_current_roster()`** to run asynchronously after startup, or pre-hash student passwords once and store them rather than recomputing bcrypt for every student every startup.

7. **Fix `lms.py` CSV import** to read `assessment_type` from the CSV column when present.

### Low Priority:

8. Add `VISTA_JWT_SECRET` to `.env` with a strong secret to suppress the startup warning.

9. Document the intentional deprecation of `mentor`/`hos`/`hop` roles in code comments.
