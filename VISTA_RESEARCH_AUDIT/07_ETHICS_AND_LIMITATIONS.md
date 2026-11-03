# Document 7 — Ethics and Limitations

**Project:** VISTA — Vision-based Intelligent Student Tracking & Academics
**Audit Phase:** 6 (Ethics and Limitations)
**Basis:** `vista/docs/CONSENT_FORM.md` (direct inspection), `vista/vision/liveness.py` (direct inspection), `vista/backend/app/routes/auth.py` (via `audit-inspection.md`), `vista/backend/app/services/coach_service.py` (direct inspection), `paper/PAPER.md` Sections VIII-IX, `audit-claim-verification.md`.

---

## 1. Biometric Data Handling

### Face Image Storage

| Aspect | Claimed | Actual | Evidence | Classification |
|--------|---------|--------|---------|---------------|
| Raw photo collection | "3-5 facial photographs" per student | 27-41 raw images per student | `CONSENT_FORM.md` vs `dataset/` directory | [CONTRADICTED] |
| Raw photo storage location | "Local server" | `dataset/` directory (~1.94 GB), committed to repository | `dataset/` exists with 680 files | [VERIFIED — photos present] |
| Raw photo retention | "Photos deleted after processing" | Photos retained indefinitely (~1.94 GB in repo) | `CONSENT_FORM.md` vs `dataset/` | [CONTRADICTED] |
| Photo format | Not specified | JPEG/JPG, 2-4 MB each, camera captures | `dataset/` file inspection | [VERIFIED] |
| Upload directory | Not mentioned in consent | Paper mentions `uploads/` directory | `PAPER.md` Section IX | [DOCUMENTED ONLY] |

**Assessment:** The consent form states photos are "deleted after processing," but ~1.94 GB of raw face images are retained in the `dataset/` directory. This is a direct contradiction between the consent form and the actual data handling practice. [CONTRADICTED]

### Embedding Storage

| Aspect | Claimed | Actual | Evidence | Classification |
|--------|---------|--------|---------|---------------|
| Embedding storage | "Encrypted database" | SQLite stores embeddings as plaintext JSON in `students.embedding` column | `CONSENT_FORM.md` vs `vista/backend/app/models/student.py`, `db.py` | [CONTRADICTED] |
| Embedding format | Not specified | 512-dimensional L2-normalized ArcFace embeddings, JSON-serialized | `vista/vision/embed.py`, `vista/vision/match.py` | [VERIFIED] |
| Embedding count | Not specified | 1 averaged embedding per student (from 3-5 enrollment images) | `vista/vision/enroll.py` | [VERIFIED] |
| NPZ storage | Not mentioned in consent | `data/processed/facial_pipeline_results.npz` (1.15 GB) — contains all embeddings + images + metadata | `data/processed/` | [VERIFIED — present] |

**Assessment:** The consent form claims the database is "encrypted," but SQLite is used with no encryption at rest. Embeddings are stored as plaintext JSON strings. [CONTRADICTED — no encryption implemented in `db.py` or any model file]

### Retention Policies

| Aspect | Claimed | Actual | Evidence | Classification |
|--------|---------|--------|---------|---------------|
| Retention duration | "8 weeks pilot + 4 weeks analysis = 12 weeks" | Data retained indefinitely (as of audit) | `CONSENT_FORM.md` vs data presence | [CONTRADICTED] |
| Deletion mechanism | "You can request deletion at any time" | No deletion endpoint or script found in backend routes | `CONSENT_FORM.md` vs `vista/backend/app/routes/` | [UNVERIFIED — no deletion API] |
| Data minimization | "Not shared with any third party" | If `LLM_USE_API=true`, aggregated academic numbers sent to OpenRouter (no PII) | `CONSENT_FORM.md` vs `coach_service.py` | [PARTIALLY VERIFIED — PII stripped but data leaves server] |

**Assessment:** The retention policy is not enforced. No deletion mechanism exists in the codebase. The consent form's 12-week retention claim is contradicted by indefinite data retention. [CONTRADICTED]

---

## 2. Consent Mechanisms

### What Exists

A consent form template exists at `vista/docs/CONSENT_FORM.md`. [VERIFIED — file inspected directly]

It covers: [VERIFIED — text of consent form]
- Purpose of study (AI-based attendance via face recognition)
- What is collected (3-5 facial photographs, attendance records)
- How data is used (face embedding creation, attendance tracking)
- Key points (local only, not shared, deletable, voluntary, withdrawal, duration)
- Risks (minimal — false match, teacher verification)
- Consent statement with checkboxes
- Parent/guardian signature (if under 18)
- Researcher contact information

