# CHAPTER 4: SYSTEM DESIGN

## 4.1 System Architecture
The VISTA system is architected as a modular, four-tier on-premise enterprise platform comprising the **Presentation Tier**, **Application Tier**, **Intelligence Tier**, and **Data Tier**. Figure 4.1 illustrates the architectural hierarchy, inter-module communication protocols, and boundary isolation.

```mermaid
graph TD
    subgraph Presentation_Tier ["Tier 1: Presentation Layer (React 18 + Vite + Tailwind v4)"]
        UI1["Admin Command Center"]
        UI2["Teacher Attendance Console"]
        UI3["Student Self-Service Portal"]
    end

    subgraph Application_Tier ["Tier 2: Application Layer (FastAPI Asynchronous Gateway)"]
        Gateway["REST API Router (122 Registered Routes / 114 API Endpoints across 14 Modules)"]
        AuthService["Auth & RBAC Service (JWT HS256 + Bcrypt)"]
        WSManager["WebSocket Connection Manager (/ws/dashboard)"]
        SchedulerService["Task Scheduler (APScheduler Midnight Cron)"]
        AuditService["Audit Logger & Prometheus Exporter"]
    end

    subgraph Intelligence_Tier ["Tier 3: Intelligence Layer (Vision & ML Engines)"]
        subgraph Vision_Subsystem ["Vision Subsystem"]
            SCRFD["Face Detector (SCRFD ONNX det_10g)"]
            Liveness["Heuristic Liveness Filter (Laplacian >= 20.0)"]
            ArcFace["Feature Extractor (ArcFace R50 512-d)"]
            Matcher["Cosine Gallery Matcher (Threshold = 0.55)"]
            ResNetFallback["Personal Classifier (ResNet-50 PyTorch)"]
            Tracker["Multi-Face Tracker (Greedy IoU Association)"]
        end
        subgraph Risk_Subsystem ["Risk & Analytics Subsystem"]
            FeatureEng["Feature Engineering (8 Longitudinal Metrics)"]
            OverrideEngine["Critical Override Engine (3 Boolean Flags)"]
            XGBoostEngine["XGBoost Risk Classifier (model.pkl)"]
            SHAPExplainer["SHAP TreeExplainer Attribution Engine"]
        end
    end

    subgraph Data_Tier ["Tier 4: Data Layer (PostgreSQL / SQLite + Redis)"]
        DB[(Relational DB: 27 Tables)]
        Cache[(Redis Cache & Token Blocklist)]
    end

    %% Connections
    Presentation_Tier -->|HTTPS REST JSON| Gateway
    Presentation_Tier <-->|WSS Live Stream| WSManager
    Gateway --> AuthService
    Gateway --> AuditService
    Gateway --> Vision_Subsystem
    Gateway --> Risk_Subsystem
    SchedulerService -->|Daily 00:00 Trigger| Risk_Subsystem
    Risk_Subsystem -->|Read/Write Metrics| DB
    Vision_Subsystem -->|Read Embeddings / Write Attendance| DB
    AuthService --> Cache
    Gateway --> DB
```
**Fig 4.1: High-Level Four-Tier System Architecture of VISTA**

### Architectural Tier Descriptions:
1. **Presentation Layer (Tier 1):** Built using React 18, Vite, and Tailwind CSS v4, this tier provides dedicated, role-scoped user workspaces for the three active institutional roles (Admin, Teacher, Student). Components connect to the backend exclusively via an Axios REST client (`src/api/client.js`) and persistent WebSocket streams for live dashboard KPI telemetry.
2. **Application Layer (Tier 2):** Implemented in FastAPI, this tier serves 122 registered routes (114 API endpoints across 14 modules). It enforces JSON Web Token (JWT) cryptographic authentication with role-based access decorators (`permissions.py`), supervises audit logging, exposes Prometheus telemetry, and executes automated midnight batch risk assessments via APScheduler.
3. **Intelligence Layer (Tier 3):** Encapsulates the computer vision and machine learning engines. The vision pipeline coordinates SCRFD detection, heuristic liveness, ArcFace feature extraction, and ResNet-50 classifier fallback. The risk prediction pipeline computes 8 engineered behavioral features and feeds XGBoost decision trees paired with SHAP explainability.
4. **Data Layer (Tier 4):** Anchored by a 27-table relational database schema managed via SQLAlchemy 2.0 ORM (PostgreSQL in production, SQLite in development) alongside an in-memory Redis instance for token blocklisting and session caching.

---

## 4.2 Use Cases and Actor Interactions

### 4.2.1 Actor Roles and Operational Scopes
The platform partitions operations across three primary human actors as defined in Table 4.1.

**Table 4.1: Actor Roles and Scope of Operations**

