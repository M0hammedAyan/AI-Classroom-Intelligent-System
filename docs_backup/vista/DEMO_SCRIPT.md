# VISTA — Demo Presentation Script

## Setup (Before Demo)

1. Start backend: `python -m uvicorn vista.backend.app.main:app --host 127.0.0.1 --port 8002`
2. Start frontend: `cd vista/frontend && npm run dev`
3. Open browser: `http://localhost:5173`
4. (Optional) Pre-enroll 1-2 team members via Enrollment page

---

## Demo Flow (10-15 minutes)

### 1. Login (30 sec)
- Show login page with VISTA branding
- Login as `admin@vista.local / admin123`
- Point out: JWT auth, role-based access

### 2. Dashboard Overview (1 min)
- Show stats: total students, present today, risk counts
- Point out HIGH/MEDIUM/LOW risk students with reasons
- Click a student name → Student Detail page

### 3. Student Detail + SHAP (2 min)
- Show individual risk assessment with reasons
- Show SHAP feature importance chart
- Explain: "The model tells us WHY this student is at risk — attendance is the biggest factor"
- Show recent attendance timeline

### 4. Face Enrollment (2 min)
- Navigate to Enrollment page
- Select a student from dropdown
- Upload 3 selfies of a team member
- Click Enroll → show success message
- Point out: "3 images averaged into a 512-dimensional embedding"

### 5. Face Recognition Test (3 min)
- Navigate to Test Recognition page
- Upload a NEW photo of the enrolled person
- Click Run Recognition
- Show result: ✓ Recognized, student name, confidence score
- Try with an unknown face → show "Unrecognized"
- Switch to Multi-Face mode → upload group photo

### 6. Attendance Log (1 min)
- Navigate to Attendance Log
- Show date filtering
- Show status badges (present/absent/liveness failed)
- Show manual override button
- Click Export CSV

### 7. Risk Flags (1 min)
- Navigate to Risk Flags page
- Show filter by level (HIGH/MEDIUM/LOW)
- Click Recompute on a student
- Show reasons update in real-time

### 8. Technical Highlights (2 min)
- Open `/docs` (FastAPI Swagger) — show all 24 endpoints
- Mention: "Architecture supports Docker deployment, PostgreSQL, WebSocket real-time updates"
- Mention SHAP explainability: "Not a black box — every prediction is explainable"

---

## Key Talking Points

- **Not just attendance** — it's an academic intelligence platform
- **Explainable AI** — SHAP values tell teachers exactly what to focus on
- **Production architecture** — Docker, PostgreSQL, WebSocket, scheduled jobs
- **Research-backed** — ArcFace (CVPR 2019), XGBoost, ByteTrack (ECCV 2022)
- **Modular** — vision, ML, backend, frontend all independently testable

---

## Backup Plans

| If this fails... | Do this instead |
|---|---|
| Face recognition not working | Show test results from `python -m vista.vision.test_recognize` |
| No enrolled faces | Use the mock data already seeded (show risk flags + attendance log) |
| Backend won't start | Show API docs from the code, explain architecture |
| Slow model loading | "First load downloads the model (~280MB). Subsequent runs are instant." |

---

## Questions to Expect

| Question | Answer |
|---|---|
| "What's the accuracy?" | "XGBoost F1=0.957 on risk prediction. Face recognition depends on enrollment quality — typically >95% at 1-2m distance." |
| "Can it handle 100 students?" | "Current brute-force matching works up to ~100. Beyond that, we'd add FAISS indexing." |
| "What about privacy?" | "All data stays on-premise. No cloud calls. Embeddings are non-reversible — you can't reconstruct a face from them." |
| "Is this real-time?" | "Single image: <2s on CPU. Video stream: ByteTrack handles frame-by-frame with temporal deduplication." |
| "How is it different from existing systems?" | "Existing systems just mark attendance. VISTA predicts academic risk and explains WHY with SHAP." |