### What Is Missing or Incomplete

| Gap | Evidence | Classification |
|-----|---------|---------------|
| Faculty advisor name is a placeholder (`[Guide Name]`) | `CONSENT_FORM.md` line: "Faculty Advisor: [Guide Name]" | [UNVERIFIED — never filled] |
| Ethics committee name is a placeholder (`[Department/Faculty Committee Name]`) | `CONSENT_FORM.md`: "This study has been reviewed by [Department/Faculty Committee Name] and approved" | [UNVERIFIED — never filled] |
| No signed consent forms in the repository | Search found no signed copies | [UNVERIFIED] |
| Consent for LLM coaching feature | Consent form mentions only face data, not LLM interaction or data sent to OpenRouter | [UNVERIFIED — not covered] |
| Consent for augmented data generation | Consent form does not mention 30x augmentation of face images | [UNVERIFIED — not covered] |
| No consent for embedding storage in NPZ file (1.15 GB) | Consent form mentions "face embedding" but not bulk NPZ storage | [UNVERIFIED — not covered] |
| Email domain inconsistency | Consent form uses `mohammed.ayan@dsatm.edu` but paper uses `@dr-ait.org` | [CONTRADICTED — different domains] |

**Assessment:** The consent form is a template with unfilled placeholder fields. No evidence of signed consent or institutional ethics approval exists in the repository. This is a **publication blocker** — any paper making biometric data claims must document ethics approval and consent procedures. [UNVERIFIED]

---

## 3. Authentication and Authorization Security Analysis

### What Is Implemented

| Feature | Implementation | Evidence | Classification |
|---------|---------------|---------|---------------|
| JWT authentication | HS256, 8-hour expiry | `vista/backend/app/routes/auth.py` | [VERIFIED] |
| Password hashing | bcrypt, 12 rounds | `auth.py` | [VERIFIED] |
| Role-based access control | 3 active roles (admin, teacher, student); 3 legacy rejected | `auth.py`, `permissions.py` | [VERIFIED] |
| Rate limiting | 5 login attempts / 5 min / IP | `auth.py` | [VERIFIED] |
| Token blocklist (logout) | In-memory `set[str]` | `auth.py` | [PARTIALLY VERIFIED] |

### Security Vulnerabilities

| Vulnerability | Detail | Evidence | Risk Level |
|--------------|--------|---------|------------|
| **In-memory token blocklist** | JWT logout adds token to Python set; restart clears blocklist, allowing revoked tokens to work again | `auth.py`, `audit-inspection.md` | Medium (pilot-grade) |
| **In-memory rate limiting** | Login rate limit stored in memory; restart resets counters | `auth.py`, `audit-inspection.md` | Low-Medium (pilot-grade) |
| **Insecure JWT secret fallback** | `VISTA_JWT_SECRET` env var falls back to hardcoded insecure default with warning | `auth.py`, `audit-inspection.md` | Medium |
| **No encryption at rest** | SQLite stores all data (including face embeddings) in plaintext | `db.py` | Medium-High (biometric data) |
| **No encryption in transit** (if not behind TLS) | Backend serves HTTP directly; TLS depends on deployment, not enforced in code | `main.py` — no TLS configuration | Medium (deployment-dependent) |
| **Single shared JWT secret** | HS256 symmetric key; no key rotation mechanism | `auth.py` | Low-Medium |

**Assessment:** The authentication system is functional for pilot use but has clear pilot-grade limitations: non-persistent blocklist and rate limiting, insecure secret fallback, and no encryption at rest for biometric data. For a production deployment, these would need to be addressed. For a research paper, they should be acknowledged as limitations. [VERIFIED — all vulnerabilities confirmed in source code]

---

## 4. Encryption of Biometric Data

### At Rest

| Data | Encryption | Evidence | Classification |
|------|-----------|---------|---------------|
| Face images (raw) | **None** — stored as plaintext JPEGs in `dataset/` | `dataset/` directory | [VERIFIED — no encryption] |
| Face embeddings (DB) | **None** — stored as plaintext JSON in SQLite | `students.embedding` column, `db.py` | [VERIFIED — no encryption] |
| Face crops + embeddings (NPZ) | **None** — stored as plaintext NumPy archive | `data/processed/facial_pipeline_results.npz` | [VERIFIED — no encryption] |
| ResNet-50 model weights | **None** — stored as plaintext `.pth` files | `training_results/best_model_npz_splitB.pth` | [VERIFIED — no encryption] |
| Student academic data | **None** — SQLite plaintext | `db.py` | [VERIFIED — no encryption] |
| JWT secret | Environment variable | `.env` | [VERIFIED — stored in env, not encrypted at rest] |

