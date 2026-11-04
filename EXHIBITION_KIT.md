# EXHIBITION KIT — VISTA
## AI-Powered Classroom Intelligent System
### Exhibition Date: 7 November 2026

> All numbers in this file come from `FINAL_AUDIT.md` (verified 2026-11-03) or directly from source files.
> Nothing is invented. `[PLACEHOLDER]` marks items the project owner must confirm before 7 Nov.

---

## SECTION A — 12-SLIDE PPT OUTLINE

---

### Slide 1 — Title Slide

| Field | Content |
|---|---|
| **Presentation title** | VISTA: AI-Powered Classroom Intelligent System |
| **Subtitle** | Automated Attendance, Academic Risk Prediction, and Personalised Study Coaching |
| **Team** | Mohammed Ayan (1DA24AI403), Saheel Pradhan (1DA23AI042), Aryan Raj Singh (1DA23AI009), Sujala Agrahari (1DA23AI050), Shrujan P (1DA22AI044) |
| **Institution** | Dr. Ambedkar Institute of Technology, Bengaluru |
| **Department** | Department of Artificial Intelligence and Machine Learning |
| **Guide** | Dr. Ajayprakash B V (Project Guide [CONFIRM designation & spelling]; HOS: Dr. Ajayprakash B V; HOP: Dr. Bharath V S) |
| **Academic year** | 2026–27 [CONFIRM] (Course: Major Project Phase-II, 22AIP706 [CONFIRM]) |
| **Exhibition date** | 7 November 2026 |

**Content bullets:**
- Final-year B.E. AI & ML capstone project
- Addresses real institutional pain points: proxy attendance, manual marking errors, early-warning academic risk
- Five integrated modules: face recognition, risk engine, CIE policy, study coach, role-scoped notifications

**Visual suggestion:** VISTA logo on dark background, split into 5 icon tiles (camera, chart, bell, bot, shield)

---

### Slide 2 — Problem Statement

**Content bullets:**
- Manual roll-call in a class of 60–70 students consumes 5–10 minutes per session — dead instructional time
- Proxy attendance is undetectable by paper-based systems
- Attendance-linked eligibility (75% rule per VTU norms) is tracked in spreadsheets — error-prone and retrospective
- No real-time early warning: students who are at risk learn about it at the end of semester
- Scale at **Dr. Ambedkar Institute of Technology, Bengaluru**: multiple divisions, 7 teachers, 70+ students per batch — manual tracking at this scale is unreliable
- RFID/biometric hardware alternatives cost ₹50,000–₹2,00,000 per lab; require physical installation; cannot identify multiple people simultaneously
- Cloud face-recognition APIs (AWS Rekognition, Azure Face) send biometric data to third-party servers — a privacy risk under DPDP Act 2023

**Visual suggestion:** Two-panel graphic — left: teacher with paper register (slow, error-prone); right: VISTA group photo upload (7 faces → 7 records in < 1 second). Annotate with "0.683 s for 60 faces on CPU" from `evaluation/results/latency_benchmark.json`.

---

### Slide 3 — Proposed Solution: VISTA Overview

**Content bullets:**
- **VISTA** = Verified Intelligent Student Tracking and Analytics
- Three user roles: **Admin** (1), **Teacher** (7), **Student** (70) — each with a separate portal and permission set
- Five core modules:
  1. **Face Recognition & Attendance** — group photo → automatic present/absent for entire batch
  2. **Academic Risk Engine** — deterministic rules + XGBoost SHAP for at-risk early warning
  3. **CIE Policy Engine** — VTU 75% rule + CIE 1/2/3 eligibility, computed automatically
  4. **Study Coach** — context-aware LLM chat grounded in each student's verified academic records
  5. **Role-Scoped Notifications** — admin → all; teacher → own subject only; students read-only
- Tech stack in one line: React/Vite → FastAPI → SQLite → InsightFace + ResNet-50 → OpenRouter LLM
- Entirely offline-capable: rule-based fallback for study coach; no internet needed for attendance

**Visual suggestion:** System block diagram — five coloured boxes (one per module) fed by a central FastAPI layer, with a three-role RBAC shield on the right and a SQLite cylinder at the bottom.

---

### Slide 4 — System Architecture

