# VISTA: An Integrated AI Platform for Face Recognition-Based Attendance and Explainable Academic Risk Prediction

## IEEE Conference Paper Draft

**Target:** IEEE CONECCT 2026 / IEEE ICCCNT / Springer LNNS (ICDSA)
**Format:** 6 pages, double-column, IEEE conference template

---

## TITLE

**VISTA: An Integrated AI Platform for Face Recognition-Based Attendance and Explainable Academic Risk Prediction in Higher Education**

---

## AUTHORS

Mohammed Ayan¹, Saheel Pradhan¹, Sujal Agrahari¹, Aryan Raj Singh¹

¹ Department of Artificial Intelligence and Machine Learning,
Dayananda Sagar Academy of Technology and Management, Bangalore, India

---

## ABSTRACT (250 words)

Manual attendance systems in Indian higher education institutions are time-consuming, error-prone, and provide no analytical insights into student academic performance. While existing solutions address either attendance automation or student analytics independently, no integrated platform combines both with explainable AI capabilities.

This paper presents VISTA (Visual Intelligence System for Tracking and Analysis), a novel AI-powered academic intelligence platform that integrates automated face recognition-based attendance with explainable student risk prediction. The system employs ArcFace R50 for face embedding extraction with cosine similarity matching, achieving 100% recognition accuracy on a 14-sample test set with 0% false accept rate at a 0.55 similarity threshold. For academic risk prediction, a rule-based scoring engine augmented with XGBoost classification (macro F1 = 0.957) identifies students as LOW, MEDIUM, or HIGH risk based on eight engineered features derived from attendance and academic performance data.

A key contribution is the integration of SHAP (SHapley Additive exPlanations) TreeExplainer to provide per-prediction explanations, generating human-readable reasons such as "Attendance at 48% — below recommended level" rather than opaque model outputs. The platform implements a hierarchical role-based access control system supporting five user roles (Admin, HOS, HOP, Mentor, Teacher) mapped to Indian collegiate administrative structures.

Experimental evaluation on real student photographs demonstrates the system's viability for pilot deployment. The platform is designed for on-premise deployment with zero recurring costs, addressing affordability constraints in Indian higher education.

**Keywords:** Face Recognition, ArcFace, Academic Risk Prediction, Explainable AI, SHAP, Attendance Automation, Higher Education, XGBoost

---

## I. INTRODUCTION

### A. Problem Statement

Indian higher education institutions face three fundamental challenges: (1) manual attendance marking consumes approximately 10 minutes per session across 45,000+ colleges, (2) at-risk students are identified only after academic failure rather than proactively, and (3) existing commercial solutions either address attendance (Truein, FaceIT) or analytics (EAB Navigate, Civitas Learning) but not both, with costs ranging from $50K-$500K annually—prohibitive for Indian colleges.

### B. Motivation

The predictive analytics in EdTech market is projected to grow from USD 680M (2024) to USD 5.9B (2034) at a CAGR of 24.1%. However, no commercially available platform combines face recognition attendance with explainable academic risk prediction in a single, affordable, on-premise system designed for Indian collegiate structures.

### C. Contributions

This paper makes the following contributions:

1. **Integrated architecture** — A unified platform combining face detection (SCRFD), recognition (ArcFace R50), and academic risk prediction with a shared data pipeline.

2. **Explainable risk scoring** — SHAP-based per-prediction explanations that convert model outputs into actionable insights for non-technical educators.

3. **Indian academic hierarchy support** — A role-based system (School → Department → Class) with five user roles matching Indian collegiate administrative structures.

4. **Zero-cost deployment model** — On-premise architecture requiring no cloud subscription or per-student licensing.

### D. Paper Organization

Section II reviews related work. Section III describes system architecture. Section IV details the face recognition pipeline. Section V presents the risk prediction engine. Section VI reports experimental results. Section VII discusses limitations and future work. Section VIII concludes.

---

## II. RELATED WORK

### A. Face Recognition for Attendance

Deng et al. [1] introduced ArcFace (Additive Angular Margin Loss) achieving 99.83% accuracy on LFW. InsightFace [2] provides a production toolkit implementing SCRFD detection and ArcFace recognition. Recent systems [3,4] demonstrate face recognition attendance in educational settings but lack integration with academic analytics.