**Assessment:** No biometric data is encrypted at rest. The consent form's claim of "encrypted database" is false. [CONTRADICTED — `CONSENT_FORM.md` claims encryption; `db.py` has no encryption]

### In Transit

| Data Path | Encryption | Evidence | Classification |
|-----------|-----------|---------|---------------|
| Frontend ↔ Backend | Depends on deployment (no TLS in code) | `main.py` — no TLS config | [UNVERIFIED — deployment-dependent] |
| Backend ↔ OpenRouter (LLM) | HTTPS (OpenRouter API) | `coach_service.py:_call_openrouter()` uses `urllib.request.urlopen` | [VERIFIED — HTTPS by default] |
| Backend ↔ Ollama (local LLM) | Local only (no network) | `coach_service.py:_call_ollama()` | [VERIFIED — no network transit] |
| Backend ↔ SQLite | Local only (file-based) | `db.py` | [VERIFIED — no network transit] |

**Assessment:** In-transit encryption depends on deployment configuration (TLS reverse proxy). The OpenRouter LLM calls use HTTPS. No biometric data is transmitted to external services. [PARTIALLY VERIFIED]

---

## 5. Data Sent to External AI Services (LLM Calls)

### What Is Sent to OpenRouter

When `LLM_USE_API=true` and `OPENROUTER_API_KEY` is configured: [VERIFIED — `coach_service.py:_call_openrouter()`]

**Sent (aggregated numerical facts):**
- Overall attendance percentage, session counts (attended/total)
- Per-subject attendance: percentage, attended/total, missable classes, recovery streak
- CIE scores (CIE 1/2/3, final scores, eligibility)
- Risk level and risk reasons
- Target threshold (75%)
- Subject names and codes (academic course identifiers)

[VERIFIED — `get_coach_facts()` returns this data; `json.dumps(facts)` injects into system prompt labeled "VERIFIED ACADEMIC CONTEXT (NO PII)"]

**NOT sent (PII stripped):**
- Student name
- Student USN/ID
- Student email
- Phone number
- Classroom name
- Parent contact information

[VERIFIED — `get_coach_facts()` does not include these fields; system prompt explicitly labeled "NO PII"]

**User message:** The student's query text is sent, wrapped in `<student_query>` XML tags. [VERIFIED — `coach_service.py`]

### Assessment

The coach service implements a reasonable PII sanitization pattern: only aggregated numerical academic data is sent to the external LLM, with explicit "NO PII" labeling. However: [VERIFIED — implementation is sound]

1. Subject names and codes are technically sent — these could potentially identify a student if combined with external knowledge. [PARTIALLY VERIFIED — minor re-identification risk]
2. The user's raw query text is sent — this could contain PII if the student types their own name or USN in the query. [PARTIALLY VERIFIED — no input-side PII filtering beyond 1000-char length limit]
3. Chat messages are persisted to local SQLite (`chat_messages` table) — no external persistence. [VERIFIED]

### When Ollama Is Used

When `LLM_USE_OLLAMA=true`: 100% on-premise, no external network calls. [VERIFIED — `coach_service.py:_call_ollama()` calls local `OLLAMA_BASE_URL`]

### When No LLM Is Configured

Deterministic rule-based fallback — no external calls at all. [VERIFIED — `generate_rule_based_reply()`]

---

## 6. Institutional Ethics Approval Requirements

### Requirements for Biometric Attendance Systems

Biometric data collection (face images) for research purposes typically requires: [DOCUMENTED ONLY — general research ethics requirements, not specific to any single institution]

1. **Institutional Review Board (IRB) / Ethics Committee approval** — documentation of review and approval
2. **Informed consent** — signed consent forms from all participants (or guardians if minors)
3. **Data Protection Impact Assessment (DPIA)** — for high-risk biometric processing
4. **Right to withdrawal** — mechanism for participants to withdraw and have data deleted
5. **Data retention policy** — defined retention period with deletion enforcement

### VISTA's Current Status