**Content bullets:**
- **Frontend:** React 18 + Vite, Tailwind CSS; runs on port 5173; no external dependencies beyond npm
- **Backend:** FastAPI 0.111.0, Uvicorn 0.29.0; 121 API routes across 10 route modules; runs on port 8002
- **Database:** SQLite via SQLAlchemy 2.0.49; 27 tables; single-file `vista_dev.db` — portable, no server needed
- **ML pipeline:**
  - InsightFace 1.0.1 (SCRFD detector: `det_10g.onnx` + ArcFace embedder: `w600k_r50.onnx`)
  - ResNet-50 cascade classifier (`best_model_npz_splitB.pth`)
  - XGBoost 3.2.0 + SHAP 0.51.0 for risk explanation
- **Study Coach:** OpenRouter API (nvidia/nemotron-3.5-super-vl:free); deterministic Python fallback when offline
- **Scheduler:** APScheduler midnight cron — risk recompute for all students
- **Security:** JWT auth, role-based route guards, XSS sanitisation, in-memory rate limiting (HTTP 429), CSP headers

**Visual suggestion:** Layered architecture diagram. Left-to-right: Browser → React → FastAPI → [SQLite | ML Pipeline | Scheduler | OpenRouter]. Annotate each layer with its technology name and version.

---

### Slide 5 — Face Recognition Pipeline

**Content bullets:**
- **Stage 1 — Detection:** SCRFD (`det_10g.onnx`) detects all faces in a single forward pass; bounding box min 50 px enforced
- **Stage 2 — Liveness:** Laplacian variance ≥ 20.0, detection confidence ≥ 0.5; filters blurred images and thumbnails
- **Stage 3 — ArcFace Embedding:** 512-dimensional L2-normalised vector per face (`w600k_r50.onnx`)
- **Stage 4 — Cosine Matching:** threshold τ = 0.55 against enrolled gallery; F1 = **0.8796** at τ = 0.55 on N=107 test crops (`evaluation/results/recognition_threshold_sweep.json`)
- **Stage 5 — ResNet-50 Cascade:** fallback classifier when ArcFace confidence is borderline; threshold conf ≥ 0.60; **90.10% test accuracy on 101 samples** (`training_results/results_npz_splitB.txt`)
- **Combined cascade result:** FRR reduced from 16.83% → **1.98%** (N=202 samples, 20 classes); FAR = 5.45% (`evaluation/results/cascade_ablation.json`)
- **Throughput:** 60 faces processed in **0.683 s** on Intel i7-13700H CPU — no GPU required (`evaluation/results/latency_benchmark.json`)
- Face embeddings stored in DB for 40 of 71 enrolled students at time of audit

**Visual suggestion:** Linear pipeline diagram — five boxes (Detect → Liveness → Embed → Cosine Match → Cascade) with result statistics annotated below each box. Add a bar chart: FRR before/after cascade (16.83% → 1.98%).

---

### Slide 6 — Attendance Management

**Content bullets:**
- **Group photo upload flow:**
  1. Teacher uploads group JPEG/PNG via `/api/v1/attendance/mark-batch`
  2. VISTA detects all faces, matches to enrolled gallery, returns present/absent for each enrolled student
  3. Single API call commits present + absent records atomically — no partial state
  4. Live pilot (30 Oct 2026): 7 faces → 7 correct records (`REPORT_ch7.md §7.2.1`)
- **Manual attendance override:**
  - Endpoint: `POST /api/v1/attendance/manual`
  - Every override is tagged: `source: "manual"`, `is_manual_override: true`
  - Reason field is mandatory — stored in `audit_logs` table with user_id, timestamp, old/new status
  - 108 audit log entries in DB at time of audit
- **CIE Policy:**
  - 75% attendance per subject = minimum for CIE eligibility (VTU norm)
  - CIE 3 eligibility: average of CIE 1 & 2 < 20/25, or one CIE absent
  - Final mark = best two of three CIE scores, scaled to 50
  - Student portal shows `cie3_eligible` and `cie3_reason` per subject, computed in real time
- **Student portal:** attendance % bounded [0, 100]; 11 subjects shown with date-wise drill-down

**Visual suggestion:** Screenshot of the teacher attendance console + a sample audit log entry showing the mandatory reason field. Add a CIE eligibility decision tree diagram.

---

