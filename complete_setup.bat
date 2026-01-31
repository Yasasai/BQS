@echo off
echo ========================================
echo  COMPLETE SETUP - Action Required Dashboard
echo ========================================
echo.
echo This script will:
echo   1. Check database status
echo   2. Sync opportunities if needed
echo   3. Start both servers
echo   4. Open dashboard
echo.
pause

echo.
echo ========================================
echo  STEP 1: Checking Database
echo ========================================
cd backend
python check_database.py

echo.
echo ========================================
echo  STEP 2: Do you want to sync from Oracle?
echo ========================================
echo.
set /p SYNC="Sync opportunities from Oracle CRM? (y/n): "
if /i "%SYNC%"=="y" (
    echo.
    echo Running sync...
    python sync_manager.py
    echo.
    echo Sync complete! Check the output above.
    pause
)

echo.
echo ========================================
echo  STEP 3: Starting Servers
echo ========================================
cd ..

echo Killing any existing processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo Starting Backend API...
start "BQS Backend API" cmd /k "cd backend && python -m uvicorn main:app --reload"
timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "BQS Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo  STEP 4: Opening Dashboard
echo ========================================
start http://localhost:5176/practice-head/action-required

echo.
echo ========================================
echo  IMPORTANT - DO THIS NOW:
echo ========================================
echo.
echo In your browser:
echo   1. Press F12 (open DevTools)
echo   2. Go to Console tab
echo   3. Look for these messages:
echo      - "🔍 Querying opportunities from database..."
echo      - "📊 Found X opportunities in database"
echo      - "✅ Returning X opportunities to frontend"
echo.
echo   4. Press Ctrl+Shift+R to hard refresh
echo.
echo You should see TWO colored cards:
echo   - Blue card (left): Unassigned opportunities
echo   - Red card (right): Submitted assessments
echo.
echo If cards are empty but console shows "Found X opportunities":
echo   - The data is there but filtering might be the issue
echo   - Check workflow_status values
echo.
pause
