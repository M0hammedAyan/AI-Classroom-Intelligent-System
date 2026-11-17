# VISTA - Startup Script (PowerShell)
# Starts Backend (:8002) and Frontend (:5173) in separate windows

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Starting VISTA Platform (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

# Set database environment variable to guaranteed synchronized database
$env:VISTA_DB_URL = "sqlite:///$($PSScriptRoot -replace '\\','/')/vista/backend/vista_dev.db"

# Face classifier: v3 (29 classes). Absolute path, because personal_classifier.py
# resolves relative paths against the current working directory.
# Rollback: point to training_results\best_model_npz_splitB.pth
$env:VISTA_FACE_MODEL = Join-Path $PSScriptRoot "training_results\expanded_v3\best_model_expanded_v3_splitB.pth"
$env:VISTA_FACE_MODEL_THRESHOLD = "0.60"

# 1. Start Backend
Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8002 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn vista.backend.app.main:app --host 127.0.0.1 --port 8002 --reload"

# 2. Start Frontend
Write-Host "[2/2] Starting React Frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd vista/frontend; npm run dev"

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host " VISTA is launching in two separate terminal windows!" -ForegroundColor Yellow
Write-Host "   Backend API Docs: http://127.0.0.1:8002/docs" -ForegroundColor Yellow
Write-Host "   Frontend Web UI:  http://localhost:5173" -ForegroundColor Yellow
Write-Host "`n Demo Credentials:" -ForegroundColor White
Write-Host "   - Admin:   admin@vista.local   / admin123" -ForegroundColor White
Write-Host "   - Teacher: teacher@vista.local / teacher123" -ForegroundColor White
Write-Host "   - Student: 1da24ai403@vista.local / student123 (Mohammed Ayan)" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Cyan
