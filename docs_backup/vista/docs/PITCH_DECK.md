# VISTA — Pitch Deck (10 Slides)

> For presenting to college management (HOP/HOS/Principal)

---

## Slide 1: Title

**VISTA — AI Classroom Intelligent System**

*Automated attendance + Early risk detection = Better student outcomes*

Team: Mohammed Ayan, Saheel Pradhan, Sujal Agrahari, Aryan Raj Singh
DSATM | School of CSE | AIML Department

---

## Slide 2: The Problem

**Every semester, students fail — and we find out too late.**

- Manual roll call: 10-15 min/session wasted, proxy attendance rampant
- At-risk students identified only AFTER failing exams
- Mentors have 20+ students but NO visibility into who needs help NOW
- Attendance + Marks + Risk are in 3 different systems (or paper registers)

*Current process is reactive. We need proactive intervention.*

---

## Slide 3: Our Solution

**VISTA: One system that connects Attendance → Academics → Risk → Action**

1. **Camera sees who's in class** — one photo marks entire class (face recognition)
2. **AI tracks patterns** — attendance drops, score declines, consecutive absences
3. **System warns mentors** — before it's too late
4. **Everyone sees their data** — Student, Teacher, Mentor, HOP, HOS

*No external APIs. No cloud. Everything runs on a college server.*

---

## Slide 4: How It Works (Demo)

**Live Demo Flow:**

1. Teacher uploads classroom photo → 4 students marked in 2 seconds
2. Dashboard shows real-time attendance
3. Student with <60% attendance flagged MEDIUM risk
4. Student with <50% + declining scores flagged HIGH risk
5. Mentor gets notification → opens student profile → sees SHAP explanation
6. Mentor logs intervention (counselling session)

*100% accuracy on face recognition (tested on real photos)*

---

## Slide 5: Technology

| What | How |
|------|-----|
| Face Detection | InsightFace SCRFD (state-of-the-art) |
| Face Recognition | ArcFace R50 — 512-dim embeddings, cosine matching |
| Risk Prediction | XGBoost ML + Rule Engine (9 features) |
| Explainability | SHAP — shows WHY a student is at risk |
| Backend | FastAPI + PostgreSQL (85+ API endpoints) |
| Frontend | React (responsive, dark/light mode) |
| Deployment | Docker — runs on any Linux server |

*All open-source. No license fees. No vendor lock-in.*

---

## Slide 6: For College Management

**What VISTA gives you that you don't have today:**

- Real-time attendance without manual roll call (saves 1500+ hours/year)
- Early warning system before students fail (not after)
- Parent alerts when attendance drops below 75%
- NAAC-ready attendance + academic reports
- One dashboard for HOS/HOP to see entire school/department

**What it costs:** A laptop + USB camera per classroom. No recurring fees.

---

## Slide 7: The Ask (Pilot Proposal)

**We're requesting permission for an 8-week pilot:**

- Target: AIML 4th Year A (30 students, 1 classroom)
- Duration: 8 weeks (daily attendance marking)
- Hardware: 1 laptop + 1 USB camera (we provide)
- Teacher involved: Kushal (already trained)
- Mentor involved: Rajeshwari (already trained)

**Deliverable:** Real accuracy numbers + research paper + time-saved report

---

## Slide 8: What We'll Measure

| Metric | Target |
|--------|--------|
| Face recognition accuracy (30 students) | ≥ 95% |
| Risk prediction vs actual outcomes | F1 ≥ 0.75 |
| Time saved per attendance session | 80% reduction |
| Teacher satisfaction | ≥ 4/5 |
| False accept rate | < 2% |

*Results will be published in an IEEE/Springer conference paper.*

---

## Slide 9: Timeline

| Week | Action |
|------|--------|
| 1 | Enroll 30 students (3-5 photos each) |
| 2 | Start daily attendance (teacher + camera) |
| 3-6 | Daily operation + data collection |
| 7-8 | Validation, comparison with manual records |
| +2 weeks | Results report + paper draft |

---

## Slide 10: Team & Next Steps

**Team:**
- Mohammed Ayan — Tech Lead, ML, Architecture
- Saheel Pradhan — Face Recognition, Camera Setup
- Sujal Agrahari — Backend, Database, Pilot Data
- Aryan Raj Singh — Frontend, UX, User Training

**Next steps (if approved):**
1. Get student consent forms signed
2. Enroll 30 students
3. Start pilot
4. Publish paper with DSATM as institutional affiliation

**Contact:** mohammed.ayan@dsatm.edu / +91 XXXXXXXXXX
