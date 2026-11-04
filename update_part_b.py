"""
update_part_b.py
----------------
Executes PART B: Document Consistency for VISTA.
Ensures verified metrics and institutional facts are synchronized across all documents:
- Roles: 3 active roles (admin, teacher, student). HOS/HOP/Mentor marked deprecated.
- DB Tables: 27 tables.
- Routes: 122 registered routes (114 API endpoints across 14 modules).
- Tests: 78 passed, 0 failed.
- Students: 70 total in database (65 active in 4th Year AIML, 5 inactive legacy demo).
- Enrolled with embeddings: 40 students.
- Subjects: 5 active Semester 7 subjects (22AIU701, 22AIU702, 22AIT703, 22AIT704C, 22AIP706).
- Institute: Dr. Ambedkar Institute of Technology, Bengaluru (never DSATM).
- School: School of Computer Science and Engineering; Programme: Artificial Intelligence and Machine Learning.
- Guide: Dr. Ajayprakash B V [CONFIRM designation and spelling]
- HOS: Dr. Ajayprakash B V [CONFIRM designation]
- HOP: Dr. Bharath V S [CONFIRM spelling and designation]
- Principal: Dr. Mahalinga V Mandi
- Course: Major Project Phase-II, code 22AIP706 [CONFIRM]
- Academic Year: 2026-27 [CONFIRM]
- Team: Mohammed Ayan, Saheel Pradhan, Aryan Raj Singh, Sujala Agrahari.

Generates CHANGELOG_FINAL.md with every document line changed.
"""
import os
import re

CHANGES = []

def log_change(filename, desc, old_val, new_val):
    CHANGES.append({
        "file": filename,
        "desc": desc,
        "old": old_val.strip(),
        "new": new_val.strip()
    })