### B. Student Risk Prediction

XGBoost [5] has demonstrated strong performance on tabular educational data. Recent work [6,7] applies SHAP for explainability in student dropout prediction. However, these systems rely on manually-entered attendance data rather than automated collection.

### C. Multi-Object Tracking

ByteTrack [8] achieves 80.3 MOTA on MOT17 using IoU-based association with Kalman filtering. While primarily designed for pedestrian tracking, the approach is applicable to multi-face classroom scenarios.

### D. Gap in Literature

No existing system integrates: (1) automated face recognition attendance, (2) ML-based risk prediction, and (3) per-prediction explainability in a single platform. VISTA addresses this gap.

---

## III. SYSTEM ARCHITECTURE

### A. Overview

VISTA follows a four-layer architecture:
- **Vision Layer:** SCRFD detection → ArcFace R50 embedding → cosine similarity matching → liveness check
- **Application Layer:** FastAPI REST API (60 endpoints), JWT authentication, WebSocket real-time updates
- **Intelligence Layer:** 8-feature engineering pipeline → rule-based scoring + XGBoost → SHAP explanations
- **Presentation Layer:** React SPA with role-specific dashboards

### B. Data Flow

1. Classroom image captured
2. SCRFD detects face bounding boxes
3. ArcFace R50 extracts 512-dimensional embedding
4. Cosine similarity computed against enrolled student gallery
5. If similarity ≥ 0.55: identity confirmed → attendance recorded
6. Periodically: risk engine computes features from attendance + scores
7. SHAP generates per-student explanations
8. Dashboard displays results with drill-down to individual profiles

### C. Database Schema

16 tables including: students, attendance, scores, risk_flags, schools, departments, class_sections, users (5 roles), mentor_assignments, teacher_subjects, interventions, audit_logs.

---

## IV. FACE RECOGNITION PIPELINE

### A. Detection

SCRFD (Sample and Computation Redistribution for Face Detection) is used for face localization. Operating on 640×640 input, it produces bounding boxes with 5-point facial landmarks.

### B. Embedding Extraction

ArcFace with ResNet-50 backbone (trained on MS1MV2, 5.8M images, 85K identities) generates 512-dimensional L2-normalized embeddings. The angular margin loss is:

L = -log(e^(s·cos(θ_yi + m)) / (e^(s·cos(θ_yi + m)) + Σe^(s·cos(θ_j))))

### C. Matching Strategy

For a gallery of N enrolled students, the probe embedding is compared against all stored embeddings using cosine similarity:

sim(a, b) = (a · b) / (||a|| · ||b||)

A threshold of 0.55 was determined empirically. For N = 30 students, brute-force comparison is O(N) and completes in <1ms.

### D. Enrollment Protocol

3-5 images per student are captured, embeddings extracted, and averaged (with re-normalization) to produce a single reference embedding per student.

### E. Anti-Spoofing

Heuristic-based liveness checking validates: (1) detection confidence > 0.5, (2) face width > 50px, (3) Laplacian texture variance > 20.

---

## V. RISK PREDICTION ENGINE

### A. Feature Engineering

Eight features are computed per student over a configurable observation window:

| # | Feature | Formula |
|---|---|---|
| 1 | Attendance % | sessions_attended / total_sessions × 100 |
| 2 | Attendance drop % | first_half_rate - second_half_rate |
| 3 | Marks average | mean(score_i / max_i × 100) |
| 4 | Marks decline % | (peak - latest) / peak × 100 |
| 5 | Assignment completion | submitted / total × 100 |
| 6 | Consecutive absences | longest absent streak |
| 7 | Performance trend | direction over last 3 assessments |
| 8 | Engagement score | 0.6 × attendance + 0.4 × completion |

### B. Scoring

Weighted sum with override rules:

risk_score = Σ(w_i × component_i), where Σw_i = 1.0

Classification: 0-39 → LOW, 40-69 → MEDIUM, 70-100 → HIGH

Override rules force HIGH on: consecutive_absences ≥ 7, attendance < 50%, marks_avg < 35%.

### C. XGBoost Model

100 trees, max_depth=4, learning_rate=0.1. Trained on 200 samples (synthetic, rule-consistent labels). Macro F1 = 0.957.

