# Document 6 — Literature Review

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 6 (Literature Review)

**IMPORTANT DISCLAIMER:** This literature review is based on (1) papers already cited in the project's own bibliography (`paper/references.bib`) — these are confirmed to exist and correctly attributed in the repo, and (2) papers from my training knowledge that I am confident exist. All training-knowledge citations are marked **[FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]**. No DOI numbers, author names, or paper titles are fabricated. If I am not confident a paper exists, I say so explicitly. Researchers MUST verify every citation against the original source before including it in any manuscript.

---

## Topic 1: Face Recognition Attendance Systems (InsightFace/ArcFace in Educational Contexts)

### Cited in the project (confirmed in `paper/references.bib`):

**ArcFace — Deng et al. (2019)** [VERIFIED in repo bibliography]
- Title: "ArcFace: Additive Angular Margin Loss for Deep Face Recognition"
- Venue: CVPR 2019, pp. 4690-4699
- DOI: 10.1109/CVPR.2019.00482
- Summary: Introduces additive angular margin loss for deep face recognition, enforcing geodesic angular margins on hyperspherical manifolds for intra-class compactness and inter-class discrepancy. Produces 512-dimensional L2-normalized embeddings.
- How it compares to VISTA: VISTA uses ArcFace R50 (`w600k_r50.onnx`) via InsightFace as its primary embedding model. This is standard usage — ArcFace is the state-of-the-art backbone for face recognition.
- What VISTA adds: VISTA adds a ResNet-50 fallback classifier as a second stage when ArcFace cosine matching falls below threshold. This is a cascade architecture, not a modification of ArcFace itself. [VERIFIED — `vista/vision/embed.py`, `vista/vision/recognize.py`]

**SCRFD — Guo et al. (2022)** [VERIFIED in repo bibliography]
- Title: "Sample and Computation Redistribution for Efficient Face Detection"
- Venue: ICLR 2022
- Summary: Addresses efficient face detection through sample and computation redistribution across training data and model layers. Achieves superior scale-invariant multi-face localization.
- How it compares to VISTA: VISTA uses SCRFD (`det_10g.onnx`) via InsightFace for face detection. This is standard usage.
- What VISTA adds: VISTA deploys SCRFD on CPU-only infrastructure (no GPU), which is a deployment-level contribution, not an algorithmic one. [VERIFIED — `vista/vision/detect.py`]

**ResNet — He et al. (2016)** [VERIFIED in repo bibliography]
- Title: "Deep Residual Learning for Image Recognition"
- Venue: CVPR 2016, pp. 770-778
- DOI: 10.1109/CVPR.2016.90
- Summary: Introduces residual connections for training very deep networks, enabling 50+ layer architectures. ResNet-50 is one of the most widely used image classification backbones.
- How it compares to VISTA: VISTA uses ImageNet-pretrained ResNet-50 as the fallback classifier, fine-tuned on 20 student identities. This is standard transfer learning, not a novel architecture.
- What VISTA adds: The two-stage cascade (ArcFace cosine → ResNet-50 fallback) is the architectural contribution, not the ResNet-50 itself. [VERIFIED — `vista/vision/personal_classifier.py`]

### Additional papers from training knowledge:

**InsightFace — Guo et al. (2021)** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Likely title: "InsightFace: 2D and 3D Face Analysis Toolkit"
- Likely venue: arXiv preprint (open-source toolkit)
- Note: InsightFace is the open-source toolkit that packages SCRFD and ArcFace models. VISTA uses this toolkit (`buffalo_l` model pack) but it is not explicitly cited in the paper. Should be cited for completeness. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- What VISTA adds: Nothing algorithmic over InsightFace; VISTA is a downstream application.

**FaceNet — Schroff et al. (2015)** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Likely title: "FaceNet: A Unified Embedding for Face Recognition and Clustering"
- Likely venue: CVPR 2015
- Summary: Introduces triplet loss for face embedding learning. Predecessor to ArcFace in the embedding-based recognition paradigm.
- Relevance: The paper mentions FaceNet in its related work. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]

**MTCNN — Zhang et al. (2016)** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Likely title: "Joint Face Detection and Alignment Using Multitask Cascaded Networks"
- Likely venue: IEEE Signal Processing Letters, 2016
- Summary: Earlier face detection method using cascaded CNNs. The paper mentions MTCNN as an earlier approach superseded by SCRFD.
- Relevance: Historical context for face detection evolution. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]

