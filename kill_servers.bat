@echo off
echo ================================================================
echo BQS SERVER CLEANUP
echo ================================================================
echo.
echo This will kill ALL Node.js and Python processes.
echo Use this if your ports (5173, 5175, 8000) are blocked.
echo.
echo WARNING: This will close any other Node/Python apps you are running.
echo.
set /p confirm="Are you sure? (y/n): "

if /i "%confirm%" neq "y" goto end

echo.
echo Killing Node.js processes (Frontend)...
taskkill /F /IM node.exe >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Node processes terminated.
) else (
    echo [INFO] No Node processes found.
)

echo.
echo Killing Python processes (Backend)...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python processes terminated.
) else (
    echo [INFO] No Python processes found.
)

echo.
echo ================================================================
echo Cleanup Complete. You can now restart servers.
echo ================================================================
echo.
pause

:end
exit
