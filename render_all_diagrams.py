"""
render_all_diagrams.py
----------------------
Renders high-resolution, professional architecture, use case, DFD, and pipeline
diagrams for the VISTA final report using matplotlib (Agg backend).
"""
import os
import shutil
os.environ["MPLCONFIGDIR"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", ".mplconfig")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)

def draw_box(ax, x, y, w, h, text, title="", color="#e2e8f0", edgecolor="#334155", title_color="#1e293b", text_color="#0f172a", fontsize=9, title_fontsize=10, boxstyle="round,pad=0.4"):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=boxstyle, linewidth=1.5, edgecolor=edgecolor, facecolor=color)
    ax.add_patch(rect)
    if title:
        ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=title_fontsize, fontweight="bold", color=title_color)
        ax.text(x + w / 2, y + (h - 0.22) / 2, text, ha="center", va="center", fontsize=fontsize, color=text_color, multialignment="center")
    else:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, fontweight="bold" if fontsize > 9 else "normal", color=text_color, multialignment="center")

def draw_arrow(ax, x1, y1, x2, y2, label="", color="#475569"):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=color, lw=1.5, shrinkA=3, shrinkB=3)
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.1, label, ha="center", va="bottom", fontsize=8, color="#334155", backgroundcolor="white")

# 1. Fig 4.1: High-Level Four-Tier System Architecture
def make_fig_4_1():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # Header
    ax.text(5, 6.7, "Fig 4.1: Four-Tier System Architecture of VISTA", ha="center", va="top", fontsize=12, fontweight="bold", color="#0f172a")

    # Tier 1
    draw_box(ax, 0.5, 5.0, 9.0, 1.3, "React 18 SPA + Vite + Tailwind CSS v4\nAdmin Portal  |  Teacher Portal  |  Student Self-Portal", "Tier 1: Presentation Layer", color="#e0f2fe", edgecolor="#0284c7")

    # Tier 2
    draw_box(ax, 0.5, 3.3, 9.0, 1.4, "FastAPI Gateway (122 Registered Routes / 114 API Endpoints across 14 Modules)\nJWT Authentication  |  Role-Based Access Control (Admin, Teacher, Student)\nInsightFace SCRFD + ArcFace  |  XGBoost Risk Engine + SHAP", "Tier 2: Application & Intelligence Layer", color="#f0fdf4", edgecolor="#16a34a")

    # Tier 3
    draw_box(ax, 0.5, 1.8, 4.3, 1.2, "APScheduler (Midnight Risk Recomputation)\nWebSocket Connection Manager (/ws/dashboard)", "Tier 3A: Asynchronous & Realtime", color="#fef3c7", edgecolor="#d97706")
    draw_box(ax, 5.2, 1.8, 4.3, 1.2, "Redis 7 Cache (In-Memory Fallback)\nPrometheus Metrics Exporter (/metrics)", "Tier 3B: Caching & Observability", color="#fef3c7", edgecolor="#d97706")

    # Tier 4
    draw_box(ax, 0.5, 0.3, 9.0, 1.2, "SQLite 3 (Development) / PostgreSQL 16 (27 Relational Schema Tables)\nONNX Weights (w600k_r50)  |  PyTorch Gallery NPZ  |  Audit Trail Logs", "Tier 4: Persistence & Storage Layer", color="#f1f5f9", edgecolor="#475569")

    # Arrows
    draw_arrow(ax, 5, 5.0, 5, 4.7, "REST / WebSockets")
    draw_arrow(ax, 2.6, 3.3, 2.6, 3.0, "Background Jobs")
    draw_arrow(ax, 7.3, 3.3, 7.3, 3.0, "State Cache / Metrics")
    draw_arrow(ax, 5, 1.8, 5, 1.5, "SQLAlchemy 2.0 ORM")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_4_1_architecture.png"), dpi=300)
    plt.close()

