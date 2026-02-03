@echo off
echo ========================================
echo  Restarting Frontend Dev Server
echo ========================================
echo.

REM Kill any existing node processes on port 5176
echo Stopping any existing dev server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5176') do (
    echo Killing process %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo Starting frontend dev server...
cd frontend
start "BQS Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo  Dev server is starting...
echo ========================================
echo.
echo Wait for the server to start (usually 5-10 seconds)
echo Then the browser will open automatically to:
echo http://localhost:5176/practice-head/action-required
echo.
echo Press any key to open the browser...
pause >nul

REM Wait a bit more to ensure server is ready
timeout /t 3 /nobreak >nul

REM Open the browser
start http://localhost:5176/practice-head/action-required

echo.
echo ========================================
echo  IMPORTANT: Hard Refresh!
echo ========================================
echo.
echo In your browser, press: Ctrl + Shift + R
echo This will clear the cache and load the new code.
echo.
echo You should see TWO colored cards:
echo   - Blue card: "1. Assign to Solution Architect"
echo   - Red card: "2. Review & Approve/Reject"
echo.
pause