| Requirement | Status | Evidence | Classification |
|-------------|--------|---------|---------------|
| IRB/Ethics committee approval | **Not documented** — consent form has placeholder `[Department/Faculty Committee Name]` | `CONSENT_FORM.md` | [UNVERIFIED] |
| Signed consent forms | **Not found** — no signed copies in repo | Repository search | [UNVERIFIED] |
| DPIA | **Not conducted** (no document found) | Repository search | [UNVERIFIED] |
| Right to withdrawal | **Claimed in consent form** but no deletion API in backend | `CONSENT_FORM.md` vs `routes/` | [UNVERIFIED — no implementation] |
| Data retention policy | **Claimed 12 weeks** but data retained indefinitely | `CONSENT_FORM.md` vs `dataset/` presence | [CONTRADICTED] |

**Assessment:** No evidence of institutional ethics approval exists in the repository. The consent form template has unfilled placeholder fields. This is a **critical publication blocker** — IEEE journals and most reputable venues require documented ethics approval for research involving human biometric data. [UNVERIFIED]

---

## 7. Bias and Fairness Issues in Face Recognition

### Demographic Bias

| Concern | Status | Evidence | Classification |
|---------|--------|---------|---------------|
| Skin tone fairness evaluation | **Not conducted** | `PAPER.md` Section VIII: "Demographic and skin tone fairness evaluations were not conducted" | [VERIFIED — acknowledged gap] |
| Gender fairness evaluation | **Not conducted** | Paper does not mention gender-based analysis | [UNVERIFIED] |
| Age fairness evaluation | **Not conducted** | All subjects are college-age students; no cross-age evaluation | [UNVERIFIED] |
| Lighting condition variation | **Not systematically evaluated** | Paper mentions "severe shadow occlusions across window seats" as failure mode (Section VII) | [DOCUMENTED ONLY — qualitative observation] |
| Pose variation | **Not systematically evaluated** | Paper mentions "extreme pitch (>30° downward tilt)" as failure mode | [DOCUMENTED ONLY — qualitative observation] |

### Technical Bias Sources

1. **Training data composition:** 20 students from a single AI&ML department — not demographically diverse. [VERIFIED — `dataset/` has 20 USN directories]
2. **ArcFace model (w600k_r50):** Pretrained on the WebFace600K dataset — known to have demographic composition biases from training data. [DOCUMENTED ONLY — general knowledge about WebFace dataset composition]
3. **ResNet-50 (ImageNet pretrained):** ImageNet has known demographic biases in its class composition. [DOCUMENTED ONLY — general knowledge]
4. **Per-class performance variation:** Students `1DA22AI402` (F1=0.000 in Split B) and `1DA24AI403` (F1=0.4615) consistently underperform — could indicate image quality issues, insufficient enrollment photos, or demographic-related factors. [VERIFIED — `training_results/results_npz_splitB.txt`]

**Assessment:** No fairness evaluation was conducted. The paper honestly acknowledges this gap. For a biometric system deployed in an educational context, demographic fairness is a critical ethical concern. This must be addressed before any claim of fair or equitable performance. [VERIFIED — gap acknowledged; UNVERIFIED — no evaluation conducted]

---

## 8. Technical Limitations of Each Major Component

### Face Recognition Pipeline

| Limitation | Detail | Evidence | Classification |
|-----------|--------|---------|---------------|
| Closed-set only | No impostor/open-set testing; FAR measures wrong-student matches, not unknown-identity rejection | `CLAIMS_TABLE.md` C-16 | [VERIFIED] |
| 20 students only | Pilot-scale; no evidence of scaling beyond 20 identities | `dataset/` has 20 dirs | [VERIFIED] |
| CPU-only inference | No GPU acceleration; latency may not scale to larger galleries | `detect.py` uses CPUExecutionProvider | [VERIFIED] |
| Heuristic liveness | No neural anti-spoofing; vulnerable to video replay, silicone masks, deepfakes | `liveness.py` — heuristic only | [VERIFIED] |
| Liveness formula inaccuracy | Paper references EAR; code does not compute EAR | `liveness.py` vs `PAPER.md` | [CONTRADICTED] |
| Per-class weakness | 2 of 20 students consistently fail | `results_npz_splitB.txt` | [VERIFIED] |
| Non-deterministic threshold sweep | `hash()` split not stable across processes | `evaluate_recognition.py` | [VERIFIED] |
| Missing ablation generator | Cannot reproduce cascade ablation | Script absent | [VERIFIED] |
| Tracker not wired | ByteTrack tracker implemented but not connected to attendance routes | `tracker.py` vs `attendance.py` | [VERIFIED] |

