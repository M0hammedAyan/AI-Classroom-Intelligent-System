# VISTA LMS — Role-Based Academic Management Architecture

> **Status:** Planning Complete — Ready for Implementation
> **Last Updated:** 2026-06-24
> **Principle:** Every role sees a completely different product.

---

## 1. Information Architecture

```
VISTA Platform
│
├── /admin/*          ← Institution-wide control
│   ├── Dashboard     (KPI: schools, depts, students, risk, attendance)
│   ├── Schools       (CRUD, assign HOS)
│   ├── Departments   (CRUD, assign HOP)
│   ├── Users         (Create any role, permissions, status)
│   ├── Analytics     (Institution-wide trends)
│   ├── Reports       (All exports)
│   ├── Settings      (System config)
│   └── Audit Logs    (Who did what, when)
│
├── /hos/*            ← School-scoped control
│   ├── Dashboard     (KPI: departments, staff, students in school)
│   ├── Departments   (View/manage within school)
│   ├── Staff         (HOPs, mentors, teachers in school)
│   ├── Students      (All students in school)
│   ├── Analytics     (School-level trends)
│   └── Reports       (School exports)
│
├── /hop/*            ← Department-scoped control
│   ├── Dashboard     (KPI: classes, teachers, subjects, risk)
│   ├── Classes       (Sections in department)
│   ├── Teachers      (Assign subjects, manage)
│   ├── Subjects      (CRUD within department)
│   ├── Risk Center   (All at-risk students in dept)
│   ├── Analytics     (Department trends)
│   └── Reports       (Department exports)
│
├── /mentor/*         ← Assigned-students only
│   ├── Dashboard     (KPI: assigned count, high-risk, attendance avg)
│   ├── Students      (Only assigned students)
│   ├── Watchlist     (High/medium risk students)
│   ├── Interventions (Track actions taken)
│   └── Reports       (Mentee reports)
│
└── /teacher/*        ← Subject + class scoped
    ├── Dashboard     (KPI: classes today, attendance, at-risk in class)
    ├── Classes       (Only assigned classes)
    ├── Attendance    (Mark, view, override)
    ├── Marks         (Enter scores per subject)
    ├── Assignments   (Create, track submissions)
    └── Reports       (Class/subject reports)
```

---

## 2. Permission Matrix

| Action | Admin | HOS | HOP | Mentor | Teacher |
|---|---|---|---|---|---|
| View all schools | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage schools | ✅ | ❌ | ❌ | ❌ | ❌ |
| View own school | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manage departments | ✅ | ✅ | ❌ | ❌ | ❌ |
| View own department | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create HOS | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create HOP | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create Mentor | ✅ | ✅ | ✅ | ❌ | ❌ |
| Create Teacher | ✅ | ✅ | ✅ | ❌ | ❌ |
| Assign mentor to students | ✅ | ✅ | ✅ | ❌ | ❌ |
| Assign teacher to subject | ✅ | ✅ | ✅ | ❌ | ❌ |
| View all students | ✅ | School | Dept | Assigned | Class |
| View risk flags | ✅ | School | Dept | Assigned | Class |
| Recompute risk | ✅ | ✅ | ✅ | ❌ | ❌ |
| Mark attendance | ✅ | ✅ | ✅ | ❌ | ✅ |
| Override attendance | ✅ | ✅ | ✅ | ❌ | ✅ |
| Enter marks | ✅ | ✅ | ✅ | ❌ | ✅ (own subject) |
| Import CSV scores | ✅ | ✅ | ✅ | ❌ | ✅ (own subject) |
| Export reports | ✅ | ✅ | ✅ | ✅ | ✅ |
| Approve access requests | ✅ | ✅ | ✅ | ❌ | ❌ |
| View audit logs | ✅ | ❌ | ❌ | ❌ | ❌ |
| System settings | ✅ | ❌ | ❌ | ❌ | ❌ |
| Enroll faces | ✅ | ✅ | ✅ | ❌ | ✅ |
| SHAP explanations | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 3. Dashboard Widgets Per Role

### Admin Dashboard
```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Schools  │ Depts    │ Students │ Teachers │ Mentors  │
│    3     │   12     │   850    │   45     │   20     │
├──────────┼──────────┼──────────┴──────────┴──────────┤
│ Attend%  │ Risk Hi  │                                │
│  78.5%   │   23     │  [Attendance Trend Chart]      │
├──────────┼──────────┤                                │
│ Pending  │ Active   │                                │
│ Requests │ Users    │                                │
│    5     │   67     │  [Risk Distribution Chart]     │
└──────────┴──────────┴────────────────────────────────┘
```

### HOS Dashboard
```
┌──────────┬──────────┬──────────┬──────────┐
│ Depts    │ Students │ Teachers │ Attend%  │
│    4     │   320    │   18     │  81.2%   │
├──────────┴──────────┴──────────┴──────────┤
│  [Department-wise Attendance Comparison]   │
├────────────────────────────────────────────┤
│  [High Risk Students in School - Table]    │
└────────────────────────────────────────────┘
```

