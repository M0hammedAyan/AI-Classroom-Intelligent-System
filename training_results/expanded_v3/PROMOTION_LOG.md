
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
