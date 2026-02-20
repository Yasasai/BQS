@echo off
echo ================================================================
echo BQS DASHBOARD - FIXED STARTUP SCRIPT
echo ================================================================
echo.

:menu
echo.
echo What would you like to do?
echo.
echo 1. Start Backend Server (FIXED)
echo 2. Start Frontend Server
echo 3. Check if Opportunities are Available
echo 4. Sync Opportunities from Oracle CRM
echo 5. Start BOTH Backend and Frontend (RECOMMENDED)
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto check
if "%choice%"=="4" goto sync
if "%choice%"=="5" goto both
if "%choice%"=="6" goto end
echo Invalid choice. Please try again.
goto menu

:backend
echo.
echo ================================================================
echo Starting Backend Server...
echo ================================================================
echo.
cd backend
echo Backend will start on: http://localhost:8000
echo API Endpoint: http://localhost:8000/api/opportunities
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
start cmd /k "title BQS Backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo.
echo Backend started in new window!
echo.
cd..
pause
goto menu

:frontend
echo.
echo ================================================================
echo Starting Frontend Server...
echo ================================================================
echo.
cd frontend
echo Frontend will start on: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.
start cmd /k "title BQS Frontend && npm run dev"
echo.
echo Frontend started in new window!
echo Open your browser to: http://localhost:5173
echo.
cd..
pause
goto menu

:check
echo.
echo ================================================================
echo Checking Opportunities Availability...
echo ================================================================
echo.
echo Testing API endpoint...
timeout /t 2 >nul
curl -s http://localhost:8000/api/opportunities >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Backend is running!
    echo.
    echo Fetching opportunities...
    curl -s http://localhost:8000/api/opportunities
    echo.
    echo.
    echo ================================================================
    echo If you see data above, opportunities are available!
    echo Open dashboard at: http://localhost:5173
    echo ================================================================
) else (
    echo [ERROR] Backend is NOT running!
    echo.
    echo Please start the backend first (Option 1)
)
echo.
pause
goto menu

:sync
echo.
echo ================================================================
echo Syncing Opportunities from Oracle CRM...
echo ================================================================
echo.
echo This will fetch opportunities from Oracle and save to database
echo.
python batch_sync_with_offset.py
echo.
echo ================================================================
echo Sync complete!
echo ================================================================
echo.
pause
goto menu

:both
echo.
echo ================================================================
echo Starting Backend and Frontend...
echo ================================================================
echo.
echo Starting Backend Server...
cd backend
start cmd /k "title BQS Backend && echo Starting Backend... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 >nul
echo Backend started!
echo.
echo Starting Frontend Server...
cd..
cd frontend
start cmd /k "title BQS Frontend && echo Starting Frontend... && npm run dev"
echo Frontend started!
echo.
cd..
echo ================================================================
echo Both servers are starting in separate windows!
echo ================================================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Wait 10-15 seconds for servers to start, then open:
echo http://localhost:5173
echo.
pause
goto menu

:end
echo.
echo Goodbye!
echo.
exit
