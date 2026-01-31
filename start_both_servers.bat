@echo off
echo ========================================
echo  BQS - Start Both Frontend and Backend
echo ========================================
echo.
echo This will start:
echo   1. Backend API (port 8000)
echo   2. Frontend Dev Server (port 5176)
echo.
echo Both will run simultaneously in separate windows.
echo.
pause

echo.
echo [1/3] Starting Backend API...
start "BQS Backend API" cmd /k "cd backend && python -m uvicorn main:app --reload"

echo Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak >nul

echo.
echo [2/3] Starting Frontend Dev Server...
start "BQS Frontend" cmd /k "cd frontend && npm run dev"

echo Waiting 5 seconds for frontend to compile...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Opening browser...
start http://localhost:5176/practice-head/action-required

echo.
echo ========================================
echo  Both servers are starting!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:5176
echo.
echo You should see TWO terminal windows:
echo   - "BQS Backend API" (Python/FastAPI)
echo   - "BQS Frontend" (Vite dev server)
echo.
echo IMPORTANT: Press Ctrl+Shift+R in browser to hard refresh!
echo.
echo If you don't see opportunities, run:
echo   run_sync_script.bat
echo.
pause
