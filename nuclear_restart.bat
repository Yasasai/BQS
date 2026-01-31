@echo off
echo ========================================
echo  NUCLEAR OPTION - Complete Clean Restart
echo ========================================
echo.
echo This will:
echo 1. Kill all Node processes
echo 2. Delete Vite cache
echo 3. Restart dev server
echo.
pause

echo.
echo [Step 1/4] Killing all Node processes...
taskkill /F /IM node.exe 2>nul
if %errorlevel%==0 (
    echo ✓ Node processes killed
) else (
    echo ℹ No Node processes running
)

echo.
echo [Step 2/4] Deleting Vite cache...
cd frontend
if exist ".vite" (
    rmdir /s /q .vite
    echo ✓ Vite cache deleted
) else (
    echo ℹ No Vite cache found
)

if exist "dist" (
    rmdir /s /q dist
    echo ✓ Dist folder deleted
) else (
    echo ℹ No dist folder found
)

echo.
echo [Step 3/4] Starting dev server...
echo Please wait...
start "BQS Frontend Dev Server" cmd /k "npm run dev"

echo.
echo [Step 4/4] Waiting for server to start...
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo  Opening browser...
echo ========================================
start http://localhost:5176/practice-head/action-required

echo.
echo ========================================
echo  IMPORTANT - DO THIS NOW:
echo ========================================
echo.
echo 1. Wait for the browser to open
echo 2. Press F12 to open DevTools
echo 3. Right-click the refresh button
echo 4. Select "Empty Cache and Hard Reload"
echo.
echo OR just press: Ctrl + Shift + R
echo.
echo You should see TWO colored cards:
echo   - Blue card: "1. Assign to Solution Architect"
echo   - Red card: "2. Review & Approve/Reject"
echo.
pause
