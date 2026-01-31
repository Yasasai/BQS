@echo off
echo ============================================
echo   DYNAMIC FRONTEND - VERIFICATION SCRIPT
echo ============================================
echo.

echo [1/3] Checking if Backend is running on port 8000...
curl -s http://127.0.0.1:8000/api/opportunities/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is RUNNING on port 8000
) else (
    echo ❌ Backend is NOT running
    echo.
    echo To start backend:
    echo   cd backend
    echo   uvicorn app.main:app --reload --port 8000
)

echo.
echo [2/3] Checking if Frontend is running on port 5176...
curl -s http://localhost:5176 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is RUNNING on port 5176
) else (
    echo ❌ Frontend is NOT running
    echo.
    echo To start frontend:
    echo   cd frontend
    echo   npm run dev
)

echo.
echo [3/3] Testing Backend API...
curl -s http://127.0.0.1:8000/api/opportunities/ -o temp_response.json 2>nul
if exist temp_response.json (
    echo ✅ Backend API is responding
    for %%A in (temp_response.json) do set size=%%~zA
    if !size! gtr 10 (
        echo ✅ Backend returned data
    ) else (
        echo ⚠️ Backend returned empty response
    )
    del temp_response.json >nul 2>&1
) else (
    echo ❌ Backend API is not responding
)

echo.
echo ============================================
echo   NEXT STEPS
echo ============================================
echo.
echo 1. Make sure both servers are running
echo 2. Open: http://localhost:5176/practice-head/action-required
echo 3. Test assignment flow:
echo    - Click "Assign" on unassigned opportunity
echo    - Select an SA
echo    - Click "Confirm Allocation"
echo    - Watch opportunity move instantly!
echo.
echo ============================================
pause