### Research gaps VISTA addresses in this topic:
- On-premise deployment of SCRFD+ArcFace on commodity CPU (no cloud, no GPU) for classroom use. [VERIFIED — `detect.py` uses CPUExecutionProvider]
- Cascade fallback to recover marginal cosine rejections. [VERIFIED — ablation shows FRR 16.83%→1.98%]
- **Gaps NOT addressed:** Open-set impostor rejection, demographic fairness, large-scale evaluation (>20 students).

---

## Topic 2: Academic Early-Warning / At-Risk Prediction Systems

### Cited in the project (confirmed in `paper/references.bib`):

**Gardner & Brooks (2018)** [VERIFIED in repo bibliography]
- Title: "Student Success Prediction in Higher Education: A Systematic Literature Review"
- Venue: Journal of Educational Data Mining, vol. 10, no. 2, pp. 1-31, 2018
- Summary: Systematic review of student success prediction in higher education. Establishes that early identification of at-risk students improves retention.
- How it compares to VISTA: VISTA's risk engine addresses this gap by providing automated risk scoring. However, VISTA's risk model (XGBoost on synthetic data) does not use real longitudinal data.
- What VISTA adds: Integration of risk scoring with attendance data (face recognition) and explainability (SHAP). [DOCUMENTED ONLY — paper framing]

**XGBoost — Chen & Guestrin (2016)** [VERIFIED in repo bibliography]
- Title: "XGBoost: A Scalable Tree Boosting System"
- Venue: KDD 2016, pp. 785-794
- DOI: 10.1145/2939672.2945397
- Summary: Scalable gradient boosting system that dominates tabular prediction tasks.
- How it compares to VISTA: VISTA uses XGBoost as an auxiliary risk model. Standard usage, not novel.
- What VISTA adds: Architectural separation — deterministic rule engine for production decisions, XGBoost for SHAP diagnostics only. [VERIFIED — `risk_engine.py`, `risk.py` route]

**Barata et al. (2023)** [VERIFIED in repo bibliography]
- Title: "Predicting and Explaining Student Performance in Higher Education Using Explainable Machine Learning"
- Venue: IEEE Transactions on Learning Technologies, vol. 16, no. 6, pp. 912-925, 2023
- DOI: 10.1109/TLT.2023.3278910
- Summary: Demonstrates that decomposing predictions into localized feature attributions enables academic advisors to tailor remedial roadmaps. Uses explainable ML for student performance prediction.
- How it compares to VISTA: VISTA uses a similar XGBoost+SHAP approach for explainability. Barata et al. use real data; VISTA uses synthetic data.
- What VISTA adds: The architectural separation of deterministic rules (production) from ML diagnostics (SHAP) is a design choice, though not fundamentally novel. [VERIFIED — `explainer.py`]

### Additional papers from training knowledge:

**UCI Student Performance Dataset — Cortez & Silva (2008)** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Likely title: "Using Data Mining to Predict Secondary School Student Performance"
- Likely venue: Proceedings of 5th Future Business Technology Conference, 2008
- Note: This is the dataset referenced by `vista/ml/validate_uci.py`. It is Portuguese secondary school data, not Indian college data — a contextual mismatch the audit noted. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]

**Learning Analytics and Knowledge (LAK) conference proceedings** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Note: The Society for Learning Analytics Research (SoLAR) publishes LAK annually. Many at-risk prediction papers appear here. Specific papers should be verified before citing. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]

### Research gaps VISTA addresses in this topic:
- Integration of risk scoring with automated attendance data (face recognition). [VERIFIED — risk engine consumes attendance records]
- SHAP-based explainability for risk predictions. [VERIFIED — `explainer.py`]
- **Gaps NOT addressed:** No real longitudinal data; XGBoost below majority baseline; no cross-validation; synthetic circular labels.

---

## Topic 3: Explainable AI in Educational Analytics

### Cited in the project (confirmed in `paper/references.bib`):

