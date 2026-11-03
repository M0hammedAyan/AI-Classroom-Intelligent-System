# Document 9 — Questions Requiring Human Input

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 7 (Questions Requiring Human Input)

This document lists ALL questions that cannot be answered from repository evidence alone. Each question is organized by category, with an explanation of why it cannot be answered from the repo and why it matters for publication.

---

## Category 1: Author and Affiliation Information

### Q1.1: Who is the official faculty advisor/guide?

- **Why it cannot be answered from the repo:** The consent form (`vista/docs/CONSENT_FORM.md`) lists "Faculty Advisor: [Guide Name]" as an unfilled placeholder. The paper (`paper/PAPER.md`) lists "Ajayprakash B. V." as the second author with role "Associate Professor and Head of Programme," but the consent form does not name him. [UNVERIFIED — placeholder in consent form]
- **Why it matters:** Publications require correct advisor attribution. The consent form must name the supervising faculty for ethical compliance. If the advisor is Ajayprakash B. V., this should be confirmed and the consent form updated.

### Q1.2: What is the correct institution name and email domain?

- **Why it cannot be answered from the repo:** The inventory states "Dr. Ambedkar Institute of Technology, Bengaluru (DSATM)" but the consent form says "Dayananda Sagar Academy of Technology & Management (DSATM), Bangalore" with email `mohammed.ayan@dsatm.edu`. The paper uses `@dr-ait.org` email domain. These are different institutions or different names for the same institution. [CONTRADICTED — `audit-inventory.md` vs `CONSENT_FORM.md` vs `PAPER.md`]
- **Why it matters:** Incorrect institutional affiliation in a published paper is a serious error. The correct name, abbreviation, and email domain must be confirmed.

### Q1.3: What are the team member roles and contributions?

- **Why it cannot be answered from the repo:** The inventory lists 5 team members but does not specify who did what. No CRediT (Contributor Roles Taxonomy) statement exists. [DOCUMENTED ONLY — no contribution statement in repo]
- **Why it matters:** IEEE requires author contribution statements. Each author's role (conceptualization, methodology, software, validation, writing, etc.) must be specified.

---

## Category 2: Institutional Ethics Approval Status

### Q2.1: Has an Institutional Review Board (IRB) or ethics committee approved this study?

- **Why it cannot be answered from the repo:** The consent form states "This study has been reviewed by [Department/Faculty Committee Name] and approved for conduct within DSATM campus" — but the committee name is an unfilled placeholder. No IRB approval letter, reference number, or approval date exists in the repository. [UNVERIFIED — placeholder text, no approval document]
- **Why it matters:** This is a **publication blocker**. IEEE and all reputable venues require documented ethics approval for research involving human biometric data. Without it, the paper cannot be submitted.

### Q2.2: Was a Data Protection Impact Assessment (DPIA) conducted?

- **Why it cannot be answered from the repo:** No DPIA document exists in the repository. The paper claims DPDP Act 2023 compliance but provides no evidence of a formal assessment. [UNVERIFIED — no DPIA document]
- **Why it matters:** Biometric data processing is high-risk under data protection law. A DPIA is typically required for such processing. Its absence weakens the compliance claim.

### Q2.3: What is the ethics approval reference number and date?

- **Why it cannot be answered from the repo:** No reference number or date is documented anywhere in the repository. [UNVERIFIED]
- **Why it matters:** Publications require the ethics approval reference number and date for verification.

---

## Category 3: Informed Consent for Biometric Data Collection

### Q3.1: Have all 20 enrolled students signed consent forms?

- **Why it cannot be answered from the repo:** No signed consent forms exist in the repository. The consent form template exists (`vista/docs/CONSENT_FORM.md`) but no filled/signed copies. [UNVERIFIED — no signed records]
- **Why it matters:** Without signed consent, using students' biometric data in research is ethically problematic and potentially unlawful. This is a **publication blocker**.

### Q3.2: Are any of the 20 students minors (under 18)?