### Slide 7 — Risk Engine and SHAP

**Content bullets:**
- **Primary: deterministic rule engine** (`vista/ml/risk_engine.py`) — three rules:
  1. ≥ 7 consecutive absences → HIGH risk
  2. Attendance < 75% in any subject → AT-RISK
  3. Chronic low CIE scores trigger SAFE/AT-RISK/CRITICAL classification
- Risk level assigned immediately on each attendance record — no waiting for a nightly job
- **Auxiliary: XGBoost (`vista/ml/model.pkl`)** — used exclusively to generate SHAP feature importance values
  - SHAP latency: **14.20 ms** per student (`evaluation/results/latency_benchmark.json`)
  - SHAP shows which features (absences, CIE scores, streak) drove the risk classification
  - **Honest note:** XGBoost macro F1 = **0.3286** on the 1,000-record dataset (`evaluation/results/risk_model_evaluation.json`); training labels were generated by the same rule engine (synthetic) — XGBoost is illustrative, not authoritative. The rule engine decides; SHAP explains.
- Risk levels: SAFE → AT-RISK → CRITICAL
- Intervention log stored per student in `interventions` table

**Visual suggestion:** Screenshot of the student profile risk view with SHAP bar chart. Annotate that the SHAP bars show feature contributions, and the rule engine (not XGBoost) makes the final call. Put a clear "ILLUSTRATIVE" watermark on the SHAP chart slide note.

---

### Slide 8 — Study Coach

**Content bullets:**
- Every student gets a personalised study coach via `POST /api/v1/coach/chat`
- **Zero-hallucination architecture:**
  1. Python computes all facts from DB first: attendance %, missable classes, recovery streak needed, CIE scores, needed marks to avoid CIE 3
  2. These computed facts (no names or IDs) are injected as a structured `facts` block into the LLM prompt
  3. LLM (nvidia/nemotron-3.5-super-vl:free via OpenRouter) only phrases what Python already computed
  4. Verified: 10/10 factual queries answered correctly, **0 hallucinations** (`evaluation/results/coach_groundedness.json`)
- **Privacy fence:** names, USNs, email, phone are stripped before any data leaves the server
- **Offline fallback:** if `OPENROUTER_API_KEY` is absent/default, or the API call fails, `generate_rule_based_reply()` is called — fully deterministic, handles attendance, CIE, and general queries without any network call
- Coach response always returns `reply`, `provider` (`openrouter` or `fallback`), `disclaimer`, and `facts`
- Students cannot send notifications; coach is the student's only interactive channel

**Visual suggestion:** Screenshot of the study coach chat interface. Show a student asking "how many classes can I miss?" and the response with the per-subject breakdown. Annotate the data flow: DB → Python → [LLM phrasing] → Student.

---

### Slide 9 — Notifications System

**Content bullets:**
- Role-scoped delivery — enforced at API level, not just UI:
  - **Admin** → audience_type: `all`, `students`, or `teachers`; broadcasts to all matching users
  - **Teacher** → restricted to subjects assigned to that teacher; HTTP 403 if they attempt another subject
  - **Student** → read-only; HTTP 403 on any POST attempt
- Notification model: `id`, `title`, `body`, `audience_type`, `sender_role`, `created_at`, `read` flag per user
- XSS protection: title and body are sanitised server-side (`re.sub` + `html.escape`) before storage
- Rate limiting: 1-minute rolling window per sender; HTTP 429 on excess
- Students see only notifications they are eligible for (subject match or all-audience)
- Confirmed live in audit: admin all-broadcast (200), teacher cross-subject attempt (403), student POST (403), student read of admin broadcast (200)

**Visual suggestion:** Screenshot of the notification centre UI. Add a small permission matrix table: Admin ✓ send all / Teacher ✓ send own subject only / Student ✗ send, ✓ read.

---

### Slide 10 — Results and Metrics

**Content bullets:**

