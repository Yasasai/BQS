# Quick Diagnostic Script

## Run this to verify everything:

```bash
@echo off
echo ========================================
echo  BQS Action Required - Diagnostic Check
echo ========================================
echo.

echo [1/5] Checking if code changes exist...
findstr /C:"action-required" frontend\src\pages\PracticeHeadDashboard.tsx >nul 2>&1
if %errorlevel%==0 (
    echo ✓ action-required code found
) else (
    echo ✗ action-required code NOT found
)

findstr /C:"#1976D2" frontend\src\pages\PracticeHeadDashboard.tsx >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Oracle Blue color found
) else (
    echo ✗ Oracle Blue color NOT found
)

findstr /C:"Action Required" frontend\src\components\RoleSidebar.tsx >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Sidebar menu item found
) else (
    echo ✗ Sidebar menu item NOT found
)

echo.
echo [2/5] Checking dev server...
netstat -ano | findstr :5176 >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Dev server running on port 5176
) else (
    echo ✗ Dev server NOT running on port 5176
    echo   Run: cd frontend && npm run dev
)

echo.
echo [3/5] Checking node_modules...
if exist "frontend\node_modules\" (
    echo ✓ node_modules exists
) else (
    echo ✗ node_modules NOT found
    echo   Run: cd frontend && npm install
)

echo.
echo [4/5] File locations:
echo   PracticeHeadDashboard.tsx: frontend\src\pages\PracticeHeadDashboard.tsx
echo   RoleSidebar.tsx: frontend\src\components\RoleSidebar.tsx
echo   App.tsx: frontend\src\App.tsx

echo.
echo [5/5] Next steps:
echo   1. Make sure dev server is running (cd frontend && npm run dev)
echo   2. Open browser to: http://localhost:5176/practice-head/action-required
echo   3. Press Ctrl+Shift+R to hard refresh
echo.
echo ========================================
pause
```

Save this as `diagnostic_check.bat` and run it!