- **Why it cannot be answered from the repo:** The consent form includes a "Parent/Guardian Signature (if under 18)" field, but no records indicate whether any students are minors. Student USNs suggest they are college students (likely adults), but this cannot be confirmed from the repo. [UNVERIFIED — no age information]
- **Why it matters:** If any student is a minor, parental consent is legally required. Even if all are adults, this must be confirmed.

### Q3.3: Were students informed that their data would be used in a research publication?

- **Why it cannot be answered from the repo:** The consent form mentions "pilot study" and "attendance system" but does not explicitly mention publication or research paper submission. [UNVERIFIED — consent form does not mention publication]
- **Why it matters:** Participants should be informed if their data will appear in published research. Many ethics committees require this.

### Q3.4: Were students informed about 30x augmentation of their face images?

- **Why it cannot be answered from the repo:** The consent form says "3-5 facial photographs" are collected for "face embedding creation." It does not mention that each photo will be augmented 30 times (horizontal flip, color jitter, rotation, noise) to create ~20,400 training samples. [UNVERIFIED — not mentioned in consent form]
- **Why it matters:** Data augmentation changes the scope of biometric data processing beyond what was consented.

### Q3.5: Were students informed about LLM coaching and data sent to external services?

- **Why it cannot be answered from the repo:** The consent form covers face data collection only. It does not mention the AI study coach, LLM interaction, or that aggregated academic numbers are sent to OpenRouter when `LLM_USE_API=true`. [UNVERIFIED — not covered in consent form]
- **Why it matters:** Sending student academic data (even without PII) to an external LLM service requires separate consent.

---

## Category 4: Dataset Licensing and Provenance

### Q4.1: Under what license are the face images shared?

- **Why it cannot be answered from the repo:** No LICENSE file exists in `dataset/`, `agumented data/`, or `data/processed/`. The face images are real biometric data of actual students, making licensing a critical question. [UNVERIFIED — no license files]
- **Why it matters:** If the dataset is shared publicly (e.g., as a supplementary material or GitHub release), a license is required. Biometric data sharing may also require additional legal review.

### Q4.2: Were the InsightFace ONNX models used under their correct license?

- **Why it cannot be answered from the repo:** The InsightFace models (`det_10g.onnx`, `w600k_r50.onnx`) are downloaded at runtime, not stored in the repo. Their license (Apache 2.0 for InsightFace) is not documented or verified in the repository. [UNVERIFIED — not documented in repo]
- **Why it matters:** Using third-party models without verifying their license terms is a compliance risk.

### Q4.3: Is the UCI Student Performance dataset available for use, and has it been properly cited?

- **Why it cannot be answered from the repo:** The UCI dataset is referenced by `vista/ml/validate_uci.py` but is not included in the repo. No citation for the UCI dataset exists in `references.bib`. [DOCUMENTED ONLY — referenced in code but not cited]
- **Why it matters:** If the UCI dataset is used for validation, it must be properly cited in the paper.

### Q4.4: Can the synthetic `student_data.csv` be shared publicly?

- **Why it cannot be answered from the repo:** The synthetic data is generated by `generate_sample_data.py` but no license or sharing policy is documented. [UNVERIFIED — no license]
- **Why it matters:** Synthetic data sharing for reproducibility requires a clear license.

---

## Category 5: Unpublished Experiments

### Q5.1: Are there offline experiment results not committed to the repository?

- **Why it cannot be answered from the repo:** The repository contains 5 evaluation result JSONs, 4 training result logs, and various documentation. However, the test-fix-plan mentions prior test runs (`test_baseline.txt`, `baseline_test_run.txt`) that may contain additional results. It is unknown whether other experiments were conducted offline (e.g., the cascade ablation generator was run but the script was never committed). [UNVERIFIED — cannot confirm whether all experiments are in the repo]
- **Why it matters:** Missing experiment scripts (like the cascade ablation generator) suggest some experiments were run but their code was not committed. This affects reproducibility claims.