| Metric | Value | Source |
|---|---|---|
| ArcFace cosine F1 at τ=0.55 | **0.8796** | `recognition_threshold_sweep.json`, N=107 |
| ResNet-50 cascade accuracy | **90.10%** | `results_npz_splitB.txt`, N=101 test samples |
| Combined cascade: FRR | **1.98%** (was 16.83% cosine-only) | `cascade_ablation.json`, N=202 |
| Combined cascade: FAR | **5.45%** (95% CI: [2.21, 10.79]) | `cascade_ablation.json`, Wilson score |
| 60-face batch latency (CPU only) | **0.683 s** | `latency_benchmark.json`, i7-13700H |
| SHAP explanation latency | **14.20 ms** | `latency_benchmark.json` |
| Study coach groundedness | **10/10 queries** — 0 hallucinations | `coach_groundedness.json` |
| XGBoost risk F1 (on synthetic labels) | **0.3286** (honest) | `risk_model_evaluation.json`, N=200 test |
| API test suite | **38 pass / 25 fail / 63 total** | pytest output, 2026-11-03 |
| DB students enrolled | **71** total, **40** with face embeddings | `vista_dev.db` query |

**Honest caveat to state aloud:** "The XGBoost F1 of 0.33 is on synthetic labels — it is used only for SHAP visualisation. The closed-set recognition tests used 20 enrolled students; open-set impostor testing is listed as future work."

**Visual suggestion:** Two bar charts side by side — (1) FRR before/after cascade; (2) Latency breakdown per pipeline stage. Keep the honest caveat on the slide in a smaller font below the main table.

---

### Slide 11 — Limitations and Future Work

**Content bullets:**

**Honest limitations (say these before the examiner does):**
1. **Small evaluation set:** 20 students, 101–202 test samples — no impostor/open-set testing done; false-accept rate on non-enrolled faces is unknown
2. **Heuristic liveness:** Laplacian variance + bbox size; a high-quality printed photo may pass — no 3D depth or deep anti-spoofing model
3. **Synthetic risk labels:** XGBoost trained on data generated by the same rule engine it was evaluated on — circular; F1 = 0.33 reflects this
4. **Cloud LLM privacy:** When OpenRouter is configured, anonymised student statistics leave the server — a tension with on-premise promises; Ollama deployment mitigates this
5. **In-memory rate limiting:** Login and notification rate limits reset on backend restart — not persistent across crashes

**Future directions (grounded in paper §X):**
1. Deploy Ollama locally — fully offline, eliminates cloud privacy concern
2. Integrate MiniFASNet or depth-based anti-spoofing for robust liveness
3. Collect a real multi-ethnic, multi-lighting dataset; evaluate FAR/FRR with a genuine impostor set
4. Redis-backed rate limiting and session management for production hardening

**Visual suggestion:** Two-column table: Limitation (with honesty rating icon) | Planned Future Work. Keep tone matter-of-fact — "this is what we know, this is what comes next."

---

### Slide 12 — Live Demo / Q&A

**Content bullets:**
- **Demo accounts (ready to use):**
  - Admin: `admin@vista.local` / `admin123`
  - Teacher: `teacher@vista.local` / `teacher123` (or `rajeshwari@vista.local` / `rajeshwari123`)
  - Student: `1da24ai403@vista.local` / `student123` (Mohammed Ayan — 81.2% attendance, seeded scores)
- **Demo flow (5 minutes):**
  1. Admin login → dashboard → student list
  2. Teacher login → upload group photo → attendance marked
  3. Student login → attendance %, CIE scores, risk level
  4. Study coach: "what topics should I focus on?"
  5. Admin → student profile → SHAP risk explanation
- **GitHub / source:** `[PLACEHOLDER — add repo URL if public]`
- **Backend:** `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002` (from `vista/` dir)
- **Frontend:** `npm run dev` (from `vista/frontend/` dir)

**Visual suggestion:** QR code to live demo URL or GitHub repo (if available). System architecture mini-diagram as a reminder. Title card: "Ask us anything."

---

---

## SECTION B — POSTER LAYOUT (A0 PORTRAIT)

---

### Header Band (top 8% of poster)

**Title:** VISTA: AI-Powered Classroom Intelligent System

**Subtitle:** Automated Attendance, Academic Risk Prediction, and Personalised Study Coaching

---

### Team Block (below header, centred)

**Team Members:**
- Mohammed Ayan — 1DA24AI403
- Saheel Pradhan — 1DA23AI042
- Aryan Raj Singh — 1DA23AI009
- Sujala Agrahari — 1DA23AI050
- Sujala Agrahari — 1DA23AI050