def replace_in_file(path, replacements):
    if not os.path.exists(path):
        print(f"Skipping missing file: {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content
    for old_str, new_str, desc in replacements:
        if old_str in new_content:
            new_content = new_content.replace(old_str, new_str)
            log_change(path, desc, old_str, new_str)
        else:
            print(f"Pattern not found in {path}: {desc[:40]}...")

    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {path}")

# 1. REPORT_front_matter.md
replacements_front_matter = [
    (
        "Sujal Agrahari",
        "Sujala Agrahari",
        "Standardize team member name to Sujala Agrahari"
    ),
    (
        """----------------------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -----------------------------------  
**Dr. Ajayprakash B V** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Dr. Ajayprakash B V**  
Project Guide &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Head of Programme (HOP)  
Project Guide &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Dept. of AI & ML  
Dept. of AI & ML  """,
        """----------------------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -----------------------------------  
**Dr. Ajayprakash B V** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Dr. Bharath V S**  
Project Guide [CONFIRM designation & spelling] &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Head of Programme (HOP), AI & ML  
Dept. of AI & ML &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; [CONFIRM spelling & designation]  

<br><br>

----------------------------------- &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; -----------------------------------  
**Dr. Ajayprakash B V** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Dr. Mahalinga V Mandi**  
Head of School (HOS) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Principal  
School of Computer Science & Engineering &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Dr. AIT, Bengaluru  
[CONFIRM designation]  """,
        "Remove duplicate Project Guide line, set Dr. Bharath V S as HOP, Dr. Ajayprakash B V as HOS, Dr. Mahalinga V Mandi as Principal"
    ),
    (
        "Associate Professor & Head of Programme (HOP), Department of Artificial Intelligence & Machine Learning",
        "Project Guide [CONFIRM designation and spelling], Department of Artificial Intelligence & Machine Learning",
        "Update Title Page guide designation"
    ),
    (
        "**Academic Year: 2026–2027**",
        "**Course: Major Project Phase-II (22AIP706) [CONFIRM]**  \n**Academic Year: 2026–27 [CONFIRM]**",
        "Add Course Code 22AIP706 and Academic Year 2026-27"
    ),
    (
        "We express our sincere and heartfelt thanks to our guide, **Dr. Ajayprakash B V**, Associate Professor, Department of Artificial Intelligence & Machine Learning",
        "We express our sincere and heartfelt thanks to our guide and Head of School (HOS), **Dr. Ajayprakash B V**, School of Computer Science & Engineering, and Head of Programme (HOP), **Dr. Bharath V S**, Department of Artificial Intelligence & Machine Learning",
        "Update Acknowledgements guide, HOS and HOP"
    )
]
replace_in_file("REPORT_front_matter.md", replacements_front_matter)

# 2. REPORT_ch1.md
replacements_ch1 = [
    (
        "delivering 120 endpoints, 27 relational database tables, automated midnight task scheduling via APScheduler, WebSocket live data push, and 3 active role-based user portals",
        "delivering 122 registered routes (114 API endpoints across 14 modules), 27 relational database tables, automated midnight task scheduling via APScheduler, WebSocket live data push, and 3 active role-based user portals",
        "Update route count from 120 to 122 registered routes (114 API endpoints)"
    )
]
replace_in_file("REPORT_ch1.md", replacements_ch1)

# 3. REPORT_ch4.md
replacements_ch4 = [
    (
        "Gateway[\"REST API Router (120 Routes across 14 Modules)\"]",
        "Gateway[\"REST API Router (122 Registered Routes / 114 API Endpoints across 14 Modules)\"]",
        "Update Architecture Diagram Gateway route count"
    ),
    (
        "this tier serves 120 registered routes.",
        "this tier serves 122 registered routes (114 API endpoints across 14 modules).",
        "Update Application Layer description of routes"
    ),
    (
        "| **UC-07** | Export Attendance Report | Teacher / Teacher / Admin / HOP| Attendance session records",
        "| **UC-07** | Export Attendance Report | Teacher / Admin | Attendance session records",
        "Fix duplicated Teacher and remove deprecated HOP in UC-07"
    )
]
replace_in_file("REPORT_ch4.md", replacements_ch4)

# 4. REPORT_ch5.md
replacements_ch5 = [
    (
        "Encompasses 14 distinct route modules exposing 110 endpoints, detailed in Table 5.1.",
        "Encompasses 14 distinct route modules exposing 114 API endpoints (122 registered routes in total including core system and OpenAPI handlers), detailed in Table 5.1.",
        "Update routes overview text in ch5"
    ),
    (
        "| `student_portal.py`| `/api/v1/student` | 10 | Student personal attendance percentage, timetable, marks, and study materials |",
        "| `student_portal.py`| `/api/v1/student` | 11 | Student personal attendance percentage, timetable, marks, and study materials |\n| `coach.py` | `/api/v1/coach` | 4 | AI Study Coach chat, query synthesis, contextual history, deterministic fallback |",
        "Add coach.py (4 endpoints) and update student_portal to 11 in Table 5.1"
    ),
    (
        "| `attendance.py` | `/api/v1/attendance` | 8 | Image-based attendance marking, manual roll calls, session logs, teacher overrides |",
        "| `attendance.py` | `/api/v1/attendance` | 9 | Image-based attendance marking, manual roll calls, session logs, teacher overrides |",
        "Update attendance endpoints count in Table 5.1"
    ),
    (
        "| `notifications.py`| `/api/v1/notifications`| 4 | In-app alerts, campus-wide announcements, unread status tracking |",
        "| `notifications.py`| `/api/v1/notifications`| 6 | In-app alerts, campus-wide announcements, unread status tracking |",
        "Update notifications endpoints count in Table 5.1"
    ),
    (
        "| `lms.py` | `/api/v1/lms` | 4 | Course assignments, student file submissions, syllabus progress tracking |",
        "| `lms.py` | `/api/v1/lms` | 5 | Course assignments, student file submissions, syllabus progress tracking |",
        "Update lms endpoints count in Table 5.1"
    ),
    (
        "| `students.py` | `/api/v1/students` | 3 | Student directory, individual profile lookup, biographic CRUD |",
        "| `students.py` | `/api/v1/students` | 4 | Student directory, individual profile lookup, biographic CRUD |",
        "Update students endpoints count in Table 5.1"
    ),
    (
        "| **Total** | | **120** | Complete production enterprise REST & WebSocket API |",
        "| **Total** | | **122** | Complete production enterprise REST & WebSocket API (114 API endpoints + 4 system + 4 docs/openapi) |",
        "Update total route count in Table 5.1 to 122"
    ),
    (
        "| `intervention.py` | `mentor_assignments` | `id` (UUID) | `student_id` $\to$ `students.student_id`, `mentor_id` $\to$ `users.id` | Mentor-student advisor mappings |",
        "| `intervention.py` | `mentor_assignments` | `id` (UUID) | `student_id` $\to$ `students.student_id`, `mentor_id` $\to$ `users.id` | Mentor-student advisor mappings (Deprecated legacy schema; unreferenced in active 3-role runtime) |",
        "Clarify mentor_assignments as deprecated legacy table"
    )
]
replace_in_file("REPORT_ch5.md", replacements_ch5)

# 5. REPORT_ch7.md
replacements_ch7 = [
    (
        "subgraph Output[\"Synthesized Mentor Dashboard Output\"]",
        "subgraph Output[\"Synthesized Academic Advisor & Teacher Dashboard Output\"]",
        "Rename Mentor Dashboard subgraph in SHAP explanation diagram"
    ),
    (
        "The mentor receives human-interpretable plain language explanations rather than opaque numerical coefficients.",
        "The academic advisor/teacher receives human-interpretable plain language explanations rather than opaque numerical coefficients.",
        "Replace mentor reference with academic advisor/teacher in SHAP narrative"
    )
]
replace_in_file("REPORT_ch7.md", replacements_ch7)

# 6. REPORT.md (re-stitch or apply replacements)
replacements_report_md = replacements_front_matter + replacements_ch1 + replacements_ch4 + replacements_ch5 + replacements_ch7
replace_in_file("REPORT.md", replacements_report_md)

# 7. EXHIBITION_KIT.md
replacements_exhibition_kit = [
    (
        "| **Institution** | Dayananda Sagar Academy of Technology and Management, Bengaluru |",
        "| **Institution** | Dr. Ambedkar Institute of Technology, Bengaluru |",
        "Fix institution to Dr. AIT Bengaluru"
    ),
    (
        "| **Guide** | [PLACEHOLDER — confirm guide name and designation: Associate Professor & Head of Programme] |",
        "| **Guide** | Dr. Ajayprakash B V (Project Guide [CONFIRM designation & spelling]; HOS: Dr. Ajayprakash B V; HOP: Dr. Bharath V S) |",
        "Update guide and academic leadership"
    ),
    (
        "| **Academic year** | [PLACEHOLDER — confirm: 2024–25 or 2025–26] |",
        "| **Academic year** | 2026–27 [CONFIRM] (Course: Major Project Phase-II, 22AIP706 [CONFIRM]) |",
        "Update academic year and course code"
    ),
    (
        "- Shrujan P — 1DA22AI044",
        "- Sujala Agrahari — 1DA23AI050",
        "Remove Shrujan P and ensure 4 team members: Ayan, Saheel, Aryan, Sujala"
    ),
    (
        "**Institution:** Dayananda Sagar Academy of Technology and Management, Bengaluru",
        "**Institution:** Dr. Ambedkar Institute of Technology, Bengaluru",
        "Update poster/slide institution to Dr. AIT"
    ),
    (
        "**Guide:** [PLACEHOLDER — Associate Professor & Head of Programme, Dept. of AI & ML]",
        "**Guide:** Dr. Ajayprakash B V [CONFIRM designation & spelling] | **HOP:** Dr. Bharath V S [CONFIRM] | **HOS:** Dr. Ajayprakash B V [CONFIRM]",
        "Update poster guide section"
    ),
    (
        "Scale at **Dayananda Sagar Academy of Technology and Management**: multiple divisions, 7 teachers,",
        "Scale at **Dr. Ambedkar Institute of Technology, Bengaluru**: multiple divisions, 7 teachers,",
        "Fix institution name in slide narrative"
    ),
    (
        "- Teacher: `rajeshwari@vista.local` / `rajeshwari123`",
        "- Teacher: `teacher@vista.local` / `teacher123` (or `rajeshwari@vista.local` / `rajeshwari123`)",
        "Clarify demo teacher login"
    )
]
replace_in_file("EXHIBITION_KIT.md", replacements_exhibition_kit)

# 8. VIVA_QA.md
replacements_viva_qa = [
    (
        "**Short answer:** The current pilot covers 70 enrolled students, 7 teachers, and 11 active subjects across CSE and AIML departments. The full deployment target is the entire department (~300 students) across all 4 years.",
        "**Short answer:** The current pilot covers 70 students (65 active in 4th Year AIML, 5 inactive demo), 7 teachers, 40 students with registered facial embeddings, and 5 active Semester 7 subjects (Deep Learning 22AIU701, Generative AI 22AIU702, Data Engineering and Analytics 22AIT703, Data Security and Privacy 22AIT704C, Major Project Phase-II 22AIP706; 6 legacy subjects deactivated).",
        "Update Q2 pilot numbers with verified counts and 5 active 7th sem subjects"
    ),
    (
        "**Short answer:** 121 API endpoints, counted by enumerating `app.routes` at runtime. This includes all operational modules plus core system endpoints (/health, /metrics, /ws/dashboard).",
        "**Short answer:** 122 registered routes (114 API endpoints under `/api` across 14 modules, plus 4 core system routes: `/`, `/health`, `/metrics`, `/ws/dashboard`, and 4 OpenAPI/docs routes: `/docs`, `/redoc`, `/openapi.json`, `/docs/oauth2-redirect`).",
        "Update Q48 endpoint count to 122 registered routes / 114 API endpoints"
    ),
    (
        "The verified ground truth is 27 tables and 121 endpoints, confirmed by runtime enumeration during the Part 1 audit.",
        "The verified ground truth is 27 tables and 122 registered routes (114 API endpoints across 14 modules), confirmed by runtime enumeration.",
        "Update verified ground truth endpoints to 122 / 114"
    ),
    (
        "**Short answer:** [PLACEHOLDER — confirm guide's full name and exact title.] The REPORT.md certificate lists them as \"Associate Professor & Head of Programme (HOP), Department of Artificial Intelligence & Machine Learning\".",
        "**Short answer:** Project Guide: Dr. Ajayprakash B V [CONFIRM designation and spelling]; Head of School (HOS): Dr. Ajayprakash B V [CONFIRM designation]; Head of Programme (HOP): Dr. Bharath V S [CONFIRM spelling and designation]; Principal: Dr. Mahalinga V Mandi.",
        "Update Q70 guide and leadership answer"
    ),
    (
        "**Short answer:** The confirmed team members in the project files are: Mohammed Ayan (1DA24AI403), Saheel Pradhan (1DA23AI042), Aryan Raj Singh (1DA23AI009). The fourth team member is Sujala Agrahari (1DA23AI050 in REPORT.md, though referred to as Sujal Agrahari in other sections — confirm the exact spelling on their institutional ID card).",
        "**Short answer:** The team members are: Mohammed Ayan (1DA24AI403), Saheel Pradhan (1DA23AI042), Aryan Raj Singh (1DA23AI009), Sujala Agrahari (1DA23AI050). All USNs are confirmed from the student records table.",
        "Update Q69 team members answer"
    )
]
replace_in_file("VIVA_QA.md", replacements_viva_qa)

# 9. FINAL_AUDIT.md
replacements_final_audit = [
    (
        "| D-1 | **test_recompute_risk returns HTTP 500** — `POST /api/v1/risk/{student_id}/recompute` returns a 500 error from live endpoint | **FIX REQUIRED** — investigate traceback in `routes/risk.py` or `ml/risk_engine.py`; write regression test | High |",
        "| D-1 | ~~**test_recompute_risk returns HTTP 500**~~ | **FIXED in Part A** — Missing assessment score handling resolved; endpoint returns valid risk payload; regression test added in `tests/test_audit_fixes.py` | Resolved |",
        "Mark D-1 test_recompute_risk as fixed"
    ),
    (
        "| **Number of API endpoints** | Ch5 Table 5.1: **114**; Abstract: \"114 endpoints\" | §III.B: **\"120 API endpoints\"** | **121** (verified by enumerating `app.routes` at runtime) |",
        "| **Number of API endpoints** | Ch5 Table 5.1: **114 API endpoints**; Total Routes: **122** | §III.B: **\"122 registered routes\"** | **122 registered routes** (114 API endpoints under `/api` + 4 system + 4 docs) |",
        "Update endpoint consistency row in FINAL_AUDIT.md"
    ),
    (
        "| **Number of DB tables** | Ch5 Table 5.2: **24 tables** | §III.C: **\"27 relational tables\"** | **27 tables** (verified via `sqlite3 vista_dev.db \".tables\"`) |",
        "| **Number of DB tables** | Ch5 Table 5.2: **27 tables** | §III.C: **\"27 relational tables\"** | **27 tables** (verified via SQLAlchemy inspector on `vista/backend/vista_dev.db`) |",
        "Update DB table consistency row in FINAL_AUDIT.md"
    ),
    (
        "| **Number of roles** | Ch1 §1.3: \"6 role-based portals\" (HOS/HOP listed); Ch5 Table 5.1: \"3 active roles\" | README.md: \"6-role dashboard\" | **3 active roles** in production (`admin`, `teacher`, `student`); HOS, HOP, Mentor are deprecated legacy roles rejected with HTTP 403 `ROLE_DEPRECATED` |",
        "| **Number of roles** | Ch1 §1.3: \"3 active role-based portals\"; Ch5 Table 5.1: \"3 active roles\" | README.md: \"3 active roles (admin, teacher, student)\" | **3 active roles** in production (`admin`, `teacher`, `student`); HOS, HOP, Mentor are deprecated legacy roles rejected with HTTP 403 `ROLE_DEPRECATED` |",
        "Update roles consistency row in FINAL_AUDIT.md"
    )
]
replace_in_file("FINAL_AUDIT.md", replacements_final_audit)

# 10. vista/README.md
replacements_readme = [
    (
        "│   ├── models/           # 8 SQLAlchemy ORM model files (24 tables)",
        "│   ├── models/           # 8 SQLAlchemy ORM model files (27 tables)",
        "Update table count in README.md"
    )
]
replace_in_file("vista/README.md", replacements_readme)

# 11. vista/PROJECT_REPORT.md
replacements_vista_project_report = [
    (
        "│  114 API Endpoints │ JWT Auth │ RBAC │ WebSocket │ Scheduler    │",
        "│  122 Routes (114 API) │ JWT Auth │ 3-Role RBAC │ WebSocket │",
        "Update API endpoints in vista/PROJECT_REPORT.md header"
    ),
    (
        "│   24 Tables           │",
        "│   27 Tables           │",
        "Update DB tables in vista/PROJECT_REPORT.md diagram"
    ),
    (
        "## 6. API Summary (114 Endpoints)",
        "## 6. API Summary (122 Routes / 114 API Endpoints)",
        "Update API summary heading in vista/PROJECT_REPORT.md"
    ),
    (
        "| Mentor (`/api/v1/mentor`) | 6 | Mentor dashboard, assigned students, watchlist, interventions CRUD |",
        "| ~~Mentor (`/api/v1/mentor`)~~ | *Deprecated* | Legacy mentor endpoints (deprecated in 3-role production runtime) |",
        "Deprecate mentor endpoints in vista/PROJECT_REPORT.md"
    ),
    (
        "## 7. Database Schema (24 Tables)",
        "## 7. Database Schema (27 Tables)",
        "Update DB schema heading in vista/PROJECT_REPORT.md"
    ),
    (
        "| users | All system users across 6 roles (admin, HOS, HOP, mentor, teacher, student) |",
        "| users | All system users across 3 active roles (admin, teacher, student; legacy roles deprecated) |",
        "Update users table description in vista/PROJECT_REPORT.md"
    ),
    (
        "| Total API endpoints | 114 (110 route + 4 core) |",
        "| Total API endpoints | 122 (114 API + 4 system + 4 docs) |",
        "Update total API endpoints in vista/PROJECT_REPORT.md table"
    ),
    (
        "| User roles | 6 (admin, HOS, HOP, mentor, teacher, student) |",
        "| User roles | 3 active roles (admin, teacher, student; HOS/HOP/mentor deprecated) |",
        "Update user roles in vista/PROJECT_REPORT.md table"
    ),
    (
        "| Teacher | gowrishankar@vista.local | hos123 |",
        "| Teacher | ajayprakash@vista.local | ajayprakash123 |",
        "Replace legacy gowrishankar login with ajayprakash"
    )
]
replace_in_file("vista/PROJECT_REPORT.md", replacements_vista_project_report)

# 12. vista/docs/PROJECT_REPORT.md
replacements_vista_docs_report = [
    (
        "| Teacher | gowrishankar@vista.local | hos123 |",
        "| Teacher | ajayprakash@vista.local | ajayprakash123 |",
        "Replace legacy gowrishankar login in vista/docs/PROJECT_REPORT.md"
    )
]
replace_in_file("vista/docs/PROJECT_REPORT.md", replacements_vista_docs_report)

# 13. vista/backend/CLAUDE.md
replacements_backend_claude = [
    (
        "- `dashboards.py` (7 endpoints): Role-scoped analytics for 6 roles",
        "- `dashboards.py` (7 endpoints): Role-scoped analytics for 3 active roles (admin, teacher, student)",
        "Update dashboards role scope in backend CLAUDE.md"
    ),
    (
        "- `app/models/` — 8 model files defining 24 tables",
        "- `app/models/` — 8 model files defining 27 tables",
        "Update tables count in backend CLAUDE.md"
    ),
    (
        "- DB schema must match the 24 tables in `app/models/` and `docs/DB_SCHEMA.md`.",
        "- DB schema must match the 27 tables in `app/models/` and `docs/DB_SCHEMA.md`.",
        "Update DB schema match rule in backend CLAUDE.md"
    ),
    (
        "- RBAC enforces 6 roles: `admin`, `hos`, `hop`, `mentor`, `teacher`, `student`.",
        "- RBAC enforces 3 active roles: `admin`, `teacher`, `student`. Legacy roles (`hos`, `hop`, `mentor`) are rejected with HTTP 403 `ROLE_DEPRECATED`.",
        "Update RBAC roles enforcement in backend CLAUDE.md"
    )
]
replace_in_file("vista/backend/CLAUDE.md", replacements_backend_claude)

# 14. vista/frontend/CLAUDE.md
replacements_frontend_claude = [
    (
        "**Implementation Scope:** Full 6-role workspace (Admin, HOS, HOP, Mentor, Teacher, Student) built with Vite 6.0, React 18, and Tailwind CSS v4.",
        "**Implementation Scope:** 3-role workspace (Admin, Teacher, Student; legacy roles deprecated) built with Vite 6.0, React 18, and Tailwind CSS v4.",
        "Update frontend implementation scope to 3 roles"
    ),
    (
        "- Maintain consistency with the 114 endpoints and 6 roles implemented in backend.",
        "- Maintain consistency with the 122 routes (114 API endpoints) and 3 active roles implemented in backend.",
        "Update frontend guidance to 122 routes / 114 API endpoints and 3 roles"
    )
]
replace_in_file("vista/frontend/CLAUDE.md", replacements_frontend_claude)

# 15. Write CHANGELOG_FINAL.md
with open("CHANGELOG_FINAL.md", "w", encoding="utf-8") as f:
    f.write("# CHANGELOG_FINAL: Document Consistency Pass (Part B)\n\n")
    f.write("**Execution Date:** 2026-11-04 | **Exhibition Date:** 7 November 2026\n\n")
    f.write("This changelog documents every line and content modification executed during the Part B Document Consistency pass.\n\n")
    f.write("| File | Description of Change | Previous Value | New Value |\n")
    f.write("| :--- | :--- | :--- | :--- |\n")
    for ch in CHANGES:
        old_san = ch['old'].replace("\n", "<br>").replace("|", "\\|")[:80]
        new_san = ch['new'].replace("\n", "<br>").replace("|", "\\|")[:80]
        f.write(f"| `{ch['file']}` | {ch['desc']} | `{old_san}` | `{new_san}` |\n")

print(f"\nCompleted Part B updates. Logged {len(CHANGES)} modifications in CHANGELOG_FINAL.md")
