@echo off
echo ============================================================
echo DASHBOARD DATA VERIFICATION
echo ============================================================
echo.

echo Step 1: Checking if backend is running...
curl -s http://localhost:8000/api/opportunities ^>nul 2^>^&1
if %errorlevel% == 0 (
    echo [OK] Backend is running
    echo.
    echo Step 2: Fetching opportunities from API...
    curl -s http://localhost:8000/api/opportunities
    echo.
    echo.
    echo ============================================================
    echo RESULT: Dashboard should be displaying opportunities!
    echo ============================================================
    echo.
    echo If you don't see opportunities on the dashboard:
    echo 1. Make sure frontend is running: cd frontend ^&^& npm run dev
    echo 2. Open browser: http://localhost:5173
    echo 3. Check browser console for errors (F12)
    echo.
) else (
    echo [ERROR] Backend is NOT running!
    echo.
    echo Please start the backend first:
    echo   cd backend
    echo   uvicorn app.main:app --reload
    echo.
    echo Then run this script again.
)

pause