**Guide:** Dr. Ajayprakash B V [CONFIRM designation & spelling] | **HOP:** Dr. Bharath V S [CONFIRM] | **HOS:** Dr. Ajayprakash B V [CONFIRM]

**Institution:** Dr. Ambedkar Institute of Technology, Bengaluru
**Department:** Department of Artificial Intelligence and Machine Learning | Academic Year: [PLACEHOLDER]

---

### Column 1 — Problem and Solution (left third)

**Problem Statement:**
Manual attendance marking at scale is slow, error-prone, and cannot detect proxy attendance. The VTU 75% eligibility rule and CIE policy are tracked in spreadsheets with no real-time early warning for at-risk students. Biometric hardware alternatives are expensive and cannot identify multiple students simultaneously. A software-only, on-device solution that is fast, privacy-preserving, and works on standard institutional hardware is needed.

**Proposed Solution:**
VISTA is a web-based academic intelligence platform that uses face recognition to mark attendance for an entire classroom from a single uploaded photograph, detects at-risk students in real time using a deterministic rule engine, enforces VTU CIE policy automatically, and provides each student a personalised AI study coach grounded in their own verified academic records.

---

### Column 2 — Architecture and Pipeline (middle third)

**System Architecture (3–4 sentence description):**
VISTA follows a three-layer architecture: a React/Vite frontend (port 5173), a FastAPI backend (port 8002, 121 routes), and a SQLite database (27 tables). The ML pipeline uses InsightFace SCRFD for multi-face detection, ArcFace for 512-dimensional embeddings, cosine similarity matching at threshold τ = 0.55, and a ResNet-50 cascade classifier as a fallback for borderline matches. Academic risk is computed by a deterministic rule engine, with XGBoost and SHAP providing visual feature attribution. The study coach uses OpenRouter LLM with a deterministic Python pre-computation layer that ensures all facts are verified before the LLM phrases a response, with a fully offline rule-based fallback.

**Architecture diagram:** *(embed the system block diagram from Slide 4)*

---

### Column 3 — Results and Contributions (right third)

**3 Key Results:**

**Result 1 — Cascade recognition accuracy:**
ResNet-50 cascade reduced the False Rejection Rate from 16.83% to **1.98%** (N=202 test samples, 20 enrolled students) while FAR held at 5.45%. Throughput: 60 faces in 0.683 s on CPU — no GPU required.
*Source: `evaluation/results/cascade_ablation.json`*

**Result 2 — Zero-hallucination study coaching:**
The study coach answered 10/10 factual queries correctly with 0 hallucinations, verified by cross-referencing each response against the live database.
*Source: `evaluation/results/coach_groundedness.json`*

**Result 3 — Complete audit trail:**
Every manual attendance override is recorded with user identity, timestamp, mandatory reason, and before/after status. 108 audit log entries confirmed in the live database at time of audit.
*Source: `vista_dev.db` audit_logs table query, 2026-11-03*

---

### Screenshot Panel (bottom band, 5 cells)

Use these actual screenshots from `docs/screenshots/`:

| Cell | File | Caption |
|---|---|---|
| 1 | `fig_7_5_admin_dashboard.png` | Admin Academic Control Centre — summary metrics, class divisions, teacher assignments |
| 2 | `fig_7_3_student_dashboard.png` | Student Self-Service Portal — bounded attendance (81.2%), subject breakdown for Mohammed Ayan (1DA24AI403) |
| 3 | `fig_7_6_admin_student_roster.png` | Admin Student Roster and Face Enrollment View — USN directory, one-click enrollment triggers |
| 4 | `fig_7_7_student_profile_risk.png` | Student Profile and Academic Risk View — longitudinal attendance chart, CIE trajectory, SHAP risk indicator |
| 5 | `fig_7_8_manual_attendance_console.png` | Manual Attendance and Marks Console — USN search, date validation, mandatory audit reason field |

> **Note:** Capture a study coach screenshot and a notifications screenshot before printing. Add them as cells 6–7 or replace cell 5 if space is tight.

---

---

## SECTION C — 5-MINUTE DEMO SCRIPT

> Pre-demo checklist: backend running on port 8002, frontend on port 5173, `.env` has `OPENROUTER_API_KEY` set, browser open to `http://localhost:5173`.

---