**SHAP — Lundberg & Lee (2017)** [VERIFIED in repo bibliography]
- Title: "A Unified Approach to Interpreting Model Predictions"
- Venue: NeurIPS 2017, vol. 30, pp. 4765-4774
- Summary: Introduces SHapley Additive exPlanations, a unified framework for interpreting model predictions using game-theoretic Shapley values.
- How it compares to VISTA: VISTA uses SHAP TreeExplainer for XGBoost risk model explanations. Standard usage.
- What VISTA adds: The integration of SHAP into a live educational platform with a dedicated `/risk/explain` endpoint is an engineering integration, not a research contribution over SHAP itself. [VERIFIED — `explainer.py`]

### Research gaps VISTA addresses in this topic:
- Providing per-prediction feature attributions for educational risk decisions. [VERIFIED — `explainer.py:explain_prediction()`]
- **Gaps NOT addressed:** No user study on whether SHAP explanations actually help teachers; no comparison of explanation quality against alternative XAI methods.

---

## Topic 4: Integrated Intelligent Classroom Platforms

### Cited in the project:
No specific integrated classroom platform papers are cited in `paper/references.bib`. The paper's related work does not reference specific integrated systems for comparison. [DOCUMENTED ONLY — this is a gap in the paper's literature review]

### From training knowledge:

The literature on integrated classroom platforms spans several sub-areas. Key themes include: [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]

- **Automated attendance systems** using various biometric modalities (fingerprint, iris, face). Many conference papers exist but specific citations require verification.
- **Learning Management Systems (LMS)** like Moodle, Canvas, Blackboard — these are commercial systems, not research papers.
- **Smart classroom** or **intelligent classroom** research — typically IoT-focused, combining sensors, displays, and analytics.

**Assessment:** The paper's related work section does not cite any specific integrated classroom platform for direct comparison. This is a literature review gap — without comparing to specific deployed systems, the "fragmented pipeline" limitation claim (paper Section I) is unsupported by evidence. [DOCUMENTED ONLY]

### Research gaps VISTA addresses in this topic:
- Integration of face recognition + risk scoring + AI coaching + CIE policy into a single platform. [VERIFIED — all components implemented and functional]
- **Gaps NOT addressed:** No comparison to any specific integrated system; no deployment-scale evaluation; no multi-institution testing.

---

## Topic 5: Privacy and Ethics of Biometric Systems in Education

### Cited in the project (confirmed in `paper/references.bib`):

**DPDP Act 2023** [VERIFIED in repo bibliography]
- Title: "The Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023)"
- Source: Ministry of Law and Justice, Government of India, Gazette of India, August 2023
- URL: https://www.meity.gov.in/content/digital-personal-data-protection-act-2023
- Summary: India's data protection law requiring consent for personal data processing, data minimization, and individual rights.
- How it relates to VISTA: The paper claims DPDP Act compliance through consent capture and data minimization. However, the consent form has placeholder fields and no signed records are in the repo. [DOCUMENTED ONLY — compliance is claimed but not verified]

### Additional considerations from training knowledge:

**GDPR (EU) and biometric data** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Biometric data is classified as "special category" personal data under GDPR Article 9, requiring explicit consent and lawful basis. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Relevance: If VISTA is used in any EU context, GDPR compliance would be required. The paper does not address GDPR.

**FERPA (US) and student records** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- The Family Educational Rights and Privacy Act (FERPA) governs student educational records in the US. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Relevance: Not applicable to Indian deployment but relevant for international scope.

**Face recognition bias and fairness** [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING]
- Multiple studies (e.g., Buolamwini & Gebru, "Gender Shades," 2018, FAT* conference) have shown that face recognition systems exhibit demographic biases, particularly across gender and skin tone. [FROM TRAINING KNOWLEDGE — VERIFY BEFORE CITING — verify exact citation]
- Relevance: VISTA's paper explicitly acknowledges that "demographic and skin tone fairness evaluations were not conducted" (Section VIII). This is a critical ethical gap. [VERIFIED — `PAPER.md` Section VIII]

### Research gaps VISTA addresses in this topic:
- On-premise processing (no raw face data sent to cloud for recognition). [VERIFIED — `detect.py` runs locally]
- PII stripping before LLM calls (only numerical aggregates sent). [VERIFIED — `coach_service.py`]
- **Gaps NOT addressed:** No encryption at rest (SQLite plaintext); consent form has placeholders; no signed consent records; no IRB/ethics committee approval documented; no demographic fairness evaluation; no data retention policy enforcement.

