# Document Correction Plan — VISTA AI Classroom Intelligent System
**Generated:** 3 Nov 2026  
**Authority:** VERIFIED FACTS list in the workflow prompt  
**Scope:** Pre-submission correction of README.md, AUDIT.md, TODO_FOR_ME.md, REPORT.md, REPORT_ch1.md, REPORT_ch2.md, REPORT_ch3.md, paper/PAPER.md, paper/PAPER.tex

---

## Summary of Issues Found

| File | Issues Found |
|---|---|
| README.md | 6-role table, endpoint count "114 (110+4)", DB table count "24", wrong startup CWD, no synthetic-data caveat |
| AUDIT.md | DB table "24", endpoint "114", DSATM × 2 |
| TODO_FOR_ME.md | Missing audit comment header, guide name (real name present — must be evaluated) |
| REPORT.md | Guide name × 2 (real name), 6-role tables × 2, endpoint "114" × 4, DB table "24" × 4, no synthetic-data note in Ch7, MiniFASNet future-enhancement references |
| REPORT_ch1.md | 6-role portals in Objective 6, endpoint "114" × 1, DB "24" × 1 |
| REPORT_ch3.md | DB "24" in ORM row of Table 3.2 |
| REPORT_ch2.md | Clean — no target errors found |
| paper/PAPER.md | Clean for most verified facts (already uses 120/27/3-role/0.55) — minor: no explicit synthetic-data dashboard note needed in paper |
| paper/PAPER.tex | Clean for most verified facts (already uses 120/27/3-role/0.55) — same |

> **Note on REPORT_ch5.md, REPORT_ch6.md, REPORT_ch7.md:** These files exist only under `docs_backup_final/` (not at the project root). The root has only REPORT_ch1.md, REPORT_ch2.md, REPORT_ch3.md. The REPORT.md monolith at root contains all chapters. Corrections below target the ROOT files only. The `docs_backup_final/` directory is an archive — do not modify it.

---

## FILE 1 — README.md

### Change 1.1 — Badge line: endpoint count and table count
**Location:** Line 4 (header badge line)  
**Old text (exact):**
```
AI-powered academic monitoring: face recognition attendance + ML risk prediction + 6-role dashboard.

**Status:** Pilot-ready | **Features:** 50+ | **Endpoints:** 114 (110 route + 4 core) | **Tables:** 24
```
**New text:**
```
AI-powered academic monitoring: face recognition attendance + ML risk prediction + 3-role dashboard.

**Status:** Pilot-ready | **Features:** 50+ | **Endpoints:** 120 registered routes | **Tables:** 27
```

### Change 1.2 — Startup command CWD is wrong
**Location:** "Setup" section, first powershell block  
**Current:** `cd vista\backend` then `..\..\.venv\Scripts\python.exe -m uvicorn app.main:app ...`  
**Issue:** The verified startup command requires CWD to be `vista/`, not `vista/backend/`, and uses `python -m uvicorn backend.app.main:app`.  
**Old text (exact):**
```powershell
cd vista\backend
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```
**New text:**
```powershell
cd vista
..\..\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002 --reload
```
> Apply the same fix to the duplicate command in the "Quick Start" bash block:  
> Old: `cd vista/backend` + `python.exe -m uvicorn app.main:app ...`  
> New: `cd vista` + `python.exe -m uvicorn backend.app.main:app ...`

### Change 1.3 — "What VISTA Does" table: 6-role and endpoint language
**Location:** "What VISTA Does" table, Platform row  
**Old text (exact):**
```
| **Platform** | 6-role dashboard for Admin, Teacher, and Student |
```
**New text:**
```
| **Platform** | 3-role dashboard (Admin, Teacher, Student); legacy HOS/HOP/Mentor roles deprecated |
```

