# VISTA Research Paper: Action Checklist, Reviewer Q&A & Proposed Experiments (`PAPER_TODO.md`)

This document serves as the research completion guide, submission audit checklist, and viva defense companion for the IEEE conference paper:
**"VISTA: An Integrated On-Premise Vision and Explainable Risk-Scoring Platform for Classroom Academics"** (Authors: Mohammed Ayan, Saheel Pradhan, Aryan Raj Singh, Sujal Agrahari, and Dr. Ajayprakash B V).

---

## 1. Ten Hardest Reviewer / Viva Examiner Questions (Reviewer Q&A)

### Q1: "Your risk prediction model achieves only 50.0% accuracy, which is lower than the majority-class baseline of 53.5%. Why include machine learning at all if a trivial dummy classifier performs better?"
**Honest Grounded Answer:**  
"That is an accurate observation, and we explicitly highlight this in Section VI-E and Table IV. The XGBoost model was trained on a synthetic dataset (`student_data.csv`, $N=1000$) where labels were generated using deterministic threshold rules mirroring `risk_engine.py`. This resulted in severe class imbalance ($107\text{ HIGH}, 81\text{ MEDIUM}, 12\text{ LOW}$ in test). The unweighted model completely failed to predict the minority class ($\text{LOW } F_1 = 0.00$).  
Critically, in the deployed VISTA architecture, **the XGBoost model does not decide student risk**. Mission-critical operational risk assignment is decided by a deterministic, auditable rule engine (`calculate_risk_from_metrics`). The role of the machine learning pipeline is strictly exploratory: it serves an auxiliary diagnostic endpoint (`/api/v1/students/{id}/risk/explain`) to compute local SHAP feature attributions, demonstrating how tree explainability can be plumbed into educational workflows once authentic multi-year longitudinal data is collected."

---

### Q2: "Your face recognition test set has only 20 enrolled gallery classes and 202 unaugmented test crops, plus one live test with 7 students. Isn't this far too small to claim enterprise readiness?"
**Honest Grounded Answer:**  
"Yes. We explicitly list this as Limitation 1 and 2 in Section VIII. VISTA was deployed as an institutional pilot within the Department of Artificial Intelligence and Machine Learning at Dr. Ambedkar Institute of Technology. The 20-student gallery reflects a single classroom cohort. While 202 unaugmented crops evaluated with 95% Wilson confidence intervals establish the statistical validity of the ResNet-50 cascade over cosine-only matching ($92.57\%$ vs $77.72\%$), real-world university deployment across multiple lecture halls requires evaluating open-set impostors, diverse ethnic demographics, and varied room illumination."

---

### Q3: "Did you test open-set rejection? How does your two-stage cascade behave when an un-enrolled stranger or student from another department sits in the classroom?"
**Honest Grounded Answer:**  
"In our current offline evaluation (`facial_pipeline_results.npz`), all test samples belong to the 20 enrolled classes (closed-set evaluation). In production, an unknown student will trigger the fallback if ArcFace cosine is $< 0.55$; however, because the PyTorch ResNet-50 head uses a closed-set 20-way Softmax, if the stranger's crop produces a maximum softmax probability $\ge 0.60$, the system will generate a false acceptance. While the combined condition ($s < 0.55 \land \max(\mathbf{p}) \ge 0.60$) provides a heuristic hurdle, formal open-set testing with an explicit background impostor set is an essential future experiment (outlined in Section 4 below)."

---

### Q4: "You claim 90.10% accuracy for the ResNet-50 classifier. Did data augmentation cause data leakage between your training and test sets?"
**Honest Grounded Answer:**  
"No, data leakage was prevented by design. In `train_from_npz.py` (lines 207–268), the dataset was partitioned on unique `(usn, source_image)` pairs *before* generating augmented variants. All 30 Albumentations variants per face were assigned strictly to the training partition. Validation and test partitions strictly contained clean, unaugmented original crops ($\text{aug\_idx}=0$). Runtime assertions (`assert_no_leakage`, lines 271–296) verify that training, validation, and test index sets are mutually disjoint."

---

### Q5: "Is your face liveness detection actually secure against spoofing attacks?"
**Honest Grounded Answer:**  
"No, not against determined adversaries. As stated in Section IV-A and Limitation 4, our liveness module uses heuristic Eye Aspect Ratio (EAR) blink detection and Laplacian variance blur thresholds. While this filters out low-resolution static photo prints or blurred screens, it is vulnerable to high-definition video replays, curved screen projections, or silicone presentation attacks. Robust deployment requires deep infrared texture analysis or active challenge-response protocols."

---

