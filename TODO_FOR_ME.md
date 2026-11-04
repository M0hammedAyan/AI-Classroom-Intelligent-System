<!-- Last audit: 3 Nov 2026. See FINAL_AUDIT.md for full findings. -->

# VISTA Major Project: Action Checklist & Submission Guide (`TODO_FOR_ME.md`)

This document serves as your completed checklist and action guide for the academic submission dossier of **VISTA (Vision-based Intelligent Student Tracking & Academics / AI Classroom Intelligent System)**. All automated technical audits, empirical benchmarks, full-stack implementations, and report chapters have been synchronized and verified against the repository codebase.

---

## 1. Project Metadata & Candidate Details

- **Project Title:** VISTA: Vision-Based Intelligent Student Tracking & Academics
- **Academic Programme:** Bachelor of Engineering in Artificial Intelligence & Machine Learning
- **Institution:** Dr. Ambedkar Institute of Technology, Bengaluru
- **Academic Year:** 2026–2027

### Project Candidates:
1. **Mohammed Ayan** — `1DA24AI403`
2. **Saheel Pradhan** — `1DA23AI042`
3. **Aryan Raj Singh** — `1DA23AI009`
4. **Sujal Agrahari** — `1DA23AI050`

### Project Guidance:
- **Project Guide & Head of Programme (HOP):** **Dr. Ajayprakash B V**, Associate Professor & Head of Programme, Department of Artificial Intelligence & Machine Learning

---

## 2. Production Interface Screenshots (Captured & Embedded in Report)

All production interface views have been captured from the running deployment, standardized in `docs/screenshots/`, and embedded into Chapter 7 of `REPORT.md`:

- [x] **Figure 7.2: Teacher Facial Attendance Live Verification View**
  - **File:** `docs/screenshots/fig_7_2_teacher_attendance.png`
  - **Route:** `http://localhost:5173/` (Teacher Portal · Deep Learning `22AIU701`, 4th Year AIML)
  - **Output:** 7 students detected and marked present simultaneously (Saheel Pradhan 96%, Mohammed Ayyan 76%, Sujal Agrahari 75%, MC Chethan Patil 73%, Shreyas K T 71%, Mallikarjuna C 70%, Vignesh V 58%).

- [x] **Figure 7.3: Student Self-Service Portal Dashboard**
  - **File:** `docs/screenshots/fig_7_3_student_dashboard.png`
  - **Route:** `http://localhost:5173/` (Student Portal · Mohammed Ayan, USN `1DA24AI403`)
  - **Output:** Bounded personal attendance card (81.2%), Average assessment marks (71.2%), class identifier (`4th Year AIML`), and subject-wise attendance list.

- [x] **Figure 7.4: Student Subject Attendance & CIE Marks Drill-Down**
  - **File:** `docs/screenshots/fig_7_4_student_subject_drilldown.png`
  - **Route:** `http://localhost:5173/` (Subject Detail Modal)
  - **Output:** Date-wise attendance history with `[Face]`, `[Manual]`, `[Seed]` badges, face recognition confidence, and CIE 1 + CIE 2 assessment marks out of 25 (Total /50).

- [x] **Figure 7.5: Admin Academic Control Centre**
  - **File:** `docs/screenshots/fig_7_5_admin_control_centre.png`
  - **Route:** `http://localhost:5173/` (Admin Portal)
  - **Output:** Cohort statistics (66 students, 5 subjects), class division chips (`4th Year AIML`), teacher user accounts, and curriculum subject management.

- [x] **Figure 7.6: Admin Student Roster and Face Biometric Enrollment View**
  - **File:** `docs/screenshots/fig_7_6_admin_student_roster.png`
  - **Route:** `http://localhost:5173/` (Admin Portal)
  - **Output:** Comprehensive 66-student roster table, USN directory, class mapping, and face biometric enrollment buttons.

- [x] **Figure 7.7: Comprehensive Student Profile & Academic Risk View**
  - **File:** `docs/screenshots/fig_7_7_student_profile_risk.png`
  - **Route:** `http://localhost:5173/` (Student Profile Modal)
  - **Output:** Longitudinal attendance bar chart, assessment marks history, and automated XGBoost early risk classification with confidence level.

- [x] **Figure 7.8: Teacher & Admin Manual Attendance & Marks Console**
  - **File:** `docs/screenshots/fig_7_8_manual_entry_console.png`
  - **Route:** `http://localhost:5173/` (Manual Entry Modal)
  - **Output:** Student USN search filter, session date constraints, Present/Absent toggles, CIE marks entry, mandatory audit justification, and record history review.

---

## 3. Simplified 3-User Architecture

In accordance with institutional requirements, the system operates across **three user roles**:
1. **Admin:** System-wide administration, academic control centre, teacher/student account creation, class/subject configuration, biometric enrollment, and cohort risk diagnostics.
2. **Teacher:** Lecture facial attendance capture via live web camera or image upload, recognition confidence review, manual roster corrections, and CIE marks entry with audit reasons.
3. **Student:** Strictly read-only self-service portal for personal attendance tracking, subject-wise progress, CIE scores, and date-wise attendance drill-down.

---

## 4. How to Start the System Locally

```powershell
# 1. Start Backend Server (FastAPI on port 8002)
cd d:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload

# 2. Start Frontend Development Server (React Vite on port 5173)
cd d:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista\frontend
npm run dev
```

Log in with demo credentials:
- **Teacher:** `rajeshwari@vista.local` / `rajeshwari123`
- **Admin:** `admin@vista.local` / `admin123`
- **Student:** `1da24ai403@vista.local` (Mohammed Ayan) / `student123`

---

## 5. Compiling the Final PDF for College Submission

### Option A: Using VS Code Markdown PDF Extension (Recommended)
1. In VS Code, install the extension **Markdown PDF** (`yzane.markdown-pdf`).
2. Open `REPORT.md`.
3. Right-click anywhere in the editor and select **Markdown PDF: Export (pdf)**.
4. The extension will generate `REPORT.pdf` formatted with page breaks, code fences, figures, and tables.

### Option B: Using Pandoc with LaTeX
```powershell
pandoc REPORT.md -o REPORT.pdf --from markdown --template eisvogel --toc --number-sections --highlight-style tango
```
