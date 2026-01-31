@echo off
echo ========================================
echo  FORCE COMPLETE REFRESH
echo ========================================
echo.
echo This will:
echo 1. Kill all Node processes
echo 2. Delete ALL caches (.vite, dist, node_modules/.vite)
echo 3. Restart dev server
echo 4. Force browser refresh
echo.
pause

echo.
echo [1/6] Killing all Node processes...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/6] Deleting Vite cache...
cd frontend
if exist ".vite" (
    rmdir /s /q .vite
    echo ✓ .vite deleted
)
if exist "dist" (
    rmdir /s /q dist
    echo ✓ dist deleted
)
if exist "node_modules\.vite" (
    rmdir /s /q node_modules\.vite
    echo ✓ node_modules\.vite deleted
)

echo.
echo [3/6] Deleting browser cache instruction...
echo When browser opens, you MUST:
echo   1. Press F12
echo   2. Right-click refresh button
echo   3. Select "Empty Cache and Hard Reload"
echo.
pause

echo.
echo [4/6] Starting dev server...
start "BQS Frontend" cmd /k "npm run dev"

echo.
echo [5/6] Waiting for server to start...
timeout /t 10 /nobreak

echo.
echo [6/6] Opening browser...
start http://localhost:5176/practice-head/action-required

echo.
echo ========================================
echo  NOW DO THIS IN THE BROWSER:
echo ========================================
echo.
echo 1. Press F12 (opens DevTools)
echo 2. Right-click the refresh button
echo 3. Select "Empty Cache and Hard Reload"
echo.
echo OR
echo.
echo 1. Press Ctrl + Shift + Delete
echo 2. Select "Cached images and files"
echo 3. Click "Clear data"
echo 4. Then press Ctrl + Shift + R
echo.
echo You MUST see TWO colored boxes:
echo   - Blue box on left
echo   - Red box on right
echo.
pause