# 2. Fig 4.2: Use Case Diagram for Multi-Role Operations
def make_fig_4_2():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5, 6.7, "Fig 4.2: Use Case Diagram for Multi-Role Operations", ha="center", va="top", fontsize=12, fontweight="bold", color="#0f172a")

    # Actors
    draw_box(ax, 0.4, 4.8, 2.2, 1.2, "Full System Management\nUser Provisioning\nAudit Trail Review", "Administrator", color="#fee2e2", edgecolor="#dc2626")
    draw_box(ax, 0.4, 2.8, 2.2, 1.2, "Attendance Capture\nManual Adjustments\nSubject CIE Marks", "Teacher", color="#dbeafe", edgecolor="#2563eb")
    draw_box(ax, 0.4, 0.8, 2.2, 1.2, "Self-Service Portal\nTranscript & Timetable\nAI Study Coach", "Student", color="#dcfce7", edgecolor="#16a34a")

    # System boundary box
    draw_box(ax, 3.2, 0.5, 6.4, 5.8, "", "VISTA Platform Operational Boundary", color="#ffffff", edgecolor="#64748b", boxstyle="square,pad=0.3")

    # Use cases
    use_cases = [
        (3.6, 5.2, "UC-01: User Authentication & JWT Issuance"),
        (3.6, 4.4, "UC-02: Manage Users, Curricula, & Subject Allocations"),
        (3.6, 3.6, "UC-03: Capture Classroom Group Photo Attendance"),
        (3.6, 2.8, "UC-04: Manual Attendance Override & Audit Trail"),
        (3.6, 2.0, "UC-05: Longitudinal Risk Scoring & SHAP Explanations"),
        (3.6, 1.2, "UC-06: Student Attendance & Performance Self-Check"),
        (6.8, 4.4, "UC-07: Export Transcripts & CSV Reports"),
        (6.8, 2.8, "UC-08: AI Study Coach RAG Interaction"),
        (6.8, 1.2, "UC-09: Live WebSocket Dashboard Broadcasting"),
    ]

    for ux, uy, utext in use_cases:
        rect = patches.FancyBboxPatch((ux, uy), 2.8, 0.6, boxstyle="round,pad=0.2", linewidth=1.2, edgecolor="#0284c7", facecolor="#f0f9ff")
        ax.add_patch(rect)
        ax.text(ux + 1.4, uy + 0.3, utext, ha="center", va="center", fontsize=7.5, color="#0c4a6e", fontweight="bold")

    # Connect actors to use cases
    draw_arrow(ax, 2.6, 5.4, 3.6, 5.5)
    draw_arrow(ax, 2.6, 5.4, 3.6, 4.7)
    draw_arrow(ax, 2.6, 5.4, 6.8, 4.7)

    draw_arrow(ax, 2.6, 3.4, 3.6, 3.9)
    draw_arrow(ax, 2.6, 3.4, 3.6, 3.1)
    draw_arrow(ax, 2.6, 3.4, 6.8, 4.7)

    draw_arrow(ax, 2.6, 1.4, 3.6, 1.5)
    draw_arrow(ax, 2.6, 1.4, 6.8, 3.1)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_4_2_use_cases.png"), dpi=300)
    plt.close()

# 3. Fig 4.3: DFD Level 0 (Context Diagram)
def make_fig_4_3():
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(5, 5.7, "Fig 4.3: Data Flow Diagram (Level 0 — Context Diagram)", ha="center", va="top", fontsize=12, fontweight="bold", color="#0f172a")

    # Process 0
    draw_box(ax, 3.8, 2.0, 2.4, 2.0, "Process 0.0\n\nVISTA Intelligent\nClassroom System", color="#ede9fe", edgecolor="#7c3aed", fontsize=10, boxstyle="circle,pad=0.3")

    # Entities
    draw_box(ax, 0.4, 3.5, 1.8, 1.2, "Administrator", color="#fee2e2", edgecolor="#ef4444")
    draw_box(ax, 0.4, 1.2, 1.8, 1.2, "Teacher", color="#dbeafe", edgecolor="#3b82f6")
    draw_box(ax, 7.8, 2.3, 1.8, 1.4, "Student", color="#dcfce7", edgecolor="#22c55e")

    # Data flows
    draw_arrow(ax, 2.2, 4.3, 3.8, 3.5, "User Config & System Setup")
    draw_arrow(ax, 3.8, 3.2, 2.2, 3.9, "Audit Logs & System Health")

    draw_arrow(ax, 2.2, 2.0, 3.8, 2.6, "Group Photo & Marks Entry")
    draw_arrow(ax, 3.8, 2.2, 2.2, 1.5, "Attendance Roster & Analytics")

    draw_arrow(ax, 6.2, 3.2, 7.8, 3.2, "Attendance & CIE Transcripts")
    draw_arrow(ax, 7.8, 2.7, 6.2, 2.7, "Coach Queries & Self-Requests")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_4_3_dfd_level_0.png"), dpi=300)
    plt.close()