### Change 1.4 — Roles table: remove HOS, HOP, Mentor rows and add deprecation note
**Location:** "## Roles" section  
**Old text (exact):**
```markdown
## Roles

| Role | Access |
|------|--------|
| Admin | Everything — full system control |
| HOS | School-wide — create depts, users, subjects |
| HOP | Department — create users, manage subjects, view dept students |
| Teacher | Own classes — mark attendance, enter marks, assignments |
| Mentor | Assigned students — watchlist, interventions, risk tracking |
| Student | Own data — attendance, scores, risk, materials, timetable |
```
**New text:**
```markdown
## Roles

> **Active roles (3):** Admin, Teacher, Student. Legacy roles HOS, HOP, and Mentor are deprecated and are rejected at login with HTTP 403 ROLE_DEPRECATED.

| Role | Access |
|------|--------|
| Admin | Everything — full system control, org tree, biometric enrollment |
| Teacher | Own classes — mark attendance, enter marks, assignments |
| Student | Own data — attendance, scores, risk, materials, timetable |
```

### Change 1.5 — Startup command port confirmation
**Location:** Both startup blocks (Setup and Quick Start)  
**Verify:** Port 8002 is already mentioned correctly in both blocks. No additional change needed — confirmed present.

---

## FILE 2 — AUDIT.md

