# VISTA — Dashboard Interaction Map

> **Principle:** Every dashboard is an operational workspace, not a presentation.
> Every widget is clickable. Every click leads somewhere actionable.
> All roles can drill into individual student reports.

---

## Universal Interaction Patterns

### Every KPI Card
```
[KPI Card] → Click → Filtered list view → Click row → Detail page → Actions
```

### Every Table Row
```
[Row] → Hover shows quick actions
      → Click → Detail page
      → Actions: View | Edit | Assign | Export | Related
```

### Every Chart
```
[Chart] → Click segment/bar → Filtered data
        → Controls: Filter | Sort | Date Range | Export PNG/CSV
```

### Student Drill-Down (Available to ALL roles)
```
Any student name/ID → Student Profile
  ├── Overview (name, class, enrollment, photo)
  ├── Attendance Tab (calendar view, stats, trend)
  ├── Academics Tab (scores by subject, trend chart)
  ├── Risk Tab (current level, SHAP chart, history)
  ├── Recommendations (actionable items)
  └── Actions: Export PDF | Recompute Risk | Log Intervention | Notify
```

---

## ADMIN DASHBOARD — Interaction Map

```
┌─────────────────────────────────────────────────────────────────────┐
│ ADMIN COMMAND CENTER                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│ │ Schools  │  │ Depts    │  │ Students │  │ Teachers │           │
│ │    3     │  │   12     │  │   850    │  │   45     │           │
│ │ [CLICK]  │  │ [CLICK]  │  │ [CLICK]  │  │ [CLICK]  │           │
│ └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│      │              │              │              │                 │
│      ▼              ▼              ▼              ▼                 │
│  /admin/schools  /admin/depts  Student List  /admin/users?role=     │
│                                 (all, filterable)  teacher          │
│                                     │                              │
│ ┌──────────┐  ┌──────────┐         ▼                              │
│ │ High Risk│  │ Attend%  │  Student Profile Page                   │
│ │   23     │  │  78.5%   │  (any student, full detail)             │
│ │ [CLICK]  │  │ [CLICK]  │                                        │
│ └────┬─────┘  └────┬─────┘                                        │
│      │              │                                              │
│      ▼              ▼                                              │
│  Risk Center     Attendance Stats                                  │
│  (all HIGH       (institution-wide,                                │
│   students)       by school, by dept)                              │
│      │                                                             │
│      ▼                                                             │
│  Click student → Student Profile → SHAP → Recommendations         │
│                                                                     │
│ ┌──────────┐  ┌──────────┐                                        │
│ │ Pending  │  │ Active   │                                        │
│ │ Requests │  │ Users    │                                        │
│ │    5     │  │   67     │                                        │
│ │ [CLICK]  │  │ [CLICK]  │                                        │
│ └────┬─────┘  └────┬─────┘                                        │
│      │              │                                              │
│      ▼              ▼                                              │
│  Access Requests  User Management                                  │
│  (Approve/Reject) (Create/Edit/Permissions)                        │
│                                                                     │
│ [CHARTS]                                                           │
│ ┌─────────────────────────────┐ ┌─────────────────────────────┐   │
│ │ Attendance Trend (Weekly)   │ │ Risk Distribution (Pie)     │   │
│ │ Click bar → week details    │ │ Click segment → filtered    │   │
│ │ Filter: school, dept, date  │ │ student list at that level  │   │
│ │ Export: PNG, CSV            │ │ Export: PNG, CSV            │   │
│ └─────────────────────────────┘ └─────────────────────────────┘   │
│                                                                     │
│ [RECENT ACTIVITY TABLE]                                            │
│ │ Student    │ Event         │ Time    │ Actions              │    │
│ │ CS22B003   │ Marked HIGH   │ 2min    │ View | Profile | Act │    │
│ │ CS22B007   │ 5th absence   │ 1hr     │ View | Profile | Act │    │
│ └────────────┴───────────────┴─────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Admin Actions from Dashboard
| Widget/Click | Destination | Available Actions |
|---|---|---|
| Schools count | Schools list | Create, Edit, Assign HOS, View departments |
| Departments count | Departments list | Create, Edit, Assign HOP, View students |
| Students count | Student list (all) | Filter by school/dept/class, Click → Profile |
| Teachers count | Users filtered by teacher | Edit, Assign subject, View performance |
| High Risk | Risk center (HIGH filtered) | Click student → Profile → SHAP → Intervene |
| Attendance % | Attendance analytics | Filter by school/dept/date, Drill into days |
| Pending Requests | Request queue | Approve, Reject, View requester profile |
| Attendance chart bar | That week's records | List of students absent/present |
| Risk pie segment | Students at that level | Click student → full profile |
| Activity row | Student profile | View, Export, Assign mentor, Recompute |

---

## HOS DASHBOARD — Interaction Map

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEAD OF SCHOOL — [School of Computing]                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│ │ Depts    │  │ Students │  │ Teachers │  │ Attend%  │           │
│ │    4     │  │   320    │  │   18     │  │  81.2%   │           │
│ │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │           │
│ │ Dept list│  │ All studs│  │ Staff pg │  │ Stats pg │           │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                     │                                              │
│                     ▼                                              │
│              Student List (school-scoped)                           │
│              Click any → Student Profile                            │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ Department Comparison Chart                                  │    │
│ │ [AIML: 85%] [CSE: 78%] [ISE: 72%] [CSBS: 80%]            │    │
│ │ Click dept bar → Department detail + students               │    │
│ └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ High Risk Students in School                          [ALL] │    │
│ │┌─────────────────────────────────────────────────────────┐  │    │
│ ││ CS22B003 │ Rohan │ AIML │ HIGH │ 6 consec abs │ [VIEW] │  │    │
│ ││ CS22B012 │ Priya │ CSE  │ HIGH │ Marks < 35%  │ [VIEW] │  │    │
│ │└─────────────────────────────────────────────────────────┘  │    │
│ │ Click [VIEW] → Student Profile → SHAP → Recommendations    │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## HOP DASHBOARD — Interaction Map

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEAD OF DEPARTMENT — [AIML Department]                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│ │ Classes  │  │ Students │  │ Subjects │  │ At Risk  │           │
│ │    3     │  │   90     │  │    8     │  │    7     │           │
│ │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │           │
│ │ Classes  │  │ Student  │  │ Subject  │  │ Risk     │           │
│ │ page     │  │ list     │  │ page     │  │ Center   │           │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                     │                            │                  │
│                     ▼                            ▼                  │
│              Click student               Risk Center Page           │
│              → Profile page              ├── Filter: HIGH/MED/LOW   │
│              → SHAP analysis             ├── Click student → Profile│
│                                          ├── Bulk: Assign mentors   │
│                                          └── Export risk report     │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ Class-wise Performance                                       │    │
│ │ [AIML-3A: 76%] [AIML-3B: 71%] [AIML-2A: 82%]             │    │
│ │ Click → Class students → Individual profiles                │    │
│ └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ Teacher Performance Summary                                  │    │
│ │ │ Teacher    │ Subject  │ Avg Score │ Attend% │ [Actions]│   │    │
│ │ │ Prof Kumar │ DS       │ 72%       │ 85%     │ View     │   │    │
│ │ │ Prof Nair  │ OS       │ 58%       │ 71%     │ View     │   │    │
│ │ Click View → Teacher's class details                         │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## MENTOR DASHBOARD — Interaction Map

```
┌─────────────────────────────────────────────────────────────────────┐
│ MENTOR WORKSPACE — Dr. Sharma (15 students assigned)                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│ │ My       │  │ High     │  │ Avg      │  │ Avg      │           │
│ │ Students │  │ Risk     │  │ Attend%  │  │ Score    │           │
│ │   15     │  │    3     │  │  72.4%   │  │  58.2%   │           │
│ │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │           │
│ │ Full list│  │ Watchlist│  │ Attend   │  │ Academic │           │
│ │          │  │ (urgent) │  │ details  │  │ details  │           │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                     │                                              │
│                     ▼                                              │
│         ┌───────────────────────────────────────┐                  │
│         │ WATCHLIST (sorted by severity)        │                  │
│         │                                       │                  │
│         │ 🔴 CS22B003 Rohan — HIGH              │                  │
│         │    Reasons: 6 consecutive absences    │                  │
│         │    [View Profile] [Log Intervention]  │                  │
│         │                                       │                  │
│         │ 🟡 CS22B005 Vikram — MEDIUM           │                  │
│         │    Reasons: Attendance dropped 35%    │                  │
│         │    [View Profile] [Log Intervention]  │                  │
│         └───────────────────┬───────────────────┘                  │
│                             │                                      │
│                             ▼                                      │
│         [View Profile] → Student Profile Page                      │
│           ├── Attendance history (calendar)                        │
│           ├── Score trend (line chart)                             │
│           ├── SHAP explanation (bar chart)                         │
│           ├── Recommendations list                                │
│           └── [Actions]: Log Intervention | Notify HOP | Export   │
│                                                                     │
│         [Log Intervention] → Form:                                 │
│           ├── Type: Counselling | Call | Meeting | Referral        │
│           ├── Notes: free text                                     │
│           ├── Outcome: Improved | No Change | Escalate            │
│           └── Save → Logged in intervention history                │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ Recent Interventions                                         │    │
│ │ │ Student  │ Type       │ Date   │ Outcome  │ [Actions] │   │    │
│ │ │ Rohan    │ Counselling│ Jun 20 │ Pending  │ Edit|View │   │    │
│ │ │ Vikram   │ Call       │ Jun 18 │ Improved │ View      │   │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## TEACHER DASHBOARD — Interaction Map