### HOP Dashboard
```
┌──────────┬──────────┬──────────┬──────────┐
│ Classes  │ Students │ Subjects │ Risk Hi  │
│    3     │   90     │    8     │    7     │
├──────────┴──────────┴──────────┴──────────┤
│  [Class-wise Attendance + Performance]     │
├────────────────────────────────────────────┤
│  [At-Risk Students with Reasons - Cards]   │
└────────────────────────────────────────────┘
```

### Mentor Dashboard
```
┌──────────┬──────────┬──────────┬──────────┐
│ My       │ High     │ Avg      │ Avg      │
│ Students │ Risk     │ Attend%  │ Score    │
│   15     │    3     │  72.4%   │  58.2%   │
├──────────┴──────────┴──────────┴──────────┤
│  [Student Watchlist - Risk Sorted]         │
├────────────────────────────────────────────┤
│  [Recent Interventions Log]                │
└────────────────────────────────────────────┘
```

### Teacher Dashboard
```
┌──────────┬──────────┬──────────┬──────────┐
│ My       │ My       │ Attend   │ At Risk  │
│ Classes  │ Subjects │ Today    │ in Class │
│    2     │    3     │  25/30   │    4     │
├──────────┴──────────┴──────────┴──────────┤
│  [Today's Classes - Quick Attendance]      │
├────────────────────────────────────────────┤
│  [Recent Marks Entry Summary]              │
└────────────────────────────────────────────┘
```

---

## 4. User Flows

### Admin → Create School Structure
```
Login → Admin Dashboard → Schools → Create School →
  → Create Department (under school) →
    → Create Class Section (under dept) →
      → Assign HOS to school →
        → Assign HOP to department
```

### HOP → Manage Department
```
Login → HOP Dashboard → Teachers → Assign Teacher to Subject →
  → Classes → View Students →
    → Risk Center → Review At-Risk →
      → Recompute Risk
```

### Teacher → Mark Attendance + Enter Marks
```
Login → Teacher Dashboard → Classes → Select Class →
  → Attendance → Upload Photo → Multi-face Recognition →
    → Confirm Results → Save

Login → Teacher Dashboard → Marks → Select Subject →
  → Enter Scores → Save → (Risk auto-recomputes)
```

### Mentor → Monitor Students
```
Login → Mentor Dashboard → Watchlist (sorted by risk) →
  → Click Student → View SHAP Explanation →
    → Log Intervention → Track Progress
```

---

## 5. Navigation Architecture

### Admin Sidebar
```
📊 Dashboard
🏫 Schools
🏛️ Departments
👥 Users & Roles
🔐 Permissions
📈 Analytics
📋 Reports
⚙️ Settings
📝 Audit Logs
```

### HOS Sidebar
```
📊 Dashboard
🏛️ Departments
👨‍🏫 Staff
🎓 Students
📈 Analytics
📋 Reports
```

### HOP Sidebar
```
📊 Dashboard
📚 Classes
👨‍🏫 Teachers
📖 Subjects
⚠️ Risk Center
📈 Analytics
📋 Reports
```

### Mentor Sidebar
```
📊 Dashboard
🎓 My Students
👁️ Watchlist
🤝 Interventions
📋 Reports
```

### Teacher Sidebar
```
📊 Dashboard
📚 My Classes
✅ Attendance
📝 Marks
📄 Assignments
📋 Reports
```

---

## 6. Database Schema (Complete)

### Core Tables

| Table | Columns | Purpose |
|---|---|---|
| users | id, name, email, password_hash, role, school_id, department_id, custom_permissions, is_active, created_at, created_by | All system users |
| schools | id, name, code, is_active, created_at | Institution schools |
| departments | id, school_id, name, code, is_active, created_at | School departments |
| class_sections | id, department_id, name, code, semester, is_active, created_at | Class groups |
| subjects | id, department_id, name, code, semester, credits, created_at | Academic subjects |
| students | id, name, class_section_id, department_id, school_id, enrollment_year, is_active, embedding, created_at | All students |

### Relationship Tables

| Table | Columns | Purpose |
|---|---|---|
| mentor_assignments | id, mentor_id, student_id, assigned_at, is_active | Mentor → students |
| teacher_subjects | id, teacher_id, subject_id, class_section_id, assigned_at, is_active | Teacher → subject + class |

### Academic Tables

| Table | Columns | Purpose |
|---|---|---|
| attendance | id, student_id, class_section_id, session_date, status, confidence, marked_by, created_at | Attendance records |
| scores | id, student_id, subject_id, score, max_score, assessment_type, date, entered_by, created_at | Academic scores |
| assignments | id, subject_id, class_section_id, title, due_date, created_by, created_at | Assignments issued |
| assignment_submissions | id, assignment_id, student_id, submitted_at, score, graded_by | Student submissions |

### System Tables

