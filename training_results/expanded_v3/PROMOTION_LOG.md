
## Step 1: PRE-CHECK
- Branch: main, tracking origin/main, ahead 9. Remote: https://github.com/M0hammedAyan/AI-Classroom-Intelligent-System.git
- User's unstaged deletions (dataset/1DA22AI402/*, dataset/1DA25AI001/* ...) left untouched; never stage or revert.
- .env: project root .env and vista\.env missing. Only vista\backend\.env exists (not loaded when run from vista\ or project root).
- DB: with no env, running from vista\ would use vista\vista_dev.db (stale 7180288 B copy). Real data is vista\backend\vista_dev.db.
  Fix: start_vista.ps1 now sets VISTA_DB_URL to the absolute path of vista\backend\vista_dev.db (non-secret).
  Verified with VISTA_DB_URL set: /health ok, database connected, GET /api/v1/students total=65 (active). Backend stopped afterwards.
- OpenRouter key: present only in vista\backend\.env, NOT loaded by the backend. Study coach uses rule-based fallback (acceptable for demo).
- Backup: vista\backend\vista_dev_pre_v3_promotion.db, 7208960 bytes, equals source size (git-ignored by *.db).

## ROLLBACK
1. Remove VISTA_FACE_MODEL (env var / start_vista.ps1 line) so the app uses best_model_npz_splitB.pth (untouched).
2. git checkout <commit-before-promotion> -- start_vista.ps1
3. Stop backend, then Copy-Item vista\backend\vista_dev_pre_v3_promotion.db vista\backend\vista_dev.db -Force
4. git revert the App.jsx ROSTER commit.

## Step 2: wire model
- start_vista.ps1 sets VISTA_FACE_MODEL (absolute path to best_model_expanded_v3_splitB.pth; relative paths resolve against cwd) and VISTA_FACE_MODEL_THRESHOLD=0.60 (final value in step 3).
- vista\backend\.env.example documents both.
- Code default unchanged; old best_model_npz_splitB.pth untouched (rollback: point env to it).
- Verified (CPU): model_info() -> 29 classes, threshold 0.6; load_state_dict OK via ResNet50FaceClassifier; random-noise face -> None (conf 0.18).

## Step 3: threshold check (v3 Split B, CPU, app preprocessing via personal_classifier)
Script: training_results\expanded_v3\threshold_check.py; results: threshold_check_results.json; plot: threshold_check.png. Sanity calibration only, not a new accuracy claim; nothing tuned on train.
- Clean test crops (splits_B test, npz aug idx 0, n=138): 137 correct (max-softmax median 0.916, mean 0.901, p05 0.853, min 0.377), 1 wrong (conf 0.326).
- Raw test photos (<=3 per student, SCRFD bbox crop as recognize._crop_face, n=87, no missed detections): 86 correct (median 0.915, mean 0.907, p05 0.863, min 0.651), 1 wrong (conf 0.203).
- Correct predictions below threshold (of 223 correct): 0.60: 2, 0.55: 2, 0.50: 2, 0.45: 2, 0.40: 1, 0.35: 0. All below-threshold correct ones are clean-crop; raw photos: 0 at every level.
- Wrong predictions: max conf 0.326, so every threshold >= 0.35 rejects all of them.
- Non-students: 5 photos of ex-student 1DA22AI402 (not a class) were all predicted 1DA24AI403 at 0.89-0.93 (probably the same person or a lookalike duplicate, so NOT a valid unknown test; they pass any threshold). UI screenshot patches 0.13-0.20, background patch 0.09, flat gray 0.09 (all rejected). One random-noise image reached 0.77 (accepted at 0.60), an arbitrary-input overconfidence case; threshold cannot fix it, face detection upstream guards it.
- Decision: keep VISTA_FACE_MODEL_THRESHOLD=0.60. Counts of lost correct predictions are identical (2/223, 0.9%) for 0.45-0.60, so the stricter value costs nothing here, and a false attendance mark is worse than a miss. No true unknown-person faces exist in the repo, so unknown-face rejection is unverified. start_vista.ps1 and .env.example already hold 0.60 (no change needed).

## Step 4 - add 1DA25AI001-010
- Names/class supplied by user (class "AI&ML 3rd sem"; classroom_id class-aiml-4a, the only existing classroom). Saved in new_students.csv.
- App.jsx ROSTER: 10 `NAME|USN` lines added before the closing backtick line.
- DB vista\backend\vista_dev.db (backup existed): 10 students rows (is_active 1, usn, usn_updated 0) and 10 users rows (role student, <usn>@vista.local, bcrypt "student123").
- Enrolled with vista.vision.enroll.enroll_student, VISTA_DB_URL set before import, excluded photos from regen_list.json removed. All 10 have embeddings.
- Backend restarted (reconcile_current_roster ran): /health ok; DB shows 75 active students, all 10 new still active with embeddings. /api/v1/students needs a token, so the count was read from the DB. Backend stopped, port 8002 free.
- Rollback: restore vista\backend\vista_dev_pre_v3_promotion.db; git revert this commit.

## Step 5 - End-to-end test
Backend run with v3 env (python -m uvicorn from vista\, port 8002), admin login, POST /attendance/mark-batch with held-out Split B test photos. Gallery-vs-classifier decider logged in-process (e2e_test.py decider -> e2e_decider.json); API results in e2e_results.json. Test rows (session_date 2099-01-*, 12 attendance rows, 11 capture_events) deleted afterwards; DB not restored from backup. Pytest: 143 passed, 5 errors (tests/test_timetable.py, pre-existing). npm run build: OK. Backend stopped.

## Step 7: commit and push
- Commits on main: 901c0fe84, 5f767afb2, ab8d0e15d, 34dafcd59, e42b81a62, 4e80e5fc6 (docs), 7dc3ab541 (e2e_cleanup2.py).
- Pushed to origin/main (https://github.com/M0hammedAyan/AI-Classroom-Intelligent-System.git), normal push, no force.
- Not staged: dataset deletions, .db/.pth/.npz, untracked scratch dirs.

## ROLLBACK
1. Model: unset VISTA_FACE_MODEL or restore start_vista.ps1 (git checkout 901c0fe84 -- start_vista.ps1), or point VISTA_FACE_MODEL at training_results\best_model_npz_splitB.pth.
2. DB: stop backend, copy vista\backend\vista_dev_pre_v3_promotion.db over vista\backend\vista_dev.db.
3. Roster: git revert 34dafcd59 (App.jsx ROSTER + student additions).
