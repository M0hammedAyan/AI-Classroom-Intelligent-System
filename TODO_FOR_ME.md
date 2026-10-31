# VISTA Major Project: Action Checklist & Submission Guide (`TODO_FOR_ME.md`)

This document serves as your actionable checklist to complete the academic submission dossier for **VISTA (Vision-based Intelligent Student Tracking & Academics / AI Classroom Intelligent System)**. All automated technical audits, empirical benchmarks, and report chapters have been completed and verified against the repository codebase.

Follow this checklist to capture required screenshots, substitute personal institutional details, and compile the final PDF.

---

## 1. Frontend Interface Screenshots to Capture

The college project report requires live interface screenshots for **Chapter 7 (Section 7.5, Table 7.7)**. 

### How to Start the System Locally:
1. **Start Backend Server:**
   ```powershell
   cd d:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
   ```
2. **Start Frontend Development Server:**
   ```powershell
   cd d:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\frontend
   npm run dev
   ```
3. Open your browser at `http://localhost:5173`.

### Screenshots Checklist:

- [x] **Figure 7.2: Teacher Facial Attendance Capture View** *(CAPTURED & EMBEDDED IN REPORT)*
  - **Route:** `http://localhost:5173/teacher/attendance` (Logged in for Deep Learning · 22AIU701, AIML 3rd Year)
  - **Verified Output:** 7 students detected and marked present simultaneously:
    1. Saheel Pradhan (96% confidence)
    2. Shreyas K T (71% confidence)
    3. Mohammed Ayyan (76% confidence)
    4. Sujala Agrahari (75% confidence)
    5. Vignesh V (58% confidence)
    6. MC Chethan Patil (73% confidence)
    7. Mallikarjuna C (70% confidence)

- [ ] **Figure 7.3: Student Self-Service Portal Dashboard**
  - **Route:** `http://localhost:5173/student/dashboard` (Log in as student, e.g., `student1@college.edu`)
  - **Action:** Navigate to the main dashboard.
  - **What to capture:** The circular percentage gauge displaying overall attendance (e.g., 82%), subject-wise attendance progress bars, and recent timetable slots.
  - **Save as:** `docs/screenshots/fig_7_3_student_dashboard.png`

- [ ] **Figure 7.4: Mentor Academic Watchlist with SHAP Insights**
  - **Route:** `http://localhost:5173/mentor/watchlist` (Log in as mentor, e.g., `mentor1@college.edu`)
  - **Action:** View the student watchlist sorted by risk. Click on a student marked `HIGH` risk to open the SHAP explanation popover.
  - **What to capture:** The color-coded risk badge, the confidence score, and the bulleted explanation strings (e.g., *"Overall attendance at 52% — below recommended level"*).
  - **Save as:** `docs/screenshots/fig_7_4_mentor_watchlist.png`

- [ ] **Figure 7.5: Admin Multi-Tier Organizational Tree View**
  - **Route:** `http://localhost:5173/admin/organization` (Log in as admin, e.g., `admin@college.edu`)
  - **Action:** Expand the Department tree (e.g., Department of Computer Science & Engineering -> Semester 6 -> Section A).
  - **What to capture:** The hierarchical node tree displaying faculty assignments and student enrollment rosters.
  - **Save as:** `docs/screenshots/fig_7_5_admin_organization.png`

- [ ] **Figure 7.6: Head of School (HOS) Institution Analytics**
  - **Route:** `http://localhost:5173/hos/overview` (Log in as HOS, e.g., `hos@college.edu`)
  - **Action:** Navigate to the institutional overview.
  - **What to capture:** College-wide aggregate attendance trends, inter-departmental bar charts, and term filter dropdowns.
  - **Save as:** `docs/screenshots/fig_7_6_hos_overview.png`

- [ ] **Figure 7.7: Manual Attendance Fallback Override Form**
  - **Route:** `http://localhost:5173/teacher/attendance/manual`
  - **Action:** Load a class roster showing Present / Absent / Late radio toggles.
  - **What to capture:** The manual override controls demonstrating system resilience when camera feeds are unavailable.
  - **Save as:** `docs/screenshots/fig_7_7_manual_override.png`

---

## 2. Personal & Institutional Placeholders to Fill

Open `REPORT.md` (or `REPORT_front_matter.md`) and search for bracketed tokens `[...]` to replace them with your actual college details:

- [ ] **Project Candidates:**
  - Replace `[Candidate Name 1]` and `[USN 1]`.
  - Replace `[Candidate Name 2]` and `[USN 2]`.
  - Replace `[Candidate Name 3]` and `[USN 3]`.
  - Replace `[Candidate Name 4]` and `[USN 4]`.
- [ ] **Faculty & Department Details:**
  - Replace `[Project Guide Name, Designation]`.
  - Replace `[Head of Department Name]`.
  - Replace `[Principal Name]`.
  - Verify department name: `DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING`.
  - Verify college name: `DR. AMBEDKAR INSTITUTE OF TECHNOLOGY, BENGALURU`.
- [ ] **Consent Form Placeholders (`vista/docs/CONSENT_FORM.md`):**


---

## 3. How to Reproduce & Re-Run Evaluations

