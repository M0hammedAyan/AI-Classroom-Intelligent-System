@echo off
title VISTA - AI Classroom Intelligent System
echo =====================================================================
echo  Starting VISTA Platform (Backend + Frontend)
echo  Exhibition: 7 Nov 2026
echo =====================================================================
echo.

:: Ensure Python virtual environment if present
if exist ".venv\Scripts\activate.bat" (
    echo [1/3] Activating virtual environment...
    call .venv\Scripts\activate.bat
)

:: Set exact database URL and ports
set VISTA_DB_URL=sqlite:///./vista_dev.db
set PORT=8002

echo [2/3] Launching FastAPI Backend on http://127.0.0.1:8002 ...
start "VISTA Backend (FastAPI :8002)" cmd /k "python -m uvicorn vista.backend.app.main:app --host 127.0.0.1 --port 8002 --reload"

echo [3/3] Launching React Frontend on http://localhost:5173 ...
cd vista\frontend
start "VISTA Frontend (Vite :5173)" cmd /k "npm run dev"
cd ..\..

echo.
echo =====================================================================
echo  VISTA is now launching!
echo  - Backend API:  http://127.0.0.1:8002
echo  - API Docs:     http://127.0.0.1:8002/docs
echo  - Frontend Web: http://localhost:5173
echo.
echo  Demo Credentials:
echo   - Admin:   admin@vista.local   / admin123
echo   - Teacher: teacher@vista.local / teacher123
echo   - Student: 1da24ai403@vista.local / student123 (Mohammed Ayan)
echo =====================================================================
pause