### Q6: "Why do you use both ArcFace cosine matching and a ResNet-50 classifier? Doesn't ArcFace already provide optimal hyperspherical separation?"
**Honest Grounded Answer:**  
"ArcFace provides strong metric embeddings ($512$-d), but setting a strict cosine threshold ($\tau=0.55$) to ensure low False Accept Rate ($5.45\%$) in uncontrolled classroom lighting causes severe False Rejection ($16.83\%$ FRR, rejecting 34 of 202 true students). In Table II, we prove empirically that the fine-tuned ResNet-50 classifier acts as a specialized local recovery mechanism: it recaptures 30 of those 34 rejected students based on fine-grained spatial features, slashing FRR to $1.98\%$ without increasing false acceptances."

---

### Q7: "You claim VISTA is privacy-preserving and on-premise, yet your AI Study Coach sends data to OpenRouter. How is that on-premise?"
**Honest Grounded Answer:**  
"We delineate the exact privacy boundary in Section IX and Claims Table C-32/C-33:
1. **Vision Biometrics:** 100% on-premise. No classroom video streams, face crops, or embedding vectors ever leave the institutional server.
2. **AI Study Coach:** Operates with strict PII stripping. When `LLM_USE_API=true`, only anonymous numerical aggregates (e.g., 'attendance: 78.2%, missable: 9') are transmitted to OpenRouter. Student names, USNs, and emails are stripped by `coach_service.py`. Furthermore, setting `LLM_USE_OLLAMA=true` routes queries to a local Ollama instance, keeping 100% of telemetry on-premise."

---

### Q8: "Why does the paper describe the attendance audit trail as relational provenance rather than an immutable cryptographic ledger?"
**Honest Grounded Answer:**  
"Because honesty requires stating the implementation as it exists. VISTA uses an append-only relational table (`audit_logs`) and a non-nullable `source` column (`'face'`, `'manual'`, `'seed'`) enforced by database constraints and route validation. There are no cryptographic hashes, Merkle trees, or distributed consensus mechanisms. Calling this a 'blockchain' or 'cryptographic ledger' would be scientifically false; it is an auditable relational provenance framework."

---

### Q9: "In your live pilot on October 30, 2026, the lowest student recognition confidence was 58%. Isn't that dangerously close to your 55% threshold?"
**Honest Grounded Answer:**  
"Yes. Student Vignesh V was matched with 58% confidence, just 3 percentage points above the $\tau=0.55$ threshold. Inspection revealed that this student was seated at the rear corner of the classroom under severe ceiling light drop-off and exhibited an oblique yaw angle ($>25^\circ$). This live edge case validates why the secondary ResNet-50 fallback is necessary: had illumination dropped further, cosine matching would have failed, requiring the cascade to maintain recognition."

---

### Q10: "Can students prompt-inject the AI Study Coach to change their marks or approve attendance exemptions?"
**Honest Grounded Answer:**  
"No, because of the architectural decoupling. The AI Study Coach is strictly a read-only presentation client. It has no write database privileges, no access to database ORM update sessions, and no tool-calling endpoints that modify attendance or score tables. Furthermore, mathematical facts are computed deterministically prior to prompt formatting; even if a student convinces the LLM to output 'Your attendance is 100%', the underlying database and official portal remain unchanged."

---

## 2. Bibliographic Verification & References Status

| Citation Key | Status | Verification Source | Venue / Year | Notes |
|---|---|---|---|---|
| `deng2019arcface` | **Verified** | IEEE CVPR 2019, pp. 4690–4699 | CVPR 2019 | Seminal ArcFace loss paper. |
| `guo2022sample` | **Verified** | ICLR 2022 / arXiv:2105.04714 | ICLR 2022 | SCRFD detection framework. |
| `he2016deep` | **Verified** | IEEE CVPR 2016, pp. 770–778 | CVPR 2016 | ResNet-50 residual architecture. |
| `chen2016xgboost` | **Verified** | ACM SIGKDD 2016, pp. 785–794 | KDD 2016 | XGBoost tree boosting. |
| `lundberg2017unified` | **Verified** | NeurIPS 2017, pp. 4765–4774 | NeurIPS 2017 | SHAP framework. |
| `barata2023predicting` | **Verified** | IEEE TLT, vol. 16, no. 6, pp. 912–925 | IEEE TLT 2023 | Explainable ML in higher education. |
| `gardner2018student` | **Verified** | JEDM, vol. 10, no. 2, pp. 1–31 | JEDM 2018 | Systematic review on student success. |
| `lee2024exploring` | **Verified** | ACM LAK 2024, pp. 312–324 | ACM LAK 2024 | LLM advising fidelity. |
| `dpdpact2023` | **Verified** | Gazette of India, Act No. 22 of 2023 | Ministry of Law & Justice, Aug 2023 | India DPDP Act. |