### Q5.2: What model was used for the coach groundedness evaluation?

- **Why it cannot be answered from the repo:** The `coach_groundedness.json` records `nvidia/nemotron-3.5-super-vl:free` but this model name is unusual. Was this the actual model, or is the JSON artifact using a test/placeholder name? The default in `coach_service.py` is `google/gemini-2.0-flash-001`. [PARTIALLY VERIFIED — artifact says `nemotron` but default is `gemini`; unclear which was actually used]
- **Why it matters:** The model used affects reproducibility of the coach groundedness result. The paper should state the exact model used.

### Q5.3: Were there any failed experiments that are not documented?

- **Why it cannot be answered from the repo:** The repo shows successful experiments and honestly documents failures (XGBoost below baseline). However, there may have been other experiments (e.g., different ResNet architectures, different augmentation strategies, different risk features) that were attempted but not documented. [UNVERIFIED — cannot confirm completeness]
- **Why it matters:** Undocumented failed experiments may contain useful insights. More importantly, selective reporting (only publishing successes) is a research integrity concern.

### Q5.4: What was the live classroom pilot result data?

- **Why it cannot be answered from the repo:** The paper mentions a live classroom pilot (October 30, 2026, 7 students, group photo) but no per-image results, confidence scores, or ground-truth verification data are saved in the repository. [DOCUMENTED ONLY — mentioned in paper but no data artifacts]
- **Why it matters:** Without saved data, the live pilot claim cannot be verified or audited.

---

## Category 6: Target Publication Venue

### Q6.1: What is the target publication venue and deadline?

- **Why it cannot be answered from the repo:** `NEEDS_YOUR_INPUT.md` asks "Which venue should we submit to?" and `PAPER_TODO.md` discusses venue options, but no final decision is documented. [DOCUMENTED ONLY — venue not decided]
- **Why it matters:** The target venue determines formatting requirements, page limits, submission deadlines, and the level of rigor expected. This affects the revision strategy.

### Q6.2: Is this for a course project, conference paper, or journal paper?

- **Why it cannot be answered from the repo:** The project has elements of all three (academic report chapters `REPORT_ch1-7.md`, a paper draft `paper/PAPER.md`, exhibition materials `EXHIBITION_KIT.md`). The intended output is unclear. [DOCUMENTED ONLY — multiple document types suggest multiple purposes]
- **Why it matters:** A course project has different requirements than a peer-reviewed publication. The level of experimental rigor, ethics documentation, and literature review depth varies by venue type.

---

## Category 7: Co-Author Contributions and Roles

### Q7.1: What did each team member contribute?

- **Why it cannot be answered from the repo:** No CRediT statement or contribution description exists. The 5 team members are listed in the inventory and paper, but their individual roles are not documented. [UNVERIFIED — no contribution statement]
- **Why it matters:** IEEE requires author contribution statements. Ghost/gift authorship (listing people who did not contribute) is an integrity violation.

### Q7.2: Is Ajayprakash B. V. a co-author or supervisor?

- **Why it cannot be answered from the repo:** The paper lists him as the second author with "Associate Professor and Head of Programme" title, suggesting a supervisory role. But whether he contributed to the research (making him a co-author) or merely supervised (which may warrant acknowledgment rather than authorship) is unclear. [DOCUMENTED ONLY — listed as author but role unclear]
- **Why it matters:** Authorship vs. acknowledgment distinction is an integrity matter. IEEE has specific guidelines on this.

---

## Category 8: Real-World Deployment Status and User Counts

### Q8.1: How many students are actually enrolled in the system?

- **Why it cannot be answered from the repo:** The `dataset/` directory has 20 student folders. The `vista_dev.db` database may contain seeded demo data. The README mentions "21 students" (stale). The actual live deployment enrollment count is not documented. [PARTIALLY VERIFIED — 20 in dataset, unknown in live DB]
- **Why it matters:** The actual number of enrolled users affects scale claims. If the system is deployed with only 20 students, scale claims should be appropriately limited.