| Time | Action | What to say (verbatim) | What the user sees | Fallback if it fails |
|---|---|---|---|---|
| **0:00–0:30** | Open browser to `http://localhost:5173`. Show login page. | "This is VISTA — an AI-powered classroom system. It has three roles: admin, teacher, and student. I'll walk you through all three in five minutes." | Login page with email and password fields, VISTA branding. | If page is blank: open a new browser tab and try `http://127.0.0.1:5173`. If still blank, open Postman and show the API at `http://127.0.0.1:8002/docs`. |
| **0:30–1:30** | Log in as `admin@vista.local` / `admin123`. Navigate to the admin dashboard and the student list. | "The admin portal shows a bird's-eye view: 71 students, 7 teachers, 27 data tables, 11 subjects. Every student account, class section, and subject is managed from here. The admin can also see the full audit log of every manual attendance override." | Admin dashboard with summary metrics. Student roster table with USNs and class sections. | If login fails: check the backend health at `http://127.0.0.1:8002/health`. If 500, restart backend. Use pre-loaded browser screenshot of admin dashboard as fallback. |
| **1:30–2:30** | Log out, log in as `rajeshwari@vista.local` / `rajeshwari123`. Navigate to attendance. Upload the prepared group photo (7 demo students). | "The teacher uploads a single group photo. VISTA detects every face simultaneously using InsightFace — no separate step per student. That photo was processed in under one second on CPU." | Face detection results: 7 faces detected, matched to enrolled students, attendance records created with `source: face`. | If face recognition fails (wrong student or no match): switch to manual attendance. Click 'Manual Entry', enter student USN `1DA24AI403`, mark present, fill in reason "Demo manual entry". This demonstrates the manual override and audit log simultaneously — pivot to it as a feature, not a failure. |
| **2:30–3:00** | Stay on teacher view. Show the attendance records just created. | "Every record carries a source tag — 'face' for automatic, 'manual' for teacher override. The audit log records who marked what, when, and why. This makes proxy attendance traceable." | Attendance record list with `source: face` badges. If manual was used: one record with `source: manual` and the audit reason visible. | If records don't appear: navigate to `http://127.0.0.1:8002/api/v1/attendance?classroom_id=class-aiml-4a&session_date=TODAY` and show the raw JSON response — the data is there even if the UI is slow. |
| **3:00–3:30** | Log out, log in as `1da24ai403@vista.local` / `student123`. Show the student dashboard. | "This is Mohammed Ayan's student portal. His attendance is 81.2%. He can see each subject separately, drill into date-wise records, and check his CIE scores and eligibility for CIE 3. The system computes the VTU 75% rule automatically — he doesn't have to count sessions himself." | Student dashboard: 81.2% attendance, subject breakdown, CIE 1/2/3 scores per subject, CIE 3 eligibility text. | If student login fails: use `1da23ai001@vista.local` / `student123` (ABHAY B SUVARNA, 100% attendance, 1 session). The CIE scores will show `not_scheduled` — note that as honest: "This student has no seeded scores yet, which is why Mohammed Ayan is our primary demo account." |
| **3:30–4:00** | Still on student portal. Open the Study Coach panel. Type: "how many classes can I miss?" | "The study coach knows Mohammed Ayan's exact records. It computes the missable classes per subject in Python first — the AI only phrases what Python has already calculated. So there are no hallucinations. We verified this: 10 out of 10 factual questions answered correctly." | Study coach response showing per-subject missable class count with attendance percentages. `provider: openrouter` shown. | If OpenRouter times out or returns an error: the fallback fires automatically. The response will show `provider: fallback` with a rule-based reply. Say: "The system has an offline fallback — it doesn't need internet to answer student questions." This is a feature demonstration, not a failure. |
| **4:00–4:30** | Log out. Log in as admin. Navigate to a student profile with an AT-RISK or CRITICAL label. Show the SHAP explanation panel. | "The risk engine flags students who miss 7 or more consecutive classes, or drop below 75% attendance. SHAP — SHapley Additive exPlanations — shows which factor contributed most to the risk flag. This helps teachers prioritise who needs intervention." | Student profile with SAFE/AT-RISK/CRITICAL badge. SHAP bar chart showing feature contributions (absence streak, CIE 1 score, attendance %, etc.). | If SHAP chart doesn't load: use the `/api/v1/risk/{student_id}/explain` endpoint in the browser or Postman. Show the JSON response with `shap_values` key. Explain the values verbally. |
| **4:30–5:00** | Return to the admin dashboard or freeze on a clean screen. | "To summarise: one photo marks attendance for an entire class. Every manual override is audited. Students see their own data in real time — no surprises at semester end. The study coach answers questions without hallucinating. And no biometric data leaves the server unless the optional cloud LLM is configured. Questions?" | Clean admin dashboard or VISTA title screen. | No fallback needed — this is a verbal summary. If the system crashed, summarise from memory and offer to show a pre-recorded video. |

