@echo off
TITLE BQS Cronjob Setup & Run
echo ==================================================
echo      BQS ORACLE FETCH & SYNC SYSTEM
echo ==================================================
echo.

echo [1/3] Checking environment...
cd ..\backend

if not exist ".env" (
    echo [WARNING] .env file not found! Using default example.
    echo Please update .env with real credentials if you haven't already.
    copy .env.example .env
)

echo.
echo [2/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/3] Starting Backend (Scheduler active)...
echo The backend will fetch from Oracle every 15 minutes.
echo Access the API at http://localhost:8000
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
