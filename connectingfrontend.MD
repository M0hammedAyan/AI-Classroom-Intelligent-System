# Connecting the Personal Face Model to the Frontend

## Goal

When a teacher selects a live classroom photo in the frontend, the image must travel through the existing API to the personally trained face-classification model, which returns student identities and attendance results.

## Current Runtime Path

`Frontend photo -> POST /api/v1/attendance/mark-batch -> FastAPI attendance route -> vision recognition -> database attendance -> frontend results`

The frontend already sends the photo to the backend. The integration work belongs primarily in the backend vision layer; the frontend request contract can remain unchanged.

## Required Tasks

### Model integration

- [x] Add a runtime loader for `training_results/best_model_npz_splitB.pth`.
- [x] Recreate the exact ResNet-50 architecture used during training.
- [x] Load the checkpoint lazily once per backend process.
- [x] Load `class_names` from the checkpoint rather than duplicating labels.
- [x] Use the same preprocessing as training: RGB, resize to 112x112, tensor conversion, mean 0.5, std 0.5.
- [x] Use CPU by default and support CUDA only when explicitly configured.
- [x] Return the predicted student ID and softmax confidence.
- [x] Apply a configurable confidence threshold and return `None` for unknown/low-confidence faces.
- [x] Do not silently fall back to ArcFace identity matching when the personal checkpoint is missing.

### Vision pipeline

- [x] Keep SCRFD face detection for locating faces in the submitted photo.
- [x] Keep the existing liveness check before writing attendance.
- [x] Crop each detected face from the submitted image and pass it to the personal classifier.
- [x] Use the personal classifier in both `recognize()` and `recognize_all()`.
- [x] Preserve the existing result contract: `student_id`, `confidence`, and `liveness_passed`.
- [x] Preserve multi-face deduplication for classroom photos.
- [x] Ensure a classifier prediction is only accepted for a student in the checkpoint class list.

### Backend and database

- [x] Keep `/api/v1/attendance/mark` compatible with the current frontend.
- [x] Keep `/api/v1/attendance/mark-batch` compatible with the current frontend.
- [x] Store the classifier confidence in attendance records.
- [ ] Confirm that startup student synchronization creates database rows for every checkpoint class.
- [ ] Decide how newly enrolled students are handled, because a fixed classifier cannot recognize a student class that was not present during training.
- [ ] Retrain and replace the checkpoint whenever new student identities are added.
- [ ] Keep database embeddings only if ArcFace enrollment/matching remains needed elsewhere; they are not used for personal-classifier identity prediction.

### Frontend

- [x] Keep the existing photo upload and base64 request flow.
- [x] Keep the existing attendance result display.
- [ ] Add a visible model/version indicator if desired, for example `Personal ResNet Split B`.
- [ ] Display low-confidence predictions as unrecognized instead of marking attendance.
- [ ] Test the teacher attendance page with a classroom image and with an unknown face.
- [ ] Test the single-face recognition page with the same backend path.

### Validation

- [ ] Add unit tests for checkpoint loading and class-name loading.
- [ ] Add inference tests for output shape, confidence range, and unknown threshold behavior.
- [ ] Run the existing vision tests.
- [ ] Run backend attendance tests.
- [ ] Test one real image through the HTTP endpoint.
- [ ] Compare live predictions against the recorded 70:15:15 test accuracy of 89.11%.
- [ ] Retrain on the current artifact before claiming final production metrics: the current NPZ has 20 classes and 20,130 samples, while the saved training report was generated from an older 21-class and 21,210-sample artifact.

## Important Model Boundary

The personal model is a ResNet-50 classifier fine-tuned for the known student classes. SCRFD is still used for face localization, and the liveness heuristic is still used for anti-spoofing. Replacing SCRFD would be a separate detector-training project.

## Known Limitations

- The current checkpoint recognizes only the student IDs stored in its `class_names` list.
- Adding a new student requires retraining or replacing the classifier.
- A single-frame liveness heuristic is not equivalent to a deep anti-spoofing model.
- The current test set is small; classroom deployment requires a separate real-world evaluation set.
- The frontend does not train or validate models. Training and validation remain offline backend/research workflows.

## Completion Criteria

The integration is complete when a frontend classroom photo reaches the backend, the backend loads the personal checkpoint, the classifier predicts a known student or rejects the face, attendance is stored, and the frontend displays the returned result without using ArcFace gallery matching for identity.