### D. SHAP Explainability

TreeExplainer computes per-feature Shapley values for each prediction:

φ_i(f, x) = Σ (|S|!(M-|S|-1)!) / M! × [f(S ∪ {i}) - f(S)]

Converted to human-readable reasons: features with |SHAP| > 0.01 and values below/above thresholds generate natural language explanations.

---

## VI. EXPERIMENTAL RESULTS

### A. Face Recognition

| Metric | Value |
|---|---|
| Test subjects | 2 enrolled + 4 unknown |
| Enrollment images | 5 per subject |
| Test images | 14 total (10 enrolled + 4 unknown) |
| True Positive Rate | 100% (10/10) |
| False Accept Rate | 0% (0/4) |
| Average confidence | 82.1% |
| Lowest correct match | 70.9% |
| Inference time (CPU) | ~800ms per image |

### B. Risk Prediction

| Model | Accuracy | Macro F1 | Precision | Recall |
|---|---|---|---|---|
| Logistic Regression | 93% | 0.94 | 0.94 | 0.94 |
| XGBoost | 95% | 0.957 | 0.96 | 0.96 |
| Rule-based | — | — | — | — |

### C. System Performance

| Metric | Value |
|---|---|
| API endpoints | 60 |
| Automated tests | 44 (31 API + 7 ML + 6 vision) |
| Frontend pages | 15 |
| User roles | 6 (admin, HOS, HOP, mentor, teacher, student) |
| p50 response latency | <15ms (non-vision) |
| Vision inference | ~800ms (CPU, no GPU) |

---

## VII. LIMITATIONS AND FUTURE WORK

### A. Limitations

1. XGBoost trained on synthetic data — real-world F1 requires outcome labels from completed semesters.
2. Face recognition tested on 2 subjects — larger-scale validation needed.
3. Single-image liveness check — not robust against sophisticated spoofing.
4. CPU inference (~800ms) — GPU would reduce to <100ms.

### B. Future Work

1. **Pilot deployment** at DSATM with 30 students for one semester.
2. **Real outcome validation** — train on actual pass/fail labels.
3. **Video stream** — ByteTrack-based multi-frame tracking.
4. **Temporal modeling** — LSTM on weekly feature sequences.
5. **Federated learning** — cross-institution model improvement.
6. **Causal inference** — measure intervention effectiveness.

---

## VIII. CONCLUSION

VISTA demonstrates the feasibility of integrating face recognition attendance with explainable academic risk prediction in a single platform. With 100% recognition accuracy on tested subjects and SHAP-powered explanations, the system provides actionable intelligence to educators. The on-premise, zero-cost deployment model addresses the affordability gap in Indian higher education. Future pilot deployment will validate real-world performance at scale.

---

## REFERENCES

[1] J. Deng, J. Guo, N. Xue, and S. Zafeiriou, "ArcFace: Additive Angular Margin Loss for Deep Face Recognition," in CVPR, 2019.

[2] J. Guo, J. Deng, A. Lattas, and S. Zafeiriou, "Sample and Computation Redistribution for Efficient Face Detection," in ICLR, 2022.

[3] S. Ramya et al., "AI-Powered Attendance Monitoring System for Educational Institutions," in IJRASET, 2025.

[4] Springer, "Advanced Student Attendance System Using Deep Learning-Based Face Recognition," LNNS, 2025.

[5] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," in KDD, 2016.

[6] S. M. Lundberg and S. I. Lee, "A Unified Approach to Interpreting Model Predictions," in NeurIPS, 2017.

[7] "Student Dropout Prediction Using Ensemble Learning with SHAP-Based Explainable AI Analysis," JSSPA, 2025.

[8] Y. Zhang et al., "ByteTrack: Multi-Object Tracking by Associating Every Detection Box," in ECCV, 2022.

---

## FORMATTING NOTES

- Use IEEE conference template (double-column, 10pt)
- 6 pages maximum
- Include system architecture diagram (Fig. 1)
- Include SHAP waterfall plot example (Fig. 2)
- Include recognition accuracy table (Table I)
- Include risk prediction comparison table (Table II)
- Submit via EDAS or CMT (per conference)
