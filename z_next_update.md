# VISTA - Next Release & Accuracy Improvement Roadmap (`z_next_update.md`)

This document outlines the actionable checklist, architectural improvements, and dataset enhancements planned for the upcoming update to push face recognition accuracy beyond 95%+ and optimize system operations.

---

## 1. Model Training & Accuracy Improvement Checklist

### A. Dataset Collection & Expansion
- [ ] **Multi-Angle Enrollment (5-7 Poses per Student):**
  - [ ] Frontal neutral ($0^\circ$).
  - [ ] Yaw Left ($-20^\circ$) and Yaw Right ($+20^\circ$).
  - [ ] Pitch Up ($+15^\circ$) and Pitch Down ($-15^\circ$).
  - [ ] Natural facial expression variants (smiling, talking).
- [ ] **Classroom Environment Illumination:**
  - [ ] Collect images under actual classroom conditions (overhead fluorescent lights, backlight from windows, ambient afternoon shadows).
- [ ] **Distance & Resolution Scaling:**
  - [ ] Capture samples representing back-row seats ($40\times 40$ to $60\times 60$ px face crops) to avoid overfitting on clean, high-res selfie portraits.
- [ ] **Accessories & Partial Occlusions:**
  - [ ] Include samples with eyeglasses, bangs/hair covering the forehead, and varied clothing/hoods.

---

### B. Vision Preprocessing & Embeddings
- [ ] **Multi-Template Gallery (Multiple Centroids per Student):**
  - [ ] Store 3 to 5 centroid embeddings per student in SQLite/memory (e.g., *Frontal*, *Tilted*, *Profile/Glasses*).
  - [ ] Match incoming face against the nearest cluster centroid (reduces false negatives from pose shifts).
- [ ] **Detector Upgrade for Small Faces:**
  - [ ] Evaluate and benchmark **SCRFD** (Sample and Computation Redistribution for Face Detection) or **RetinaFace-ResNet50** to improve detection recall on wide-angle lecture hall captures.
- [ ] **Lightweight Face Restoration / Super-Resolution:**
  - [ ] Test integration of tiny CodeFormer or GFPGAN landmark enhancement for back-row blurry face crops.

---

### C. Architecture & Training Optimization
- [ ] **Fine-Tune with Additive Angular Margin (ArcFace / AdaCos Loss):**
  - [ ] Replace standard Cross-Entropy on ResNet-50 with ArcFace margin loss ($s=64.0, m=0.5$) to maximize inter-class separation and intra-class compactness.
- [ ] **Augmentation Pipeline Hardening:**
  - [ ] Add `MotionBlur` and `GaussianBlur` to simulate student head motion.
  - [ ] Add `RandomShadow` and `Downscale` to simulate classroom lighting and camera sensor limits.

---

### D. Video & Temporal Verification
- [ ] **Multi-Frame Temporal Voting (Track-and-Vote):**
  - [ ] For live camera streams or short burst captures (3-5 seconds), implement ByteTrack / SORT tracking to aggregate embeddings across tracklets.
  - [ ] Mark attendance based on majority voting over 5 consecutive frames rather than single-frame decisions.

---

## 2. Completed in Current Release (Recap)

- [x] **Roster Status Synchronization:** Fixed attendance roster status to immediately show **Present** with confidence scores upon teacher photo capture/batch detection.
- [x] **UI Polish & Character Encoding:** Removed corrupted characters (`ΓÇö`, `┬╖`, etc.) across teacher roster and notification center; restored clean standard glyphs (`-`, `·`, `🔔`, `✕`).
- [x] **Clean Workspace Layout:** Streamlined the review interface by removing redundant upload buttons from the roster card and unifying image processing through the main class capture workflow.
- [x] **Multi-Classroom ID Resolution:** Updated backend `attendance_log` to resolve both class section codes (`AIML-4A`) and IDs (`class-aiml-4a`) seamlessly.

---

## 📅 Target Milestone Timeline

| Phase | Milestone | Priority | Expected Impact |
|---|---|---|---|
| **Phase 1** | Collect 5 poses per student & multi-centroid gallery | 🔴 High | +4% to +6% accuracy |
| **Phase 2** | ArcFace fine-tuning & realistic blur/lighting augmentations | 🟡 Medium | +2% to +3% accuracy |
| **Phase 3** | SCRFD detector & multi-frame temporal voting | 🟢 High | Significant back-row recall boost |