---

---

## SECTION D — FAILURE RECOVERY PLAN

---

### D-1 — Backend Won't Start

**Symptoms:** `http://localhost:8002/health` returns a connection error; frontend shows "API unreachable".

**Diagnosis steps:**
1. Check if port 8002 is already in use: `netstat -ano | findstr :8002` (Windows) — if another process is using it, kill it with `taskkill /PID <pid> /F`
2. Check Python is available: `python --version` — should be 3.11.9
3. Look at the terminal for the startup error. Common causes: missing `.env`, missing model file, SQLite lock

**Recovery command:**
```powershell
cd D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002
```
If that fails, try port 8003: add `--port 8003` and update the frontend `.env` (`VITE_API_URL=http://127.0.0.1:8003`).

**Demo workaround:** Open `http://127.0.0.1:8002/docs` in a second browser tab — the interactive Swagger UI lets you show every API endpoint and run them live. This is actually a strong technical demo: "I can show you the full API schema and run any endpoint directly." Use the pre-recorded video as the absolute last resort.

---

### D-2 — Face Not Recognised in Group Photo

**Symptoms:** Attendance result shows a demo student as "unknown" or absent even though they are in the photo.

**Diagnosis steps:**
1. The student likely has no face embedding in the DB. Verify: `SELECT student_id, embedding IS NOT NULL as enrolled FROM students WHERE student_id = '1DA24AI403'`
2. If `enrolled = 0`: that student was not enrolled before the demo. This is the highest-risk known issue (D-10 in FINAL_AUDIT.md).

**Recovery: use manual attendance:**
```
POST /api/v1/attendance/manual
{"student_id":"1DA24AI403","classroom_id":"class-aiml-4a","session_date":"<today>","subject_id":"subject-22aiu701","status":"present","note":"Manual override — face enrollment pending"}
```
This actually demonstrates the manual override and audit log — pivot immediately: "The system handles the case where a student isn't enrolled yet. Let me show you the audit trail this creates."

**Demo workaround:** Before 7 Nov, run `SELECT student_id FROM students WHERE embedding IS NOT NULL` and verify all 7 demo students are enrolled. Re-enroll any missing ones using `POST /api/v1/students/{id}/enroll` with the student's face photo. This is Priority P1 in FINAL_AUDIT.md §G.

---

### D-3 — Study Coach Returns Error

**Is there a fallback?** Yes — `coach_service.py` lines 361–363 and 399:
- If `OPENROUTER_API_KEY` is absent or equals the default placeholder string `"your_openrouter_api_key_here"`, `generate_rule_based_reply()` is called instead.
- If the OpenRouter HTTP call raises any exception, the same fallback fires at line 399.
- `generate_rule_based_reply()` never raises an exception — it always returns a formatted string.
- The API response will show `"provider": "fallback"` instead of `"provider": "openrouter"`.

**What the fallback returns:**
For "how many classes can I miss?" — a per-subject list with missable class count and recovery streak if below 75%.
For CIE / marks queries — a per-subject CIE status with needed marks to avoid CIE 3.
For general queries — a structured summary of overall attendance and subject breakdown.

**Demo workaround:** The fallback is a feature. If OpenRouter fails, say: "The system has an offline fallback — this is intentional for institutional settings without reliable internet." The `provider: fallback` tag in the response is visible proof. No action needed.

---

### D-4 — Database Locked or Corrupted

**Symptoms:** Backend starts but returns 500 errors on all DB queries; startup log says "database is locked" or "no such table".