```
┌─────────────────────────────────────────────────────────────────────┐
│ TEACHER WORKSPACE — Prof. Kumar (DS, OS for AIML-3A, AIML-3B)       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│ │ My       │  │ My       │  │ Attend   │  │ At Risk  │           │
│ │ Classes  │  │ Subjects │  │ Today    │  │ in Class │           │
│ │    2     │  │    3     │  │  25/30   │  │    4     │           │
│ │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │  │ [CLICK]→ │           │
│ │ Class    │  │ Subject  │  │ Today's  │  │ Risk list│           │
│ │ list     │  │ list     │  │ log      │  │ for class│           │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                   │              │                  │
│                                   ▼              ▼                  │
│                         Today's Attendance    At-risk students      │
│                         ├── Present (green)   ├── Click → Profile   │
│                         ├── Absent (red)      └── Actions: Notify   │
│                         ├── Override button                         │
│                         └── Export CSV                              │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ QUICK ACTIONS                                                │    │
│ │ [📸 Mark Attendance] [📝 Enter Marks] [📄 New Assignment]  │    │
│ └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│ [📸 Mark Attendance] →                                             │
│   ├── Select Class → Upload Photo → Face Recognition               │
│   ├── Results: Student identified (green) / Unknown (yellow)       │
│   ├── Confirm → Save attendance records                            │
│   └── Switch to Manual → Checkbox per student                      │
│                                                                     │
│ [📝 Enter Marks] →                                                 │
│   ├── Select Subject → Select Assessment Type                      │
│   ├── Table: Student | Score | Max Score                           │
│   ├── Bulk entry or one-by-one                                     │
│   ├── Save → Risk auto-flags if score drops                        │
│   └── Import CSV button                                            │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ Class Performance Summary                                    │    │
│ │ │ Student    │ Attend% │ Avg Score │ Risk  │ [Actions]  │   │    │
│ │ │ CS22B001   │ 92%     │ 78%       │ LOW   │ Profile    │   │    │
│ │ │ CS22B003   │ 48%     │ 38%       │ HIGH  │ Profile    │   │    │
│ │ Click Profile → Student full detail + SHAP                   │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## STUDENT PROFILE PAGE (Accessible by ALL roles)

```
┌─────────────────────────────────────────────────────────────────────┐
│ STUDENT PROFILE — CS22B003 Rohan Mehta                              │
│ Class: AIML-3A │ Department: AIML │ School: Computing │ Risk: HIGH  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ [Overview] [Attendance] [Academics] [Risk & AI] [Interventions]     │
│                                                                     │
│ ═══ OVERVIEW TAB ═══                                               │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│ │ Attendance │ │ Avg Score  │ │ Risk Level │ │ Consec Abs │       │
│ │   48%      │ │   38%      │ │   HIGH     │ │     6      │       │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘       │
│                                                                     │
│ ═══ ATTENDANCE TAB ═══                                             │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ Calendar Heatmap (green=present, red=absent, gray=no class) │    │
│ │ [Jun 2026]                                                   │    │
│ │ M  T  W  T  F                                               │    │
│ │ 🟢 🟢 🔴 🟢 🔴  ← Week 1                                    │    │
│ │ 🔴 🔴 🔴 🔴 🟢  ← Week 2 (consecutive!)                     │    │
│ └─────────────────────────────────────────────────────────────┘    │
│ Weekly trend chart │ Monthly comparison │ Export CSV                 │
│                                                                     │
│ ═══ ACADEMICS TAB ═══                                              │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ Score Trend Line Chart                                       │    │
│ │ DS: 42 → 38 → 32 (DECLINING ↓)                             │    │
│ │ OS: 55 → 48 → 41 (DECLINING ↓)                             │    │
│ └─────────────────────────────────────────────────────────────┘    │
│ │ Subject    │ Score │ Max │ %   │ Trend │ Teacher      │         │
│ │ Data Struct│ 32    │ 100 │ 32% │  ↓    │ Prof Kumar   │         │
│ │ OS         │ 41    │ 100 │ 41% │  ↓    │ Prof Nair    │         │
│                                                                     │
│ ═══ RISK & AI TAB ═══                                              │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ SHAP Feature Importance                                      │    │
│ │ Overall Attendance ████████████████░░░░ +2.46 (HIGH IMPACT) │    │
│ │ Average Score      █████████░░░░░░░░░░ +1.20               │    │
│ │ Failed Subjects    ███░░░░░░░░░░░░░░░░ +0.17               │    │
│ │ Recent Attendance  ░░░░░░░░░░░░░░░░░░░ -0.09 (helps)       │    │
│ └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│ Reasons:                                                           │
│ • Attendance at 48% — below 75% threshold                          │
│ • Average marks at 38% — below passing threshold                   │
│ • 6 consecutive absences detected                                  │
│                                                                     │
│ Recommendations:                                                   │
│ • Immediate counselling referral required                          │
│ • Notify Head of Department                                        │
│ • Create structured intervention plan                              │
│                                                                     │
│ ═══ INTERVENTIONS TAB ═══ (Mentor/HOP/Admin only)                  │
│ │ Date   │ By        │ Type         │ Notes         │ Outcome │    │
│ │ Jun 20 │ Dr Sharma │ Counselling  │ Family issue  │ Pending │    │
│ │ Jun 15 │ Dr Sharma │ Phone call   │ Not reachable │ No chg  │    │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ ACTIONS:                                                     │    │
│ │ [Export PDF] [Recompute Risk] [Log Intervention] [Notify]   │    │
│ └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Navigation Paths Summary