---

## Research Gaps VISTA Addresses (Consolidated)

| Gap | How VISTA Addresses It | Evidence | Quality of Address |
|-----|----------------------|---------|-------------------|
| Fragmented attendance + risk + advising pipelines | Single integrated platform | [VERIFIED] | Engineering integration, not research novelty |
| High FRR in classroom face recognition | Two-stage cascade fallback | [VERIFIED — ablation] | Strongest contribution |
| Opaque risk diagnostics | SHAP explainability | [VERIFIED — `explainer.py`] | Standard technique applied |
| LLM hallucination in advising | Deterministic computation firewall | [VERIFIED — `coach_service.py`] | Practical pattern, narrow evaluation |
| On-premise compute (no cloud for vision) | CPU-only ONNX inference | [VERIFIED] | Deployment-level, not algorithmic |

## Research Gaps VISTA Does NOT Address

| Unaddressed Gap | Evidence | Impact |
|----------------|---------|--------|
| Open-set impostor rejection | [VERIFIED — no impostor test set] | Critical for security claims |
| Demographic bias/fairness | [VERIFIED — paper acknowledges] | Critical for biometric ethics |
| Real longitudinal risk data | [VERIFIED — synthetic only] | Critical for risk model validity |
| Multi-institution evaluation | [VERIFIED — 1 classroom, 20 students] | Limits generalizability |
| Comparison to specific deployed systems | [DOCUMENTED ONLY] | Weakens "existing systems" claims |
| Data encryption at rest | [VERIFIED — SQLite plaintext] | Privacy concern |
| Formal ethics approval | [UNVERIFIED — consent form has placeholders] | Publication blocker |

---

## Novelty Assessment: What Is Genuinely New vs. Engineering Integration

### Genuinely New (with caveats)

1. **Two-stage cascade for classroom attendance (MODERATE novelty):** The specific architecture of using ArcFace cosine matching as a first-stage filter with a personally-trained ResNet-50 classifier as a second-stage fallback, validated by ablation (FRR 16.83%→1.98%), is a legitimate architectural contribution. However: (a) cascade architectures are not new in face recognition generally, (b) the ablation generator is missing, and (c) it is closed-set only. [PARTIALLY VERIFIED]

2. **Deterministic computation firewall for LLM coaching (LOW-MODERATE novelty):** Pre-computing all arithmetic facts in deterministic code and injecting only numerical aggregates into the LLM prompt is a practical design pattern. This is related to but distinct from RAG — it uses deterministic computation rather than retrieval. The 10/10 groundedness result is promising but narrow. [PARTIALLY VERIFIED]

### Engineering Integration (NOT research novelty)

1. Using SCRFD + ArcFace (standard InsightFace usage). [VERIFIED]
2. Fine-tuning ResNet-50 (standard transfer learning). [VERIFIED]
3. Using XGBoost for tabular prediction (standard EDM practice). [VERIFIED]
4. Using SHAP for explainability (standard XAI practice). [VERIFIED]
5. Building a FastAPI + React web platform (standard software engineering). [VERIFIED]
6. Implementing CIE policy rules (domain-specific engineering). [VERIFIED]

### Indefensible Novelty Claims That Must Be Removed

1. **"Novel" vision pipeline** — SCRFD + ArcFace is standard InsightFace. Do not claim the vision pipeline itself is novel. [VERIFIED — off-the-shelf usage]
2. **"Novel" risk model** — XGBoost for student risk is standard EDM practice, and the model performs below baseline. Do not claim the risk model is a novel ML contribution. [VERIFIED — below majority baseline]
3. **"Novel" explainability approach** — SHAP TreeExplainer is standard. Do not claim SHAP integration as a research contribution. [VERIFIED — standard technique]
4. **Any claim of superior performance over published baselines** — no comparison to any published system exists in the repo. [VERIFIED — no comparative evaluation]
5. **"Novel" LLM coaching** — the deterministic firewall is a practical pattern, but RAG and grounding approaches are well-established. Do not claim this as fundamentally new. [DOCUMENTED ONLY — related work acknowledges RAG]

---

*End of Document 6 — Literature Review*