**Diagnosis steps:**
1. Check if another Python process has the DB open: `Get-Process python | Where-Object {$_.CPU -gt 0}`
2. Kill any stale backend processes: `Get-Process python | Stop-Process -Force`
3. Restart backend — SQLite lock is released when the process exits

**Recovery steps:**
1. Stop all backend processes
2. Copy the current DB as a backup: `Copy-Item vista\backend\vista_dev.db vista\backend\vista_dev_backup_DEMO.db`
3. Restart backend

**Backup database:** The audit does not confirm a pre-seeded backup DB. **Before 7 Nov:** run `Copy-Item vista\backend\vista_dev.db vista\backend\vista_dev_CLEAN_BACKUP.db` and keep this file. If the main DB is corrupted, copy the backup back: `Copy-Item vista\backend\vista_dev_CLEAN_BACKUP.db vista\backend\vista_dev.db`.

**Demo workaround:** If DB is unrecoverable, use the Swagger UI (`/docs`) to show the API schema and run read-only endpoints against whatever data remains. Fall back to pre-recorded video for the full flow.

---

### D-5 — Frontend Won't Start

**Symptoms:** `http://localhost:5173` returns connection refused; `npm run dev` shows an error.

**Diagnosis steps:**
1. Check Node.js is installed: `node --version`
2. Check if `node_modules/` exists: `Test-Path vista\frontend\node_modules` — if False, run `npm install` first
3. Check for a port conflict: `netstat -ano | findstr :5173`

**Recovery command:**
```powershell
cd D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\frontend
npm install   # only if node_modules is missing
npm run dev
```
If port 5173 is blocked, Vite will auto-select the next free port (5174, 5175…) — the terminal output will show the actual URL.

**Alternative — show API responses in Postman or browser:**
The backend has full Swagger documentation at `http://127.0.0.1:8002/docs`. Every endpoint can be exercised directly. This is a credible technical demo:
- Login: `POST /api/v1/auth/login`
- Student portal: `GET /api/v1/student-portal/dashboard` (with Bearer token)
- Study coach: `POST /api/v1/coach/chat`
- Risk explain: `GET /api/v1/risk/{student_id}/explain`

Say: "Let me show you the raw API — this is actually how the frontend talks to the backend."

---

### D-6 — API Key Expired or Rate Limited

**Symptoms:** Study coach returns an error response, or `provider` field shows `fallback` unexpectedly. OpenRouter may return HTTP 429 (rate limited) or 401 (key expired/invalid).

**Fallback behavior from `coach_service.py`:**
- Any HTTP error from OpenRouter is caught by the `try/except` block at lines 361–399
- `generate_rule_based_reply()` is called as the final safety net
- The response will have `"provider": "fallback"` — the student sees a full, formatted reply regardless
- No raw Python traceback or error message is ever shown to the user

**Demo workaround:**
1. If OpenRouter is rate limited during demo, the fallback fires automatically — no action needed
2. To demonstrate the OpenRouter path explicitly: use a fresh API key (check `https://openrouter.ai/keys` for usage limits before the exhibition)
3. To test the fallback path intentionally: temporarily set `OPENROUTER_API_KEY=test_invalid` in `.env`, restart backend, ask the coach a question — it will return a rule-based reply with `provider: fallback`. Reset the key afterwards.
4. Free-tier OpenRouter keys (the project uses `nvidia/nemotron-3.5-super-vl:free`) have no cost but may have request-per-minute limits — spread coach queries across the demo rather than sending them all at once.

---

*EXHIBITION_KIT.md generated: 2026-11-03*
*All numbers sourced from FINAL_AUDIT.md (verified 2026-11-03) and project source files.*
*Shrujan P's USN (1DA22AI044) sourced from `vista/frontend/src/App.jsx` ROSTER constant.*

**[PLACEHOLDER] items requiring project owner confirmation before 7 Nov:**
1. Guide name and exact designation (Associate Professor vs Assistant Professor — inconsistency in REPORT.md; see FINAL_AUDIT.md §E)
2. Academic year (2024–25 or 2025–26)
3. GitHub repository URL (if to be shown on Slide 12 or poster)
4. Student login `1da24ai403@vista.local` — verify it works end-to-end before exhibition day (FINAL_AUDIT.md F-13)
5. Confirm all 7 demo group-photo students have face embeddings in DB (FINAL_AUDIT.md F-10, P1)