| Table | Columns | Purpose |
|---|---|---|
| risk_flags | id, student_id, risk_level, risk_score, reasons, confidence, computed_at | Risk predictions |
| access_requests | id, requester_id, request_type, target_details, status, reviewed_by, created_at | Approval workflow |
| audit_logs | id, user_id, action, target_type, target_id, details, ip_address, created_at | Activity tracking |
| interventions | id, mentor_id, student_id, type, notes, outcome, created_at | Mentor actions |

---

## 7. API Architecture

### Auth & RBAC
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me                    → current user + permissions
```

### Admin APIs (/api/v1/admin/*)
```
CRUD   /admin/schools
CRUD   /admin/departments
CRUD   /admin/class-sections
CRUD   /admin/users
PATCH  /admin/users/{id}/permissions
GET    /admin/analytics/institution
GET    /admin/audit-logs
```

### HOS APIs (/api/v1/hos/*)
```
GET    /hos/dashboard
GET    /hos/departments
GET    /hos/staff
GET    /hos/students
GET    /hos/analytics
GET    /hos/reports
```

### HOP APIs (/api/v1/hop/*)
```
GET    /hop/dashboard
GET    /hop/classes
GET    /hop/teachers
GET    /hop/subjects
GET    /hop/risk-center
GET    /hop/analytics
```

### Mentor APIs (/api/v1/mentor/*)
```
GET    /mentor/dashboard
GET    /mentor/students
GET    /mentor/watchlist
POST   /mentor/interventions
GET    /mentor/interventions
```

### Teacher APIs (/api/v1/teacher/*)
```
GET    /teacher/dashboard
GET    /teacher/classes
POST   /teacher/attendance/mark
GET    /teacher/attendance/log
POST   /teacher/marks
GET    /teacher/marks
POST   /teacher/assignments
GET    /teacher/assignments
```

### Shared APIs
```
GET    /api/v1/students/{id}/risk
GET    /api/v1/students/{id}/risk/explain
GET    /api/v1/export/report
```

---

## 8. Frontend Component Tree

```
App.jsx
├── AuthGuard (redirects based on role)
│
├── AdminLayout/
│   ├── AdminSidebar
│   ├── AdminDashboard (KPI widgets + charts)
│   ├── SchoolsManagement
│   ├── DepartmentsManagement
│   ├── UsersManagement
│   ├── AnalyticsCenter
│   ├── ReportsCenter
│   ├── SystemSettings
│   └── AuditLogs
│
├── HOSLayout/
│   ├── HOSSidebar
│   ├── HOSDashboard
│   ├── HOSDepartments
│   ├── HOSStaff
│   ├── HOSStudents
│   ├── HOSAnalytics
│   └── HOSReports
│
├── HOPLayout/
│   ├── HOPSidebar
│   ├── HOPDashboard
│   ├── HOPClasses
│   ├── HOPTeachers
│   ├── HOPSubjects
│   ├── HOPRiskCenter
│   ├── HOPAnalytics
│   └── HOPReports
│
├── MentorLayout/
│   ├── MentorSidebar
│   ├── MentorDashboard
│   ├── MentorStudents
│   ├── MentorWatchlist
│   ├── MentorInterventions
│   └── MentorReports
│
└── TeacherLayout/
    ├── TeacherSidebar
    ├── TeacherDashboard
    ├── TeacherClasses
    ├── TeacherAttendance
    ├── TeacherMarks
    ├── TeacherAssignments
    └── TeacherReports
```

---

## 9. Development Roadmap

| Phase | What | Depends On |
|---|---|---|
| **Phase 1** | Auth + RBAC middleware + role routing | Nothing |
| **Phase 2** | Institution structure (schools, depts, classes) | Phase 1 |
| **Phase 3** | User management (create all roles, scoped) | Phase 1 + 2 |
| **Phase 4** | Teacher system (subjects, marks, attendance) | Phase 3 |
| **Phase 5** | Mentor system (assignments, watchlist, interventions) | Phase 3 |
| **Phase 6** | HOP dashboard + department analytics | Phase 4 + 5 |
| **Phase 7** | HOS dashboard + school analytics | Phase 6 |
| **Phase 8** | Admin dashboard + institution analytics | Phase 7 |
| **Phase 9** | Reports + exports (PDF, CSV) per role | Phase 4-8 |
| **Phase 10** | Audit logs + optimization + testing | All |

---

## 10. Key Design Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | Role-based routing (/admin/*, /teacher/*) | Each role is a completely different product |
| 2 | Scoped data access at API level | Never return data outside user's scope |
| 3 | Separate layout per role | Different sidebar, navigation, widgets |
| 4 | Audit everything | Admin needs full visibility |
| 5 | Approval workflows for mentors/teachers | Prevents unauthorized access |
| 6 | Auto-assign students to school/dept/class on admission | Reduces admin workload |
| 7 | SHAP available to all roles | Every role benefits from explainability |
| 8 | Intervention tracking for mentors | Proves mentor engagement |