*Excluded Phantom Citations:*  
- Removed `Wang, Shan, Dai, Face Liveness Detection Using Texture and Morphological Operations, IEEE TIFS 2017` (unverified / non-existent citation).

---

## 3. LaTeX Compilation & Figure Export Instructions

### A. How to Compile `paper/PAPER.tex`
When LaTeX is installed on your machine or on Overleaf:
```bash
cd paper
pdflatex PAPER.tex
bibtex PAPER
pdflatex PAPER.tex
pdflatex PAPER.tex
```

### B. Generated Figure Artifacts in `paper/figures/`
- [x] `fig_threshold_sweep.png` & `fig_threshold_sweep.pdf` (ArcFace threshold sweep, FAR/FRR trade-off)
- [x] `fig_cascade_ablation.png` & `fig_cascade_ablation.pdf` (Cosine vs Cascade ablation with 95% Wilson CIs)
- [x] `fig_group_photo_latency.png` & `fig_group_photo_latency.pdf` (Multi-face scaling latency from 1 to 45 faces)
- [x] `architecture.mmd` (Mermaid source for complete 4-tier platform architecture)
- [x] `cascade_flow.mmd` (Mermaid source for two-stage decision cascade)

---

## 4. Proposed Experiments to Strengthen Future Submissions

The following four experiments are fully formulated with prepared methodology:

### Experiment 1: Multi-Condition Open-Set Face Benchmark ($N \ge 50$)
- **Objective:** Evaluate open-set impostor rejection and illumination invariance.
- **Protocol:**
  - Enroll 30 students in the gallery.
  - Collect 10 un-enrolled students (impostors) seated among enrolled students.
  - Test under 3 environmental conditions: Natural Morning Light, Overhead Fluorescent Light, and Dim Curtained Projector Mode.
  - Measure False Discovery Rate (FDR) and Open-Set Identification Rate (DIR) at $\text{FAR} = 1\%$.

### Experiment 2: Demographically Disaggregated Fairness Audit
- **Objective:** Evaluate facial recognition performance across demographic subgroups to detect algorithmic bias.
- **Protocol:**
  - Categorize test crops across Fitzpatrick skin phototypes (I–VI) and gender.
  - Compute Equalized Odds and Disparate Impact across ArcFace and ResNet-50 stages.
  - Ensure ethical consent is captured in strict compliance with Section 4 of India's DPDP Act, 2023.

### Experiment 3: Authentic Longitudinal Risk Model Training
- **Objective:** Replace synthetic labels with authentic university degree progression records.
- **Protocol:**
  - Ingest 3 years of historical departmental academic records ($N \ge 1500$ students).
  - Train cost-sensitive XGBoost with `scale_pos_weight` to address class imbalance.
  - Benchmark against Logistic Regression, Random Forest, and LightGBM using 5-fold stratified cross-validation.

### Experiment 4: Human-AI Advising Usability Survey
- **Objective:** Measure student and teacher acceptance of the automated notification center and AI Study Coach.
- **Protocol:**
  - Deploy VISTA across a 6-week academic module for 60 students and 4 faculty members.
  - Administer System Usability Scale (SUS) surveys evaluating trust, perceived workload reduction, and cognitive clarity of SHAP explanations.

---

## 5. Target Venues & Submission Checklist

### Recommended Venues
1. **IEEE International Conference on Advanced Learning Technologies (ICALT)**
   - *Fit:* Strong track on AI in educational technology, Learning Analytics, and classroom systems.
2. **IEEE Frontiers in Education Conference (FIE)**
   - *Fit:* Engineering education research, curricular monitoring, and retention technologies.
3. **ACM Conference on Learning Analytics and Knowledge (LAK) — Short Paper Track**
   - *Fit:* Empirical evaluation of student risk modeling and advising systems.
4. **IEEE Region 10 Conference (TENCON) / IEEE INDICON**
   - *Fit:* Applied computer vision and institutional software engineering in India/Asia-Pacific.

### Final Submission Checklist
- [x] Title reflects reality: *"On-Premise Vision"* used instead of *"Edge-Vision"*.
- [x] All numbers verified against `CLAIMS_TABLE.md` and `evaluation/results/`.
- [x] Exact operating points reported: precision, recall, FAR, and FRR with 95% Wilson confidence intervals.
- [x] XGBoost risk model reported with majority-class baseline (50.0% vs 53.5%) and synthetic data caveat.
- [x] Data leakage prevention code lines documented (`train_from_npz.py:207–296`).
- [x] No phantom references; all 9 citations verified with publishers/DOIs.
- [x] Complete Ethics and Privacy section addressing India DPDP Act 2023, data minimization, and telemetry boundaries.