# 4. Fig 4.4: DFD Level 1 (Functional Decomposition)
def make_fig_4_4():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5, 6.7, "Fig 4.4: Data Flow Diagram (Level 1 — Functional Decomposition)", ha="center", va="top", fontsize=12, fontweight="bold", color="#0f172a")

    # 4 Main Processes
    draw_box(ax, 0.8, 4.4, 3.8, 1.4, "1.0 Authentication & RBAC\n(JWT validation, role permission checks)", color="#f0f9ff", edgecolor="#0284c7")
    draw_box(ax, 5.4, 4.4, 3.8, 1.4, "2.0 Biometric Attendance Engine\n(SCRFD detection, ArcFace, Cascade matching)", color="#f0fdf4", edgecolor="#16a34a")
    draw_box(ax, 0.8, 1.8, 3.8, 1.4, "3.0 CIE Academic Policy Engine\n(CIE1/CIE2 assessment rules, eligibility)", color="#fef3c7", edgecolor="#d97706")
    draw_box(ax, 5.4, 1.8, 3.8, 1.4, "4.0 Longitudinal Risk Engine\n(8-feature extraction, XGBoost + SHAP)", color="#fdf2f8", edgecolor="#db2777")

    # Data Stores in center/bottom
    draw_box(ax, 2.8, 0.2, 4.4, 0.9, "D1: Users | D2: Attendance & Gallery | D3: Scores | D4: Risk Flags", "Persistent Relational Data Store (27 Tables)", color="#f8fafc", edgecolor="#475569")

    # Connect
    draw_arrow(ax, 4.6, 5.1, 5.4, 5.1, "Verified Token")
    draw_arrow(ax, 7.3, 4.4, 7.3, 3.2, "Attendance Events")
    draw_arrow(ax, 2.7, 4.4, 2.7, 3.2, "Student Identity")
    draw_arrow(ax, 4.6, 2.5, 5.4, 2.5, "Academic Marks")
    draw_arrow(ax, 5.0, 1.8, 5.0, 1.1, "Read / Write Records")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_4_4_dfd_level_1.png"), dpi=300)
    plt.close()

# 5. Fig 4.5: DFD Level 2 (Face Recognition & Attendance Process)
def make_fig_4_5():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5, 6.7, "Fig 4.5: Data Flow Diagram (Level 2 — Biometric Attendance Pipeline)", ha="center", va="top", fontsize=12, fontweight="bold", color="#0f172a")

    steps = [
        (0.6, 5.2, "2.1 Classroom Photo Ingestion\n(Base64 payload validation)"),
        (3.8, 5.2, "2.2 SCRFD Multi-Face Detection\n(Bounding boxes & landmarks)"),
        (7.0, 5.2, "2.3 Texture Anti-Spoof Filter\n(Laplacian variance test)"),
        (7.0, 3.2, "2.4 ArcFace Embedding\n(512-dim normalized vector)"),
        (3.8, 3.2, "2.5 Gallery Cosine Matcher\n(Threshold tau = 0.55)"),
        (0.6, 3.2, "2.6 ResNet-50 Classifier Fallback\n(Borderline recovery at tau = 0.60)"),
        (0.6, 1.2, "2.7 Database Record Commit\n(Insert present rows in attendance)"),
        (5.4, 1.2, "2.8 WebSocket Event Dispatch\n(Broadcast to active client sessions)"),
    ]

    for sx, sy, stext in steps:
        draw_box(ax, sx, sy, 2.4, 1.2, stext, color="#f8fafc", edgecolor="#0284c7")

    draw_arrow(ax, 3.0, 5.8, 3.8, 5.8)
    draw_arrow(ax, 6.2, 5.8, 7.0, 5.8)
    draw_arrow(ax, 8.2, 5.2, 8.2, 4.4)
    draw_arrow(ax, 7.0, 3.8, 6.2, 3.8)
    draw_arrow(ax, 3.8, 3.8, 3.0, 3.8)
    draw_arrow(ax, 1.8, 3.2, 1.8, 2.4)
    draw_arrow(ax, 3.0, 1.8, 5.4, 1.8, "Confirmed Log")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_4_5_dfd_level_2.png"), dpi=300)
    plt.close()