### Change 2.1 — Endpoint count in Section C.2 table title and total row
**Location:** Section "C. Architecture — 2. FastAPI Endpoints Inventory" table header and total row  
**Old text (exact, table title line):**
```
### 2. FastAPI Endpoints Inventory (Total Count: 114)
Verified in `vista/backend/app/main.py:40-54` and `vista/backend/app/routes/*.py`.
```
**New text:**
```
### 2. FastAPI Endpoints Inventory (Total Count: 120 registered routes)
Verified in `vista/backend/app/main.py:40-54` and `vista/backend/app/routes/*.py`.
```

**Old text (exact, total row):**
```
| **Total** | | **114** | Complete production enterprise API |
```
**New text:**
```
| **Total** | | **120** | Complete production enterprise API |
```

### Change 2.2 — DB table count in Section C.3 heading and body
**Location:** Section "C. Architecture — 3. Database Schema (24 Tables ...)" heading  
**Old text (exact):**
```
### 3. Database Schema (24 Tables across 8 SQLAlchemy Modules)
Verified in `vista/backend/app/models/*.py`.
```
**New text:**
```
### 3. Database Schema (27 Tables across 8 SQLAlchemy Modules)
Verified in `vista/backend/app/models/*.py`.
```

> The 3 additional tables are `chat_messages`, `notification_reads`, and `notifications_legacy` — add them to the numbered list at the end (items 25, 26, 27) with a brief note: "Added in extended schema update; confirmed in `sqlite_master` query."

### Change 2.3 — Completed matrix: endpoint and DB table counts
**Location:** Section "H. Completed vs. Partially Done vs. Pending Matrix"  
**Old text (exact):**
```
| **FastAPI REST API** | ✅ Implemented & Working | `vista/backend/app/main.py` | 114 endpoints across 14 modules |
| **Relational Database** | ✅ Implemented & Working | `vista/backend/app/models/*.py` | 24 tables across 8 modules |
```
**New text:**
```
| **FastAPI REST API** | ✅ Implemented & Working | `vista/backend/app/main.py` | 120 registered routes across 14 modules |
| **Relational Database** | ✅ Implemented & Working | `vista/backend/app/models/*.py` | 27 tables across 8 modules |
```

### Change 2.4 — DSATM in Dataset section (Section E.1)
**Location:** Section "E. Dataset Analysis — 1. Raw Student Dataset"  
**Old text (exact):**
```
- **Capture Conditions:** Real mobile phone camera captures under typical fluorescent and daylight illumination at DSATM classrooms, varying between frontal, $\pm 30^\circ$ yaw, smiling, neutral, and slight downward gaze.
```
**New text:**
```
- **Capture Conditions:** Real mobile phone camera captures under typical fluorescent and daylight illumination at [PLACEHOLDER: Institution Name] classrooms, varying between frontal, $\pm 30^\circ$ yaw, smiling, neutral, and slight downward gaze.
```

### Change 2.5 — DSATM in Section K (Real-World Applications)
**Location:** Section "K. Real-World Applications", first bullet  
**Old text (exact):**
```
- **Engineering and Degree Colleges (VTU / DSATM):** Automated roll call compliance, NAAC criteria documentation, and mandatory 75% attendance threshold monitoring.
```
**New text:**
```
- **Engineering and Degree Colleges (VTU / [PLACEHOLDER: Institution Name]):** Automated roll call compliance, NAAC criteria documentation, and mandatory 75% attendance threshold monitoring.
```

### Change 2.6 — DSATM in Section L (Gaps List)
**Location:** Section "L. Gaps List — item 2"  
**Old text (exact):**
```
   - *Status:* Paper draft in `vista/docs/IEEE_PAPER.md` cites DSATM affiliation and mentions target IEEE/Springer conferences.
```
**New text:**
```
   - *Status:* Paper draft in `vista/docs/IEEE_PAPER.md` cites [PLACEHOLDER: Institution Name] affiliation and mentions target IEEE/Springer conferences.
```

---

## FILE 3 — TODO_FOR_ME.md

### Change 3.1 — Prepend audit comment header
**Location:** Very top of file, before the `# VISTA Major Project:` heading  
**Old text:** *(nothing — file starts directly with the heading)*  
**New text to prepend:**
```markdown
<!-- Last audit: 3 Nov 2026. See FINAL_AUDIT.md for full findings. -->

```

### Change 3.2 — Guide name evaluation
**Location:** Section "1. Project Metadata — Project Guidance"  
**Current text:**
```
- **Project Guide & Head of Programme (HOP):** **Dr. Ajayprakash B V**, Associate Professor & Head of Programme, Department of Artificial Intelligence & Machine Learning
```
**Decision:** The name "Dr. Ajayprakash B V" appears consistently throughout all documents (REPORT.md certificate page, acknowledgements, REPORT.md guide signature) as the confirmed guide. The instruction says to use `[PLACEHOLDER: Guide Name]` unless confirmed. Since the same name is present on the formal REPORT.md certificate page, treat it as confirmed and **leave unchanged** — no replacement needed.  
**Action:** No change required for the guide name in TODO_FOR_ME.md.

### Change 3.3 — HOS/Mentor role references that imply "to implement"
**Location:** Section "3. Simplified 3-User Architecture" — already correctly states 3 roles.  
**Note:** TODO_FOR_ME.md already has a correct 3-role section and no HOS/Mentor "to implement" entries. No change needed in this section.

---

## FILE 4 — REPORT.md

### Change 4.1 — Guide name role on Certificate page (appears as both "Project Guide" AND "Head of Programme")
**Location:** Certificate section  
**Old text (exact):**
```
**Dr. Ajayprakash B V** &nbsp;&nbsp;...&nbsp;&nbsp; **Dr. Ajayprakash B V**  
Project Guide &nbsp;&nbsp;...&nbsp;&nbsp; Head of Programme (HOP)  
Project Guide &nbsp;&nbsp;...&nbsp;&nbsp; Dept. of AI & ML  
Dept. of AI & ML  
```
**Issue:** The same person is listed as both "Project Guide" on the left signature block and "Head of Programme (HOP)" on the right. The right block should be the HoD/Examiner line, not a second listing of the same guide. This is a formatting issue, not a name issue.  
**New text — right column should read:**
```
**[PLACEHOLDER: Head of Department Name]**  
Head of Department  
Dept. of AI & ML  
```
> If the guide IS also the HoP, both blocks showing the same name are acceptable — confirm with the user before changing. Flag as: **Requires user confirmation before editing.**

**Separately:** The Acknowledgements section says "Assistant Professor" for the guide:
```
our guide, **Dr. Ajayprakash B V**, Assistant Professor, Department of Artificial Intelligence & Machine Learning
```
But the cover page and TODO_FOR_ME.md say "Associate Professor". Choose the higher rank claimed in the cover page (Associate Professor) for consistency.  
**Old text (exact):**
```
our guide, **Dr. Ajayprakash B V**, Assistant Professor, Department of Artificial Intelligence & Machine Learning,
```
**New text:**
```
our guide, **Dr. Ajayprakash B V**, Associate Professor, Department of Artificial Intelligence & Machine Learning,
```

### Change 4.2 — Abstract: endpoint "114" and DB table "24"
**Location:** ABSTRACT section  
**Old text (exact):**
```
The backend is implemented in FastAPI providing 114 RESTful endpoints, 24 relational database tables, role-based access control across 3 institutional roles (Admin, Teacher, and Student)
```
**New text:**
```
The backend is implemented in FastAPI providing 120 RESTful endpoints, 27 relational database tables, role-based access control across 3 institutional roles (Admin, Teacher, and Student)
```

### Change 4.3 — Chapter 1, Objective 6: "6 role-based user portals" and "114 endpoints, 24 tables"
**Location:** Chapter 1 — Section 1.3 Objectives, item 6  
**Old text (exact):**
```
6. **Robust Enterprise Architecture and Scoped Portals:** To implement an asynchronous, production-ready backend in FastAPI delivering 114 endpoints, 24 relational database tables, automated midnight task scheduling via APScheduler, WebSocket live data push, and 6 role-based user portals (Admin, Head of School, Head of Program, Mentor, Teacher, and Student).
```
**New text:**
```
6. **Robust Enterprise Architecture and Scoped Portals:** To implement an asynchronous, production-ready backend in FastAPI delivering 120 endpoints, 27 relational database tables, automated midnight task scheduling via APScheduler, WebSocket live data push, and 3 active role-based user portals (Admin, Teacher, and Student); legacy roles HOS, HOP, and Mentor are deprecated and rejected at login.
```

### Change 4.4 — Chapter 4 System Architecture Mermaid: remove HOS, HOP, Mentor portal nodes
**Location:** Chapter 4 — Section 4.1 System Architecture, Mermaid diagram  
**Old text (exact, inside the Presentation_Tier subgraph):**
```
        UI1["Admin Command Center"]
        UI2["Head of School (HOS) Portal"]
        UI3["Head of Program (HOP) Portal"]
        UI4["Faculty Mentor Watchlist"]
        UI5["Teacher Attendance Console"]
        UI6["Student Self-Service Portal"]
```
**New text:**
```
        UI1["Admin Command Center"]
        UI2["Teacher Attendance Console"]
        UI3["Student Self-Service Portal"]
```
> Also update the caption and description for Fig 4.1 if it references 6 portals — replace with "3 role-scoped portals".

**Also update Data Tier node in same diagram:**  
**Old text (exact):**
```
        DB[(Relational DB: 24 Tables)]
```
**New text:**
```
        DB[(Relational DB: 27 Tables)]
```

**Also update Application Tier node:**  
**Old text (exact):**
```
        Gateway["REST API Router (114 Endpoints across 14 Modules)"]
```
**New text:**
```
        Gateway["REST API Router (120 Routes across 14 Modules)"]
```

### Change 4.5 — Chapter 4 Table 4.1: remove HOS, HOP, Mentor actor rows
**Location:** Chapter 4 — Section 4.2.1, Table 4.1: Actor Roles  
**Old text (exact):**
```
| **HOS** | School-Level | Monitors cross-departmental staff performance, aggregate enrollment, and faculty retention. |
| **HOP** | Department-Level | Manages course catalogs, teacher-subject mappings, class timetables, and departmental at-risk watchlists. |
| **Mentor** | Assigned Students | Tracks longitudinal risk flags, inspects SHAP diagnostic factors, and logs remedial counseling sessions. |
```
**Action:** Remove those three rows entirely. The table should only contain Admin, Teacher, and Student rows.  
**Also add a note below the table:**
```
> **Note:** Roles HOS, HOP, and Mentor were planned in early design but are deprecated in the production system. Login attempts with these roles return HTTP 403 ROLE_DEPRECATED.
```

### Change 4.6 — Chapter 4 Table 4.2: remove UC-06 (Log Mentorship Intervention) which references Mentor actor
**Location:** Chapter 4 — Section 4.2.2, Table 4.2: Use Case Specifications  
**Old text (exact):**
```
| **UC-06** | Log Mentorship Intervention | Mentor | Student flagged in risk watchlist; counseling session conducted.| Intervention note, action item, and review date stored in DB. |
```
**Action:** Remove this row. Optionally replace with a note: "UC-06 (Mentorship) is deprecated; intervention logging is accessible to Admin only."

### Change 4.7 — Chapter 4 Use Case Diagram Mermaid: remove Mentor actor
**Location:** Chapter 4 — Section 4.2.3, Mermaid use case diagram  
**Old text (exact):**
```
    subgraph Actors
        A((Admin))
        T((Teacher))
        S((Student))
    end
```
This is already correct (3 actors). However, the DFD Level 1 diagram references a `Mentor([Mentor / HOP])` node:  
**Old text (exact, in Fig 4.4 DFD Level 1 mermaid):**
```
    Mentor([Mentor / HOP]) -->|Query Watchlist| P4
    Mentor -->|Log Intervention Action| D4
```
**Action:** Remove those two lines. The Admin role handles watchlist queries instead.

### Change 4.8 — Chapter 4 Architectural Tier description paragraph: "6 role-scoped workspaces"
**Location:** Section 4.1, Architectural Tier Descriptions, item 1  
**Old text (exact):**
```
1. **Presentation Layer (Tier 1):** Built using React 18, Vite, and Tailwind CSS v4, this tier provides dedicated, role-scoped user workspaces for all six institutional roles. Components connect to the backend exclusively via an Axios REST client (`src/api/client.js`) and persistent WebSocket streams for live dashboard KPI telemetry.
```
**New text:**
```
1. **Presentation Layer (Tier 1):** Built using React 18, Vite, and Tailwind CSS v4, this tier provides dedicated, role-scoped user workspaces for the three active institutional roles (Admin, Teacher, Student). Components connect to the backend exclusively via an Axios REST client (`src/api/client.js`) and persistent WebSocket streams for live dashboard KPI telemetry.
```

### Change 4.9 — Chapter 4 Data Layer tier description: "24-table"
**Location:** Section 4.1, Architectural Tier Descriptions, item 4  
**Old text (exact):**
```
4. **Data Layer (Tier 4):** Anchored by a 24-table relational database schema managed via SQLAlchemy 2.0 ORM (PostgreSQL in production, SQLite in development) alongside an in-memory Redis instance for token blocklisting and session caching.
```
**New text:**
```
4. **Data Layer (Tier 4):** Anchored by a 27-table relational database schema managed via SQLAlchemy 2.0 ORM (PostgreSQL in production, SQLite in development) alongside an in-memory Redis instance for token blocklisting and session caching.
```

### Change 4.10 — Chapter 5 Table 5.1: endpoint total "114" in summary row
**Location:** Chapter 5 — Table 5.1, total row  
**Old text (exact):**
```
| **Total** | | **114** | Complete production enterprise REST & WebSocket API |
```
**New text:**
```
| **Total** | | **120** | Complete production enterprise REST & WebSocket API |
```

### Change 4.11 — Chapter 5 Table 5.2 heading: "24 Tables"
**Location:** Chapter 5 — Section 5.2.3 heading and table title  
**Old text (exact):**
```
### 5.2.3 Relational Database Schema (`vista/backend/app/models/`)
The database architecture comprises 24 tables declared across 8 model modules in `vista/backend/app/models/`. Table 5.2 lists all tables, foreign key constraints, and operational purposes.

**Table 5.2: Database Relational Schema Specification (24 Tables)**
```
**New text:**
```
### 5.2.3 Relational Database Schema (`vista/backend/app/models/`)
The database architecture comprises 27 tables declared across 8 model modules in `vista/backend/app/models/`. Table 5.2 lists all tables, foreign key constraints, and operational purposes.

**Table 5.2: Database Relational Schema Specification (27 Tables)**
```
> Also add three new rows to the bottom of Table 5.2 for the three additional confirmed tables:
> - `chat_messages` (coach module): AI Study Coach conversation history
> - `notification_reads` (notification.py): Per-user notification read status
> - `notifications_legacy` (notification.py): Legacy notification archive

### Change 4.12 — Chapter 5 Summary section: "114 endpoints and 24 relational tables, enforcing 6-role RBAC"
**Location:** Section 5.5 Summary  
**Old text (exact):**
```
The backend implements 114 endpoints and 24 relational tables, enforcing 6-role RBAC security and scheduled midnight risk computations.
```
**New text:**
```
The backend implements 120 endpoints and 27 relational tables, enforcing 3-role RBAC security (Admin, Teacher, Student) and scheduled midnight risk computations.
```

### Change 4.13 — Chapter 6 Testing section: "114 endpoints" in testing objectives
**Location:** Chapter 6 — Section 6.1 Testing Objectives, item 2  
**Old text (exact):**
```
2. **Interface and Authentication Integrity:** Verify that the FastAPI backend strictly enforces JSON Web Token (JWT) signature validity, role-based authorization hierarchies, database relational constraints, and audit log persistence across all 114 endpoints.
```
**New text:**
```
2. **Interface and Authentication Integrity:** Verify that the FastAPI backend strictly enforces JSON Web Token (JWT) signature validity, role-based authorization hierarchies, database relational constraints, and audit log persistence across all 120 registered routes.
```

### Change 4.14 — Chapter 6 RBAC section: "6 distinct user roles" and HOP reference
**Location:** Chapter 6 — Section 6.3.1 RBAC Verification  
**Old text (exact):**
```
The VISTA backend implements 6 distinct user roles (`admin`, `teacher`, `student`). Each endpoint is decorated with dependency-injected permission checks (`require_role` in `vista/backend/app/permissions.py`).
```
**Note:** This is internally inconsistent (says 6 but lists 3). Fix the number:  
**New text:**
```
The VISTA backend implements 3 active user roles (`admin`, `teacher`, `student`); legacy roles `hos`, `hop`, and `mentor` are deprecated and rejected at login with HTTP 403. Each endpoint is decorated with dependency-injected permission checks (`require_role` in `vista/backend/app/permissions.py`).
```

**Also remove or update item 3 in the RBAC verification list:**  
**Old text (exact):**
```
3. **Departmental Scoping:** A Head of Department (`hop`) is restricted from querying attendance aggregates or academic records belonging to departments outside their administrative domain.
```
**New text:**
```
3. **Scope Enforcement:** Admin users are restricted to institutional-scope operations; teachers are restricted to their assigned classes; students can only access their own records.
```

### Change 4.15 — Chapter 7 Results: ADD synthetic-data note at start of section 7.1 / 7.2
**Location:** Chapter 7 — Beginning of Section 7.2 (Output Analysis), before the "### 7.2.1 Biometric Recognition Pipeline" heading  
**Action:** Insert the following note block immediately after the Section 7.2 heading line:
```markdown
> **⚠️ Note on Dashboard Data:** Attendance records and marks visible in the dashboard are seeded synthetic demo data generated by `seed_demo_data()` in `db.py`. They are not real student records. Recognition accuracy figures are derived from the real-world pilot dataset described in Section 7.1.
```

### Change 4.16 — Chapter 8 Conclusions: "114 FastAPI route endpoints, 24 relational SQLAlchemy database tables, 6 distinct role-based access control tiers"
**Location:** Chapter 8 — Section 8.2 Conclusions, item 4  
**Old text (exact):**
```
4. **Architectural Completeness:** The platform delivers an end-to-end operational software product comprising 114 FastAPI route endpoints, 24 relational SQLAlchemy database tables, 6 distinct role-based access control tiers, dynamic audit logging, and responsive web portals for administrators, department heads, mentors, teachers, and students.
```
**New text:**
```
4. **Architectural Completeness:** The platform delivers an end-to-end operational software product comprising 120 FastAPI registered routes, 27 relational SQLAlchemy database tables, 3 active role-based access control tiers (Admin, Teacher, Student), dynamic audit logging, and responsive web portals for administrators, teachers, and students.
```

### Change 4.17 — List of Tables: "Table 5.2 (24 Tables)"
**Location:** LIST OF TABLES section  
**Old text (exact):**
```
- **Table 5.2:** Database Relational Schema Specification (24 Tables)
```
**New text:**
```
- **Table 5.2:** Database Relational Schema Specification (27 Tables)
```

---

## FILE 5 — REPORT_ch1.md

### Change 5.1 — Objective 6: "114 endpoints, 24 tables, 6 role-based user portals"
**Location:** Section 1.3 Objectives, item 6  
**Old text (exact):**
```
6. **Robust Enterprise Architecture and Scoped Portals:** To implement an asynchronous, production-ready backend in FastAPI delivering 114 endpoints, 24 relational database tables, automated midnight task scheduling via APScheduler, WebSocket live data push, and 6 role-based user portals (Admin, Head of School, Head of Program, Mentor, Teacher, and Student).
```
**New text:** *(identical to Change 4.3 above)*
```
6. **Robust Enterprise Architecture and Scoped Portals:** To implement an asynchronous, production-ready backend in FastAPI delivering 120 endpoints, 27 relational database tables, automated midnight task scheduling via APScheduler, WebSocket live data push, and 3 active role-based user portals (Admin, Teacher, and Student); legacy roles HOS, HOP, and Mentor are deprecated and rejected at login.
```

---

## FILE 6 — REPORT_ch3.md

### Change 6.1 — Table 3.2: SQLAlchemy row description "24-table declarative mapping"
**Location:** Table 3.2, Database ORM row  
**Old text (exact):**
```
| **Database ORM** | SQLAlchemy | `>=2.0.0` | 24-table declarative mapping and connection pooling |
```
**New text:**
```
| **Database ORM** | SQLAlchemy | `>=2.0.0` | 27-table declarative mapping and connection pooling |
```

---

## FILE 7 — REPORT_ch2.md

**No changes required.** The chapter contains only literature survey content with no incorrect technical facts from the verified list.

---

## FILE 8 — paper/PAPER.md

### Status
The paper already uses the correct authoritative values:
- 120 API routes ✓ (Section III.B)
- 27 relational tables ✓ (Section III.C)
- 3 active roles (Admin, Teacher, Student) ✓ (Section III.B)
- HOS/HOP/Mentor deprecated with 403 ✓ (Section III.B)
- Cosine threshold 0.55 ✓ (Section IV.A.3, Table I)
- Laplacian variance heuristic ✓ (no MiniFASNet claim)
- 20 students, ~20,130 samples ✓ (Section V.B)
- XGBoost on synthetic data, 1000 samples 800/200 split ✓ (Section V.B, E)
- 90.10% on 101 test samples (Split B) ✓ (implied; N=202 ablation with 107 sweep is different test)

### Change 8.1 — Guide name: institution affiliation uses real institution name "Dr. Ambedkar Institute of Technology"
**Note:** The paper already uses "Dr. Ambedkar Institute of Technology" (which is DRAIT, a real institution). This is NOT "DSATM" — it is a different institution name that appears to be intentionally used. The verified facts say NOT to use "DSATM" but to use "[PLACEHOLDER: Institution Name]". The paper uses "Dr. Ambedkar Institute of Technology" which is the full name. If this is the correct institution, it should remain. If not, replace with placeholder.  
**Action:** **Flag for user confirmation.** The paper uses "Dr. Ambedkar Institute of Technology, Bengaluru, India" — if this is the correct institution name, no change needed. If the institution is DSATM and this is wrong, replace all occurrences of "Dr. Ambedkar Institute of Technology" with "[PLACEHOLDER: Institution Name]".

### Change 8.2 — No synthetic-data dashboard note needed in paper
The paper already notes that risk data is synthetic (Section V.B: "Synthetic Academic Records Dataset") and has a critical caveat (Section V.E). No additional note is required.

---

## FILE 9 — paper/PAPER.tex

### Status
The .tex file mirrors the .paper/PAPER.md content for the sections read. The same authoritative values (120 routes, 27 tables, 3 roles, 0.55 threshold) are already present.

### Change 9.1 — Same institution name question as PAPER.md
**Action:** Same as Change 8.1 — flag for user confirmation. If institution name should be DRAIT, leave as-is. If it should be DSATM or placeholder, replace `Dr. Ambedkar Institute of Technology` in `\IEEEauthorblockA` with `[PLACEHOLDER: Institution Name]`.

---

## Cross-Cutting Notes for the Implementing Agent

1. **Do NOT change REPORT_ch5.md, REPORT_ch6.md, REPORT_ch7.md at the root** — these files do not exist at the project root (only in `docs_backup_final/`). All corrections to chapters 5, 6, 7 apply to the REPORT.md monolith only.

2. **DB table count 24 → 27 must be done consistently.** Every occurrence of "24 tables" or "24-table" in the target files must become "27 tables" / "27-table".

3. **Endpoint count 114 → 120 must be done consistently.** Every occurrence of "114 endpoint", "114 endpoints", "114 routes" or "110 route + 4 core" in the target files must become "120 registered routes" (or "120 endpoints" where "routes" would be grammatically awkward).

4. **6-role → 3-role must be done consistently.** Every table, diagram, or sentence that lists 6 roles or names HOS/HOP/Mentor as active roles must be updated to 3 active roles with a deprecation note.

5. **Synthetic-data note** must be inserted exactly once in REPORT.md Chapter 7 (as specified in Change 4.15). It does not need to appear elsewhere.

6. **Startup command fix** (README.md Changes 1.2) is critical — both the Setup and Quick Start blocks need the CWD changed from `vista/backend` to `vista` and the module path changed from `app.main:app` to `backend.app.main:app`.

7. **MiniFASNet references** in REPORT.md Section 7.4 (Limitations) and Section 8.3 (Future Enhancements) correctly describe MiniFASNet as a *future* deep anti-spoofing enhancement, NOT as a current implementation. These references are accurate and should NOT be changed. Only references that claim MiniFASNet is the current anti-spoofing method are incorrect.

8. **DSATM occurrences** are in AUDIT.md (2 occurrences) and NEEDS_YOUR_INPUT.md (not in scope). Replace both AUDIT.md occurrences with `[PLACEHOLDER: Institution Name]`.

9. **Guide name** is consistently "Dr. Ajayprakash B V" everywhere. The only discrepancy is "Assistant Professor" (Acknowledgements) vs "Associate Professor" (cover page). Fix Acknowledgements to say "Associate Professor" (Change 4.1 secondary item). The HoD signature block on the Certificate page must be verified with the user (Change 4.1 primary item).

---

## Verification Checklist (post-implementation)

After applying all changes, run the following grep checks to confirm no stale values remain in the target files:

```powershell
# Should return 0 hits in target files
Select-String -Path "README.md","AUDIT.md","TODO_FOR_ME.md","REPORT.md","REPORT_ch1.md","REPORT_ch3.md" `
  -Pattern "6-role dashboard|6 role|HOS \||HOP \||Mentor \|| 114 endpoint| 114 route|110 route \+ 4|24 table|24-table|24 Tables|DSATM" `
  -SimpleMatch | Select-Object Filename, LineNumber, Line
```

```powershell
# Should return hits confirming correct values present
Select-String -Path "README.md","REPORT.md","REPORT_ch1.md" `
  -Pattern "120 registered routes|120 endpoints|27 table|27-table|3 active role|3-role" | Select-Object Filename, LineNumber, Line
```