### Risk Prediction System

| Limitation | Detail | Evidence | Classification |
|-----------|--------|---------|---------------|
| Below majority baseline | XGBoost 50.0% < 53.5% majority baseline | `risk_model_evaluation.json` | [VERIFIED] |
| Synthetic data only | No real longitudinal student outcomes | `student_data.csv` is synthetic | [VERIFIED] |
| Circular labels | Labels derived from same rule engine as production | `generate_sample_data.py` | [VERIFIED] |
| LOW class failure | F1=0.000 for minority class | `risk_model_evaluation.json` | [VERIFIED] |
| No cross-validation | Single 80/20 split only | `train.py` | [VERIFIED] |
| Generator out of sync | Script produces 200 rows, CSV has 1000; different label logic | `generate_sample_data.py` vs CSV | [CONTRADICTED] |
| No class weighting | XGBoost has no `scale_pos_weight` | `train.py` config | [VERIFIED] |

### AI Study Coach

| Limitation | Detail | Evidence | Classification |
|-----------|--------|---------|---------------|
| Narrow groundedness evaluation | 10 queries, 1 student only | `coach_groundedness.json` | [VERIFIED] |
| No adversarial testing | No prompt injection stress tests | `evaluate_coach_groundedness.py` | [VERIFIED] |
| External LLM dependency | When using OpenRouter, academic data leaves server | `coach_service.py` | [VERIFIED — PII stripped but data leaves] |
| User input not PII-filtered | Student can type own name/USN in query | `coach_service.py` — no input-side PII filter | [PARTIALLY VERIFIED] |
| No rate limiting at coach level | Only notification system has rate limiting | `coach_service.py` | [VERIFIED] |

### Platform/Backend

| Limitation | Detail | Evidence | Classification |
|-----------|--------|---------|---------------|
| In-memory token blocklist | Revoked tokens work after restart | `auth.py` | [VERIFIED] |
| No encryption at rest | SQLite plaintext | `db.py` | [VERIFIED] |
| SQLite only | No PostgreSQL deployment (only in requirements) | `db.py` | [VERIFIED] |
| Parent alerts incomplete | Table exists, delivery mechanism unclear | `parent_alerts` table | [PARTIALLY VERIFIED] |
| Monolithic frontend | 88 KB single `App.jsx` | `App.jsx` | [VERIFIED — not a limitation per se] |
| Multiple stale DB copies | 3 copies of `vista_dev.db` at different locations | Inventory | [VERIFIED] |

---

## 9. Liveness Detection Limitations

### Current Implementation

`vista/vision/liveness.py` implements a heuristic-only liveness check: [VERIFIED — file inspected directly]

| Check | Threshold | Purpose | Evidence |
|-------|-----------|---------|---------|
| Detection confidence | < 0.5 → fail | Very low confidence suggests printed photo | [VERIFIED — `MIN_DET_CONFIDENCE = 0.5`] |
| Face width | < 50px → fail | Tiny faces are unreliable/suspicious | [VERIFIED — `MIN_FACE_WIDTH = 50`] |
| Laplacian variance | < 20.0 → penalty (score × 0.6) | Blurriness check — printed photos tend to be sharper/flatter | [VERIFIED — `MIN_LAPLACIAN_VARIANCE = 20.0`] |

### What Is NOT Implemented

| Missing Feature | Impact | Evidence | Classification |
|----------------|--------|---------|---------------|
| Neural anti-spoofing (MiniFASNet) | No protection against high-quality spoofing | `liveness.py` docstring: "Phase 2 will integrate MiniFASNet" | [DOCUMENTED ONLY — future work] |
| EAR (Eye Aspect Ratio) | Paper claims EAR is used; code does not compute it | `liveness.py` vs `PAPER.md` | [CONTRADICTED] |
| Blink detection | No temporal liveness (single-frame only) | `liveness.py` — no video sequence | [VERIFIED] |
| 3D depth analysis | No protection against 3D masks | Not implemented | [VERIFIED] |
| Infrared/thermal liveness | No protection against screen replay | Not implemented | [VERIFIED] |

### Vulnerability Assessment

The current heuristic liveness check is vulnerable to: [DOCUMENTED ONLY — paper acknowledges in Section VIII, Q5 in PAPER_TODO.md]
- High-definition video replay attacks
- Curved screen attacks (phone/tablet held up)
- Silicone masks
- Deepfake video presentations
- Printed photos with sufficient texture variance