### Q8.2: Is the system deployed in production or only in development/pilot?

- **Why it cannot be answered from the repo:** The repo contains development databases, test databases, and a consent form for a "pilot study." Backend logs (`backend-live.log`, `backend-8003.log`) suggest live runs. But no production deployment documentation exists. [PARTIALLY VERIFIED — logs suggest live runs, no deployment docs]
- **Why it matters:** Production deployment claims require evidence (uptime, user counts, usage logs). Pilot claims are more modest and appropriate for the current evidence.

### Q8.3: How many real attendance records have been marked via face recognition?

- **Why it cannot be answered from the repo:** The database contains seeded demo data (`source='seed'`) and potentially real face-marked attendance (`source='face'`). The actual count of face-marked attendance records is not documented. [UNVERIFIED — not documented]
- **Why it matters:** The number of real attendance records validates the system's operational use. If most records are seeded demo data, the system's operational claims are weaker.

### Q8.4: Has the parent alert system ever been used in production?

- **Why it cannot be answered from the repo:** The `parent_alerts` table exists but the delivery mechanism (email/SMS) is not implemented in code. `NEEDS_YOUR_INPUT.md` asks "How are parent alerts delivered?" [UNVERIFIED — delivery mechanism unclear]
- **Why it matters:** If the parent alert system is claimed as a feature, its delivery mechanism must be functional. If it's just a database table with no delivery, it should not be claimed as implemented.

---

## Category 9: Other Unanswerable Questions

### Q9.1: What is the actual GPU vs CPU inference performance difference?

- **Why it cannot be answered from the repo:** All inference is CPU-only (`CPUExecutionProvider`). No GPU benchmarks exist. The paper claims "CPU-optimized" but provides no GPU comparison. [VERIFIED — CPU only, no GPU comparison]
- **Why it matters:** The "on-premise CPU" framing is a strength, but without a GPU comparison, the performance trade-off cannot be quantified.

### Q9.2: What are the actual demographics of the 20 enrolled students?

- **Why it cannot be answered from the repo:** No demographic data (age, gender, skin tone, ethnicity) is stored in the repository. The USNs suggest they are AI&ML department students at an Indian engineering college, but no demographic breakdown exists. [UNVERIFIED — no demographic data]
- **Why it matters:** Without demographic data, fairness/bias claims cannot be made or refuted. This is critical for biometric systems.

### Q9.3: What was the resolution of the "21st student" (1DA22AI010)?

- **Why it cannot be answered from the repo:** The `image_count_report.txt` lists 21 students including `1DA22AI010`, but the current `dataset/` has only 20 (this student's folder is absent). Whether this student withdrew, was removed, or was never enrolled is unknown. [CONTRADICTED — stale report vs current directory]
- **Why it matters:** Understanding why a student was removed helps understand data provenance and potential consent issues.

### Q9.4: What are the actual OpenRouter API costs for the coach service?

- **Why it cannot be answered from the repo:** No cost data exists in the repo. The coach uses a free model (`nvidia/nemotron-3.5-super-vl:free`) for evaluation, but production usage costs are not documented. [UNVERIFIED — no cost data]
- **Why it matters:** If the system is deployed at scale, LLM API costs become a practical concern.

### Q9.5: Was the `vista/requirements.txt` (with Redis, Celery, PostgreSQL) ever actually used?

- **Why it cannot be answered from the repo:** `vista/requirements.txt` includes Redis, Celery, and psycopg2-binary, but the running system uses SQLite with APScheduler (not Celery) and in-memory (not Redis). The `vista/backend/requirements.txt` does not include these. [PARTIALLY VERIFIED — two requirements files with different dependencies; unclear which is operational]
- **Why it matters:** If Redis/Celery/PostgreSQL were planned but never deployed, this should be documented as "planned" not "implemented."

---

*End of Document 9 — Questions Requiring Human Input*
