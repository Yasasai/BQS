@echo off
echo ============================================================
echo BQS Backend - Oracle CRM Sync System
echo ============================================================
echo.

echo [1/3] Checking Python dependencies...
python -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [2/3] Starting FastAPI Backend Server...
echo.
echo ============================================================
echo Server will start on: http://localhost:8000
echo API Docs available at: http://localhost:8000/docs
echo.
echo Oracle Sync Schedule: Daily at midnight (00:00)
echo Manual sync: POST http://localhost:8000/api/sync-database
echo Sync status: GET http://localhost:8000/api/sync-status
echo ============================================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