All empirical benchmark numbers quoted in `AUDIT.md` and `REPORT.md` are 100% reproducible. Use the scripts in `/evaluation/`:

### 1. Re-Run Unit Tests:
```powershell
# Run vision pipeline tests (7/7 tests)
python -X utf8 vista/vision/test_recognize.py

# Run ML risk engine tests (7/7 tests)
python -X utf8 vista/ml/test_risk_engine.py
```

### 2. Re-Run Threshold Sweep Benchmark:
```powershell
python evaluation/evaluate_recognition.py
# Outputs: evaluation/results/recognition_threshold_sweep.json
```

### 3. Re-Run Latency & Group Photo Benchmark:
```powershell
python evaluation/benchmark_latency.py
# Outputs: evaluation/results/latency_benchmark.json
```

### 4. Re-Run Academic Risk Model Evaluation:
```powershell
python evaluation/evaluate_risk_model.py
# Outputs: evaluation/results/risk_model_evaluation.json
```

---

## 4. Viva Voce & Presentation Defense Questions

Be prepared for the following critical questions during your external viva examination:

1. **Question:** *"Why does your documentation report 100% face recognition accuracy, but your test sweep shows 85.98%?"*
   - **Answer:** *"The 100% accuracy figure was obtained strictly during an initial live camera pilot with 14 photographs of 2 enrolled students (Saheel and Sujal). For our rigorous engineering evaluation, we conducted an unconstrained cosine similarity sweep across 107 test facial crops from 20 classes. That evaluation proved an optimal F1-score of 0.9246 at threshold 0.30, and 78.50% accuracy at our production default threshold of 0.55, which prioritizes false-acceptance suppression (91.30% precision) to prevent proxy attendance."*

2. **Question:** *"Why is your XGBoost Risk Model Macro F1-score 0.329 when earlier documents claimed 0.957?"*
   - **Answer:** *"The historical 0.957 figure was measured on a small, perfectly balanced 200-sample synthetic dataset. When evaluated against the realistic 1,000-sample dataset, the data exhibits a severe class skew (53.5% High risk, 40.5% Medium risk, and only 6.0% Low risk). The scarcity of Low-risk training instances depresses the unweighted macro F1-score. To prevent real students from slipping through, VISTA implements a hybrid architecture where deterministic rule-based safety overrides instantly flag critical risk indicators regardless of statistical class imbalance."*

3. **Question:** *"How does the system ensure student privacy under data protection regulations?"*
   - **Answer:** *"VISTA enforces Privacy-by-Design. Raw video frames are processed transiently in volatile RAM and immediately discarded. Only irreversible 512-dimensional mathematical embeddings are stored, encrypted with AES-256. Furthermore, student face recognition requires explicit opt-in consent recorded in the database, with a zero-penalty manual attendance fallback always available."*

4. **Question:** *"Why did you use SCRFD + ArcFace instead of MTCNN + FaceNet?"*
   - **Answer:** *"Empirical literature and our benchmarks show SCRFD operates at 71.2 ms on CPU with superior small-face detection in crowded classrooms compared to MTCNN (which takes >150 ms and suffers in dense groups). ArcFace utilizes Additive Angular Margin loss to enforce tighter intra-class geodesic clusters and wider inter-class margins on the hypersphere, yielding significantly higher discriminative power than Euclidean triplet-loss FaceNet."*

---

## 5. Compiling the Final PDF for College Submission

You can convert `REPORT.md` into a professionally bound PDF using either of the following standard methods:

### Option A: Using VS Code Markdown PDF Extension (Recommended)
1. In VS Code, install the extension **Markdown PDF** (`yzane.markdown-pdf`).
2. Open `REPORT.md`.
3. Right-click anywhere in the editor and select **Markdown PDF: Export (pdf)**.
4. The extension will generate `REPORT.pdf` formatted with page breaks, code fences, and tables.

### Option B: Using Pandoc with LaTeX
```powershell
pandoc REPORT.md -o REPORT.pdf --from markdown --template eisvogel --toc --number-sections --highlight-style tango
```

### Option C: Import into Microsoft Word
1. Open `REPORT.md` in any Markdown viewer or paste into Microsoft Word.
2. Verify page margins are set to **1.25 inches (Left)** for hard binding and **1.0 inch (Right, Top, Bottom)**.
3. Verify font is **Times New Roman, 12 pt**, with **1.5 line spacing**.
4. Print single-sided or double-sided as required by your department.

---

### Summary of Completed Files in Repository

| File Name | Purpose & Status |
| :--- | :--- |
| `AUDIT.md` | Phase 1 Comprehensive Technical Audit & Discrepancy Matrix (Verified) |
| `REPORT.md` | Phase 2 Master College Project Report (~111 KB, 1,271 lines, Complete) |
| `REPORT_front_matter.md` | Title, Certificate, Abstract, TOC, List of Figures/Tables |
| `REPORT_ch1.md` – `ch7.md` | Chapters 1 through 7 with verified figures, tables, and algorithms |
| `REPORT_back_matter.md` | Applications, Conclusions, Roadmap (P0/P1/P2), IEEE References |
| `evaluation/` | Python benchmark scripts and JSON empirical results |
| `TODO_FOR_ME.md` | This student action checklist |
