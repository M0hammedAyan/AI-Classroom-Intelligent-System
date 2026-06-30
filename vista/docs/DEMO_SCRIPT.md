# VISTA Demo Video Script (5 minutes)

## Setup Before Recording

- Backend running on port 8002
- Frontend on port 5173
- Fresh database with seed data (30 timetable slots, 6 subjects, 4 students)
- Dark mode enabled for visual impact
- Browser at 80% zoom for better screen recording

---

## Demo Flow

### 0:00-0:15 — Intro (Title Card)

"VISTA — AI Classroom Intelligent System. Automated attendance + early risk detection."

### 0:15-0:45 — The Problem (Voice-over)

"In Indian engineering colleges, teachers spend 10-15 minutes on roll call every session.
Proxy attendance is rampant. And by the time we identify struggling students, it's too late.
VISTA solves this with AI."

### 0:45-1:30 — Teacher Login + Mark Attendance

1. Login as `kushal@vista.local` (Teacher)
2. Show Teacher Dashboard — subjects, at-risk students, quick actions
3. Click "Mark Attendance"
4. Select class: AIML-4A
5. Upload a classroom photo (use test photo with Saheel + Sujal)
6. Show result: "2 students marked present in 2 seconds"
7. Point out confidence scores

### 1:30-2:00 — Attendance Log

1. Navigate to "Attendance Log"
2. Show today's attendance — present/absent status
3. Point out: "No manual roll call needed. One photo, entire class."

### 2:00-2:45 — Student Dashboard (Switch to Student)

1. Login as `sujal@vista.local` (Student)
2. Show Student Dashboard:
   - Today's timetable (6 periods)
   - Attendance heatmap (last 14 days)
   - KPI cards (attendance %, avg score, risk level)
   - Upcoming assignments
3. Click "My Attendance" — show per-subject breakdown
4. Click "My Subjects" — show all subjects with teacher names
5. Toggle Dark Mode in Settings

### 2:45-3:30 — Risk Detection (Switch to Mentor)

1. Login as `rajeshwari@vista.local` (Mentor)
2. Show Mentor Dashboard — watchlist with HIGH risk students
3. Click on Sujal (HIGH risk) → opens Student Profile
4. Show:
   - Risk level: HIGH
   - SHAP explanation bars (which factors contributed)
   - Attendance is 52%, scores declining
5. Show "Download PDF Report" button
6. Show notification bell — "HIGH Risk: Sujal Agrahari"

### 3:30-4:15 — Admin + Organization Management

1. Login as `admin@vista.local`
2. Show Admin Dashboard:
   - Institution tree (School → Department → Classes → Subjects → Users)
   - Analytics charts (attendance trend, risk donut, subject performance)
3. Click "+ Dept" to show the creation modal
4. Show announcements page — create a notice
5. Show timetable — full weekly schedule

### 4:15-4:45 — Key Differentiators (Voice-over)

"What makes VISTA different:"
- "100% on-premise — no cloud, no APIs, college data never leaves"
- "One photo = entire class marked"
- "Explainable AI — not just 'at risk' but WHY"
- "Built for Indian college hierarchy — 6 roles, scoped access"
- "Zero cost — open source, runs on any laptop"

### 4:45-5:00 — Closing

"VISTA is pilot-ready. We're looking to test with 30 real students for 8 weeks.
The result: a validated system + published research paper."

"Team: Mohammed Ayan, Saheel, Sujal, Aryan — AIML 4th Year, DSATM"

---

## Recording Tips

1. Use OBS Studio (free) for screen recording
2. Record at 1080p, 30fps
3. Use a clean microphone for voice-over (can record separately)
4. Mouse movements should be slow and deliberate
5. Pause 1-2 seconds on each important screen
6. Add subtle background music (lo-fi, very quiet)
7. Export as MP4, H.264, ~50MB target
