# PROMOTION_ASSESSMENT: v3 checkpoint as the live face model

Nothing was swapped. Facts below come from reading `vista/vision/personal_classifier.py`, `vista/vision/recognize.py`, `vista/backend/app/routes/attendance.py`, loading the checkpoints with torch (`promo_check.py` in this folder), and a read-only SQLite query of `vista/backend/vista_dev.db`.

## 1. Loader compatibility (`personal_classifier.py`)

- **Path:** `MODEL_PATH` comes from env `VISTA_FACE_MODEL`, default `training_results/best_model_npz_splitB.pth`. The model can be changed with an env var, with no file overwrite.
- **num_classes and names:** `checkpoint["class_names"]` is read, converted with `str()`, and `num_classes = len(class_names)`. Nothing is hard-coded.
- **v3 checkpoint format:** both v3 checkpoints are dicts with `model_state_dict`, `class_names` (a Python list of str), `epoch`, `val_acc`, `split`, plus extra keys `num_classes` and `lr` that the loader ignores. The live checkpoint is a list too, with 20 names.
  - v3 Split B: 29 names, final layer `head.8.bias` shape (29,), epoch 3.
  - v3 Split A: 29 names, `head.8.bias` (29,), epoch 1.
  - Live: 20 names, `head.8.bias` (20,).
- **Architecture and input:** the loader builds the same ResNet-50 plus head (`head.8` is the last Linear) and resizes to 112x112 with mean=std=0.5 and RGB input. `FIX_LOG.md` states `train_expanded_v3.py` uses the same 112x112, mean/std 0.5, no channel flip. The layer names match (`head.8.*`), so `load_state_dict` should work. I did not run an actual load through `ResNet50FaceClassifier`, only inspected keys and shapes.
- **Threshold:** `VISTA_FACE_MODEL_THRESHOLD` defaults to 0.60 and is applied to the max softmax. v3 was trained with label smoothing 0.1 (train loss floor about 0.66), so its confidences are lower than the baseline's for the same certainty. I did not measure the v3 confidence distribution, so how many correct faces fall below 0.60 is unknown. Check this before the demo.
- **Device:** CPU unless `VISTA_FACE_MODEL_DEVICE=cuda`.

## 2. `_classify_detected_face` (`recognize.py`)

1. It first tries the DB gallery: `_load_student_gallery()` takes active students that have a 512-d embedding and matches with cosine threshold 0.55 (`VISTA_FACE_MATCH_THRESHOLD`). A gallery hit returns directly, and the classifier is not used.
2. Otherwise it crops the face and calls `classify_face`. If the score is at or above the threshold it returns the classifier's USN. Otherwise `student_id` is None.

So the classifier only decides faces the DB gallery misses. Promoting v3 changes only that fallback path.

## 3. Attendance route when the USN is not in `students`

DB state (read-only): 70 students, 65 active. 39 active students have an embedding.

- **Not in DB:** all 10 new 1DA25AI* students. The other 19 v3 classes are in the DB.
- **1DA22AI402:** the row exists but `is_active = 0`, with an embedding. It has 0 attendance rows. Because it is inactive, the gallery loader skips it. The live model still has it as a class, so today the live classifier can output it. v3 does not know it, so a 1DA22AI402 photo would be labelled as another student or fall below the threshold.
- **`attendance.py` (single and multi-face paths):** a non-None USN is written as an `Attendance` row without checking that it exists in `students`. `attendance.student_id` is declared as a foreign key, but SQLite foreign keys are off (`PRAGMA foreign_keys` returned 0, and `db.py` does not enable it). So an unknown USN would be stored, not rejected. The response from `_mark_response` has `student_name: null` for it. `/attendance/log` builds its list from the students table, so those rows never show in the roster view.
- **Effect:** a new student would be recognised by the model, but their attendance would appear as an orphan row with no name and would not show in the class log or per-student views. This is a data gap, not a crash. I did not trace every other query (stats, exports) over that table.

## 4. Promotion steps (do not run until approved)

1. **Add the 10 students (1DA25AI001-010) to `students`** through the normal roster flow, with the right classroom and `is_active = 1`. This is a DB write, so it needs the owner's approval. Without it, new-student attendance is orphaned.
2. **Smoke test v3 without touching any file:** set `VISTA_FACE_MODEL` to `training_results/expanded_v3/best_model_expanded_v3_splitB.pth` in the shell that starts the backend (do not edit `.env`, or record the change on purpose). Confirm `model_info()` reports 29 classes.
3. **Check the threshold:** run a few real classroom frames or the clean test crops through `classify_face`, and compare how many correct predictions fall under 0.60. If many do, set `VISTA_FACE_MODEL_THRESHOLD` lower (try 0.45 to 0.50 and verify).
4. **End-to-end check:** run `/attendance` with a photo of a kept student, a new student, and an unknown person. Confirm names appear and the unknown person is rejected.
5. **Rollback:** unset `VISTA_FACE_MODEL`, which returns to `best_model_npz_splitB.pth` (untouched). Restart the backend.
6. **Do not copy over `best_model_npz_splitB.pth`.** Use the env var, or copy v3 to a new filename. The `.pth` files are gitignored (`expanded_v3/*.pth`), so the team machine needs the file copied by hand.

## 5. Recommendation for the 7 Nov demo

Promote **v3 Split B** through the env var, but only after steps 1, 3 and 4 pass. If step 1 cannot be done, keep the live model for the demo. Reasons:

- v3 is trained on a verified, deduplicated dataset. Test accuracy is 99.28% (137/138, 95% CI 96.01-99.87%) on clean single-face crops, and it covers the 10 new students the live model cannot recognise.
- Split B is preferred over A. A's val accuracy was 1.0 at every epoch, so its checkpoint (epoch 1) was picked by order, not by evidence. B has a real val signal (best 0.9928 at epoch 3) and a larger test set.
- The risks are the untested confidence threshold, the missing DB rows, and the fact that clean-crop accuracy does not predict accuracy on far, small or occluded classroom faces. 1DA24AI404 was misclassified in both splits, so check this student by hand during the smoke test.