# 6. Fig 5.1: Multi-Stage Facial Recognition Cascade Pipeline Flow
def make_fig_5_1():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(5, 5.7, "Fig 5.1: Multi-Stage Facial Recognition Cascade Pipeline Flow", ha="center", va="top", fontsize=12, fontweight="bold", color="#0f172a")

    draw_box(ax, 0.5, 4.0, 2.0, 1.1, "Input Face Crop\n(Aligned 112x112)", color="#e0f2fe", edgecolor="#0284c7")
    draw_box(ax, 3.0, 4.0, 2.2, 1.1, "Liveness Filter\n(Laplacian var >= 100)", color="#fef3c7", edgecolor="#d97706")
    draw_box(ax, 5.7, 4.0, 2.2, 1.1, "ArcFace Backbone\n(512-d Embedding)", color="#f0fdf4", edgecolor="#16a34a")
    draw_box(ax, 8.4, 4.0, 1.3, 1.1, "Gallery\nCosine", color="#f0fdf4", edgecolor="#16a34a")

    # Decision diamond / box
    draw_box(ax, 5.7, 2.0, 2.2, 1.2, "Cosine Match >= 0.55?\nYES -> Confirmed\nNO -> Fallback", color="#f8fafc", edgecolor="#64748b")
    draw_box(ax, 1.5, 2.0, 3.0, 1.2, "ResNet-50 Classifier\nConfidence >= 0.60?\nYES -> Recovered Match", color="#ede9fe", edgecolor="#7c3aed")
    draw_box(ax, 3.5, 0.4, 3.0, 1.0, "Result: Enrolled Student ID\n(Mark Present with Source)", color="#dcfce7", edgecolor="#15803d")

    draw_arrow(ax, 2.5, 4.55, 3.0, 4.55)
    draw_arrow(ax, 5.2, 4.55, 5.7, 4.55)
    draw_arrow(ax, 7.9, 4.55, 8.4, 4.55)
    draw_arrow(ax, 9.0, 4.0, 7.9, 2.6)
    draw_arrow(ax, 5.7, 2.6, 4.5, 2.6, "Fallback")
    draw_arrow(ax, 6.8, 2.0, 6.0, 1.4, "Direct Match")
    draw_arrow(ax, 3.0, 2.0, 4.0, 1.4, "Recovered")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_5_1_face_cascade.png"), dpi=300)
    plt.close()

# 7. Fig 5.2: Academic Risk Feature Vector Extraction & Classification Workflow
def make_fig_5_2():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(5, 5.7, "Fig 5.2: Longitudinal Academic Risk Assessment & Attribution Workflow", ha="center", va="top", fontsize=12, fontweight="bold", color="#0f172a")

    draw_box(ax, 0.4, 3.8, 2.4, 1.4, "Historical Records\n- Attendance Logs\n- Assessment Marks\n- Assignments", "Data Inputs", color="#e0f2fe", edgecolor="#0284c7")
    draw_box(ax, 3.3, 3.8, 3.2, 1.4, "8 Temporal Features\n(Overall & recent attendance,\navg marks, trend slope,\nfailed subjects, submissions)", "Feature Engineering", color="#f0fdf4", edgecolor="#16a34a")
    draw_box(ax, 7.0, 3.8, 2.6, 1.4, "3 Critical Overrides\n- Consecutive abs >= 3\n- Overall att < 60%\n- Failed subjects >= 2", "Safety Overrides", color="#fee2e2", edgecolor="#ef4444")

    draw_box(ax, 1.5, 1.4, 3.0, 1.6, "XGBoost Classifier\n3-Class Prediction\n(Low, Medium, High Risk)\nBaseline Acc: 89.0%", "Classification Engine", color="#ede9fe", edgecolor="#7c3aed")
    draw_box(ax, 5.5, 1.4, 3.8, 1.6, "SHAP TreeExplainer\nAttribution Vector\n(+2.986 Attendance Push)\nPrescriptive Interventions", "Explainability (XAI)", color="#fef3c7", edgecolor="#d97706")

    draw_arrow(ax, 2.8, 4.5, 3.3, 4.5)
    draw_arrow(ax, 6.5, 4.5, 7.0, 4.5)
    draw_arrow(ax, 4.9, 3.8, 3.0, 3.0)
    draw_arrow(ax, 8.3, 3.8, 4.0, 3.0, "Overrides")
    draw_arrow(ax, 4.5, 2.2, 5.5, 2.2, "Feature Map")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig_5_2_risk_workflow.png"), dpi=300)
    plt.close()

# Copy existing evaluation figures to figures/ directory
def copy_existing_figures():
    shutil.copyfile("training_results/training_curve_npz_splitB.png", os.path.join(OUTPUT_DIR, "fig_7_1_training_curves.png"))
    shutil.copyfile("training_results/confusion_matrix_npz_splitB.png", os.path.join(OUTPUT_DIR, "fig_7_2_confusion_matrix.png"))
    shutil.copyfile("paper/figures/fig_group_photo_latency.png", os.path.join(OUTPUT_DIR, "fig_7_3_latency_scaling.png"))
    print("Copied evaluation curves, confusion matrix, and latency figures to figures/")

if __name__ == "__main__":
    make_fig_4_1()
    make_fig_4_2()
    make_fig_4_3()
    make_fig_4_4()
    make_fig_4_5()
    make_fig_5_1()
    make_fig_5_2()
    copy_existing_figures()
    print("All diagrams rendered successfully to figures/")
