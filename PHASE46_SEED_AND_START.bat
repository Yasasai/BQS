@echo off
TITLE BQS Phase 4.6 - Seed + Start
color 0A
echo ================================================================
echo   BQS Phase 4.6 Hotfix - Populate DB + Start Backend
echo ================================================================
echo.

cd /d "%~dp0"

REM ── Step 1: Run the seed script ──────────────────────────────────
echo [1/3] Seeding opportunity data...
echo.
backend\venv\Scripts\python backend\phase46_seed.py
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARN] Seed script returned an error - check output above.
    echo        Continuing to start the server anyway...
)
echo.

REM ── Step 2: Run users seed if needed ─────────────────────────────
echo [2/3] Ensuring users are seeded...
backend\venv\Scripts\python backend\seed_users.py
echo.

REM ── Step 3: Start backend server ─────────────────────────────────
echo [3/3] Starting FastAPI backend on http://localhost:8000 ...
echo        Swagger UI: http://localhost:8000/docs
echo        Press Ctrl+C to stop.
echo.
cd backend
venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