### From Any Student Name (in any table, any role):
```
Click student → /student/{id} → Full Profile with tabs
```

### From KPI "High Risk" card:
```
Click → Risk filtered list → Click student → Profile → SHAP tab → Recommendations
```

### From Attendance chart:
```
Click bar → Day's records → Click student row → Profile → Attendance tab
```

### From Teacher "Mark Attendance":
```
Upload photo → Face recognition results → Confirm → 
  → If recognized: attendance saved, WebSocket broadcast
  → If unknown: manual override option
  → View today's full log → Click any student → Profile
```

### From Mentor Watchlist:
```
See high-risk student → [View Profile] → SHAP explanation →
  → [Log Intervention] → form → save →
  → Track outcome over time
```

---

## Filter/Sort/Export on Every Data View

| View | Filters | Sort Options | Export |
|---|---|---|---|
| Student list | School, Dept, Class, Risk Level, Status | Name, ID, Attendance%, Score, Risk | CSV, PDF |
| Attendance log | Date, Class, Status | Time, Student, Confidence | CSV |
| Risk center | Level, Department, Class | Score (desc), Name | CSV, PDF |
| Scores view | Subject, Student, Date range | Score, Date, Percentage | CSV |
| Users list | Role, School, Department, Status | Name, Role, Created | CSV |
| Interventions | Student, Type, Outcome, Date | Date, Student, Type | CSV |

---

## Workflow Chains (End-to-End)

### Attendance → Risk → Intervention
```
Teacher marks attendance → Student absence count increases →
  → Risk auto-recomputes (if scheduled) or manual trigger →
  → Student crosses HIGH threshold →
  → Appears on Mentor watchlist + HOP Risk Center →
  → Mentor logs intervention →
  → Tracks outcome
```

### New Student Admission Flow
```
Admin/HOP adds student to system →
  → Auto-assigned to school/dept/class based on ID →
  → Appears in Teacher's class list →
  → HOP assigns mentor →
  → Teacher starts marking attendance →
  → After 2 weeks: risk can be computed
```

### Access Request Flow
```
Teacher needs access to new class →
  → Submits request (type: subject_class, target: AIML-3B) →
  → HOP sees in pending requests →
  → HOP approves →
  → Teacher now sees AIML-3B in their classes →
  → Can mark attendance + enter marks for that class
```
