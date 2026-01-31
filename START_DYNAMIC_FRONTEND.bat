@echo off
echo ============================================
echo   STARTING DYNAMIC FRONTEND SYSTEM
echo ============================================
echo.
echo This will start:
echo   - Backend on port 8000
echo   - Frontend on port 5176
echo.
echo Press Ctrl+C in each window to stop
echo.
pause

echo.
echo Starting Backend Server...
start "BQS Backend (Port 8000)" cmd /k "cd backend && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "BQS Frontend (Port 5176)" cmd /k "cd frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo   SERVERS STARTED
echo ============================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5176
echo.
echo Opening frontend in browser...
start http://localhost:5176/practice-head/action-required
echo.
echo ============================================
echo   TEST THE ASSIGNMENT FLOW
echo ============================================
echo.
echo 1. You should see the Practice Head Dashboard
echo 2. Look for "Assign to Solution Architect" card
echo 3. Click "Assign" on any unassigned opportunity
echo 4. Select an SA from dropdown
echo 5. Click "Confirm Allocation"
echo 6. Watch the opportunity move INSTANTLY to "Assigned" tab
echo 7. NO PAGE REFRESH NEEDED!
echo.
echo ============================================
pause