| Actor | Institutional Scope | Core Responsibilities |
|---|---|---|
| **Admin** | Institution & Department Wide | System-wide control centre; provisions teacher and student accounts; manages class sections and 4th Year AIML curriculum; registers student face prototypes; executes manual attendance and CIE marks entry with audit logging; inspects full cohort risk analytics. |
| **Teacher** | Assigned Classes & Subjects | Captures lecture images via live web camera or image upload; automated SCRFD + ArcFace attendance marking; inspects confidence rates; toggles roster attendance corrections; enters CIE 1 & 2 marks; executes manual entries with mandatory audit reasons. |
| **Student** | Self-Service (Own Record Only) | Strictly read-only portal; views bounded attendance percentage (0–100%); tracks subject-wise attendance across all 5 active courses; inspects CIE 1 and CIE 2 results; drills down into date-wise attendance history with source badges (`Face`, `Manual`, `Seed`). |

### 4.2.2 System Use Case Specifications
Table 4.2 details the primary functional use cases supported by the platform.

**Table 4.2: Use Case Specifications for Primary Operational Workflows**

| Use Case ID | Use Case Name | Primary Actor | Preconditions | Postconditions |
|---|---|---|---|---|
| **UC-01** | User Authentication | Any Registered Actor | Valid institutional email and bcrypt-hashed password exist. | JWT token issued; user redirected to role-scoped dashboard. |
| **UC-02** | Mark Attendance via Photo | Teacher | Teacher assigned to class session; classroom photo captured. | Present records written to DB; attendance summary broadcasted. |
| **UC-03** | Manual Attendance Override | Teacher / Admin | Attendance session exists for specified date and classroom. | Attendance status updated; audit record logged with reason. |
| **UC-04** | Enroll Student Face | Teacher / Admin | Minimum 3 unoccluded facial photographs uploaded. | Normalized 512-dim ArcFace prototype embedding persisted in DB. |
| **UC-05** | View Academic Risk Watchlist| Admin| Daily risk recalculation executed or triggered on-demand. | At-risk student list displayed with severity levels and SHAP drivers. |
| **UC-06** | Log Teacher / Adminship Intervention | Teacher / Admin | Student flagged in risk watchlist; counseling session conducted.| Intervention note, action item, and review date stored in DB. |
| **UC-07** | Export Attendance Report | Teacher / Admin | Attendance session records exist for specified date range. | Formatted CSV or ReportLab PDF report downloaded. |
| **UC-08** | Access Student Self-Portal | Student | Student authenticated with active enrollment status. | Personal attendance stats, timetable, and study materials displayed. |

### 4.2.3 Use Case Diagram
Figure 4.2 models the interactions between the institutional actors and core functional use cases.

```mermaid
graph LR
    subgraph Actors
        A((Admin))
        T((Teacher))
        S((Student))
    end

    subgraph VISTA_Platform ["VISTA Operational Platform"]
        UC1([UC-01: Authenticate & Login])
        UC2([UC-02: Mark Photo Attendance])
        UC3([UC-03: Manual Attendance Override])
        UC4([UC-04: Enroll Student Face])
        UC5([UC-05: View Risk Watchlist & SHAP])
        UC6([UC-06: Log Remedial Intervention])
        UC7([UC-07: Export CSV / PDF Reports])
        UC8([UC-08: View Personal Stats & LMS])
        UC9([UC-09: Institutional Structure CRUD])
    end

    A --> UC1
    A --> UC4
    A --> UC5
    A --> UC6
    A --> UC7
    A --> UC9

    T --> UC1
    T --> UC2
    T --> UC3
    T --> UC4
    T --> UC7

    S --> UC1
    S --> UC8
```
**Fig 4.2: Use Case Diagram for Multi-Role Operations**

### 4.2.4 Detailed Operational Flow for Primary Use Case: UC-02 (Mark Photo Attendance)
1. **Trigger:** Teacher logs into the Teacher Portal and navigates to the "Mark Attendance" console during an active lecture session.
2. **Input:** Teacher selects the class section (e.g., `AIML-4A`), specifies the subject, and captures or uploads an in-class photograph.
3. **Execution Steps:**
   - The React client packages the image file as a `multipart/form-data` payload and transmits a `POST` request to `/api/v1/attendance/mark`.
   - The FastAPI route handler verifies the teacher's JWT bearer token and invokes `vista.vision.recognize.recognize(image_path)`.
   - The SCRFD ONNX model detects all human faces in the image, outputting bounding box coordinates and 5-point facial landmarks.
   - For each detected face, `vista.vision.liveness.check_liveness()` evaluates detection confidence, bounding box width ($\ge 50$ px), and Laplacian texture variance ($\ge 20.0$). Faces failing heuristic liveness are logged with status `liveness_failed`.
   - Faces passing liveness are normalized and passed to ArcFace R50, yielding a 512-dimensional unit vector.
   - The vector is compared against all enrolled class embeddings in memory using cosine similarity. If $\text{sim} \ge 0.55$, the student identity is confirmed.
   - If cosine similarity $< 0.55$, the face crop is passed to the localized PyTorch ResNet-50 classifier (`personal_classifier.py`). If the classifier confidence $\ge 0.60$, the identity is confirmed via the fallback path.
   - If both matching paths fail, the face is logged as unrecognized and discarded without inserting a database record.
   - For all confirmed student identities, the attendance service creates new records in the `attendance` table with status `present`, session date, and timestamp.
   - The endpoint queries the class roster, derives absent students by diffing roster entries against present records, and computes real-time session percentages.
