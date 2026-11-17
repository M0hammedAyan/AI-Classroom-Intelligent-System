# VISTA - Startup Script (PowerShell)
# Starts Backend (:8002) and Frontend (:5173) in separate windows.
# Works from any current directory; the backend runs on the project .venv.

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Starting VISTA Platform (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

# Project virtual environment (has cv2, insightface, onnxruntime, torch, ...)
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "ERROR: virtual environment not found at $py" -ForegroundColor Red
    Write-Host "Create it and install dependencies:" -ForegroundColor Red
    Write-Host "  python -m venv .venv" -ForegroundColor Red
    Write-Host "  .\.venv\Scripts\python.exe -m pip install -r vista\requirements.txt" -ForegroundColor Red
    exit 1
}

# Set database environment variable to guaranteed synchronized database
$env:VISTA_DB_URL = "sqlite:///$($PSScriptRoot -replace '\\','/')/vista/backend/vista_dev.db"

# Face classifier: v3 (29 classes). Absolute path, because personal_classifier.py
# resolves relative paths against the current working directory.
# Rollback: point to training_results\best_model_npz_splitB.pth
$env:VISTA_FACE_MODEL = Join-Path $PSScriptRoot "training_results\expanded_v3\best_model_expanded_v3_splitB.pth"
$env:VISTA_FACE_MODEL_THRESHOLD = "0.60"
if (-not (Test-Path $env:VISTA_FACE_MODEL)) {
    Write-Host "WARNING: face model not found at $($env:VISTA_FACE_MODEL); face recognition will not work." -ForegroundColor Yellow
}

# Skip a service whose port is already in use instead of starting a second copy
function Test-PortInUse([int]$Port) {
    return [bool](Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

# 1. Start Backend (working directory = project root so vista.backend... resolves)
if (Test-PortInUse 8002) {
    Write-Host "[1/2] Port 8002 already in use - backend not started." -ForegroundColor Yellow
} else {
    Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8002 ..." -ForegroundColor Green
    Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList "-NoExit", "-Command", "& '$py' -m uvicorn vista.backend.app.main:app --host 127.0.0.1 --port 8002 --reload"
}

# 2. Start Frontend
if (Test-PortInUse 5173) {
    Write-Host "[2/2] Port 5173 already in use - frontend not started." -ForegroundColor Yellow
} else {
    Write-Host "[2/2] Starting React Frontend on http://localhost:5173 ..." -ForegroundColor Green
    Start-Process powershell -WorkingDirectory (Join-Path $PSScriptRoot "vista\frontend") -ArgumentList "-NoExit", "-Command", "npm run dev"
}

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host " VISTA is launching in two separate terminal windows!" -ForegroundColor Yellow
Write-Host "   Backend API Docs: http://127.0.0.1:8002/docs" -ForegroundColor Yellow
Write-Host "   Frontend Web UI:  http://localhost:5173" -ForegroundColor Yellow
Write-Host "`n Demo Credentials:" -ForegroundColor White
Write-Host "   - Admin:   admin@vista.local   / admin123" -ForegroundColor White
Write-Host "   - Teacher: teacher@vista.local / teacher123" -ForegroundColor White
Write-Host "   - Student: <usn in lowercase>@vista.local / student123" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Cyan