**Assessment:** The liveness module provides minimal anti-spoofing protection and should not be relied upon for security-critical applications. The paper and PAPER_TODO.md honestly acknowledge this. The paper's formula referencing EAR is factually incorrect and must be corrected. [CONTRADICTED — paper formula; VERIFIED — honest acknowledgment of limitations]

---

## 10. Academic Risk Prediction Fairness Concerns

| Concern | Status | Evidence | Classification |
|---------|--------|---------|---------------|
| Class imbalance bias | Severe: 6% LOW, 53.5% HIGH → model fails on minority class (LOW F1=0.000) | `risk_model_evaluation.json` | [VERIFIED] |
| No class weighting | XGBoost has no `scale_pos_weight` or sample weights | `train.py` config | [VERIFIED] |
| No protected-attribute fairness | No evaluation of risk predictions across demographic groups | Paper does not address | [UNVERIFIED] |
| Circular labeling bias | Labels derive from deterministic rules → model learns rule engine biases | `generate_sample_data.py` | [VERIFIED] |
| No real-world validation | Risk predictions not validated against actual student outcomes | Synthetic data only | [VERIFIED] |
| Over-prediction of HIGH class | Model predicts HIGH for 131/200 (65.5%) of test samples; actual HIGH is 53.5% | Confusion matrix analysis | [VERIFIED — 131 predicted HIGH vs 107 actual] |
| Under-prediction of LOW class | Model predicts LOW for 1/200 (0.5%) of test samples; actual LOW is 6% | Confusion matrix analysis | [VERIFIED — 1 predicted LOW vs 12 actual] |

**Assessment:** The risk model exhibits systematic bias toward predicting the majority class (HIGH) and completely fails to identify the minority class (LOW). This means the system would systematically miss low-risk students who need attention (false negatives on LOW) while over-flagging medium-risk students as high-risk (false positives on HIGH). In an educational context, this could lead to intervention fatigue (too many HIGH flags) and missed opportunities (LOW students not identified). [VERIFIED — all metrics confirmed in confusion matrix]

---

## 11. Recommendations for Ethical Compliance Before Publication

### Critical (Must Address Before Submission)

1. **Obtain institutional ethics approval** — document IRB/ethics committee review and approval for biometric data collection. Fill the placeholder fields in the consent form. [UNVERIFIED — currently missing]

2. **Collect and archive signed consent forms** — obtain signed consent from all 20 enrolled students (or guardians if any are minors). Store records securely. [UNVERIFIED — no signed copies]

3. **Correct the consent form** — fix all contradictions:
   - Change "3-5 photographs" to actual count (27-41)
   - Remove "photos deleted after processing" (photos are retained)
   - Remove "encrypted database" (SQLite is plaintext)
   - Add consent for LLM coaching and data sent to OpenRouter
   - Add consent for 30x augmentation
   - Update retention policy to match actual practice
   [CONTRADICTED — multiple contradictions documented above]

4. **Implement data deletion API** — the consent form promises deletion on request; no deletion endpoint exists. [UNVERIFIED]

5. **Add LLM coaching consent** — the current consent form covers only face data, not the LLM interaction or data sent to external services. [UNVERIFIED]

### High Priority (Should Address Before Submission)

6. **Conduct demographic fairness evaluation** — evaluate recognition accuracy across skin tones, gender, and lighting conditions. [UNVERIFIED — paper acknowledges gap]

7. **Add encryption at rest** — encrypt SQLite database or migrate to PostgreSQL with encryption. At minimum, encrypt the biometric embedding column. [VERIFIED — currently plaintext]

8. **Implement open-set impostor testing** — create a test set with un-enrolled faces and measure rejection rate. [VERIFIED — absent]

9. **Add input-side PII filtering for coach** — filter student name/USN from user queries before sending to LLM. [PARTIALLY VERIFIED — not currently implemented]

### Medium Priority (Should Address Before Production)

10. **Implement persistent token blocklist** — use Redis or database table instead of in-memory set. [VERIFIED — currently in-memory]

11. **Enforce data retention policy** — implement automated deletion after the stated retention period. [VERIFIED — not enforced]

12. **Remove insecure JWT secret fallback** — require explicit secret configuration, fail safely if absent. [VERIFIED — insecure fallback exists]

---

*End of Document 7 — Ethics and Limitations*