4. **Output:** The API returns a JSON response containing marked count, present student list, and unrecognized face count. The teacher interface updates immediately, and live attendance metrics are broadcasted to connected dashboards via WebSocket (`/ws/dashboard`).

---

## 4.3 Data Flow Diagrams (DFD)

### 4.3.1 DFD Level 0 — Context Diagram
Figure 4.3 depicts the top-level context diagram representing external entity interactions with the unified VISTA boundary.

```mermaid
graph TD
    Teacher[Teacher] -->|1. Classroom Photo, Attendance & Marks| VISTA[VISTA System Boundary]
    Admin[Administrator] -->|2. Org Structure, Curriculum & User Credentials| VISTA
    Student[Student] -->|3. Read-Only Attendance & Marks Queries| VISTA

    VISTA -->|4. Verified Attendance, Recognition & Session Stats| Teacher
    VISTA -->|5. Audit Trails, Roster & System KPI Reports| Admin
    VISTA -->|6. Attendance Overview, Subject Progress & CIE Results| Student
```
**Fig 4.3: Data Flow Diagram (Level 0 — Context Diagram)**

### 4.3.2 DFD Level 1 — Functional Decomposition
Figure 4.4 illustrates the Level 1 functional decomposition, detailing the data flow across the primary subsystems: Authentication, Vision Attendance, Academics/LMS, Risk Engine, and Reporting.

```mermaid
graph TD
    User([User / Client]) -->|Login Credentials| P1[1.0 Authenticate & RBAC]
    P1 -->|JWT Token| User
    P1 -->|Verify Token| P2[2.0 Facial Attendance Marking]
    P1 -->|Verify Token| P3[3.0 Academic Records & LMS]
    P1 -->|Verify Token| P4[4.0 Academic Risk Engine]
    P1 -->|Verify Token| P5[5.0 Report & Export Service]

    Teacher([Teacher]) -->|Classroom Photo| P2
    P2 -->|Query Enrolled Vectors| D1[(D1: Students & Embeddings)]
    P2 -->|Store Present/Absent Logs| D2[(D2: Attendance Records)]
    P2 -->|Emit Event| WS([WebSocket Broadcast])

    Teacher -->|Assessment Marks & Syllabi| P3
    P3 -->|Store Marks & Coursework| D3[(D3: Academic Scores & LMS)]

    APScheduler([APScheduler / Trigger]) -->|Midnight Batch Job| P4
    P4 -->|Fetch Attendance History| D2
    P4 -->|Fetch Score Trajectories| D3
    P4 -->|Store Risk Scores & Drivers| D4[(D4: Risk Flags & Interventions)]
    P4 -->|Queue Critical Absence Notice| D5[(D5: Parent Alerts)]

    Admin([Admin]) -->|Query Watchlist| P4
    Admin -->|Log Intervention Action| D4

    User -->|Request CSV / PDF| P5
    P5 -->|Read Records| D2
    P5 -->|Read Risk Data| D4
    P5 -->|Generate File| User
```
**Fig 4.4: Data Flow Diagram (Level 1 — Functional Decomposition)**

### 4.3.3 DFD Level 2 — Facial Recognition & Attendance Processing
Figure 4.5 details the inner data transformations of Process 2.0 (Facial Attendance Marking Subsystem).

```mermaid
graph TD
    Photo[Uploaded Classroom Photo] --> P2_1[2.1 SCRFD Face Localization]
    P2_1 -->|Bounding Boxes & 5 Landmarks| P2_2[2.2 Heuristic Liveness Verification]
    
    P2_2 -->|Texture Var < 20.0 or Box < 50px| P2_2_Fail[2.2.1 Log Liveness Failed]
    P2_2_Fail --> D2[(D2: Attendance DB)]
    
    P2_2 -->|Liveness Passed: 112x112 Crop| P2_3[2.3 ArcFace R50 Feature Extraction]
    P2_3 -->|512-d Unit Embedding| P2_4[2.4 Cosine Gallery Matching]
    D1[(D1: Student Face Embeddings)] -->|Enrolled Prototypes| P2_4
    
    P2_4 -->|Cosine Sim >= 0.55| P2_6[2.6 Resolve Student Identity]
    P2_4 -->|Cosine Sim < 0.55| P2_5[2.5 ResNet-50 Fallback Classifier]
    
    P2_5 -->|Softmax Conf >= 0.60| P2_6
    P2_5 -->|Softmax Conf < 0.60| P2_7[2.7 Discard Unrecognized Face]
    
    P2_6 -->|Confirmed Student ID| P2_8[2.8 Deduplicate & Session Diff]
    D1 -->|Class Roster| P2_8
    P2_8 -->|Write Present / Absent Records| D2
    P2_8 -->|JSON Result & Metrics| Client[Client Dashboard]
```
**Fig 4.5: Data Flow Diagram (Level 2 — Facial Recognition & Attendance Process)**
