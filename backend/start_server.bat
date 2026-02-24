@echo off
echo ============================================================
echo Starting BQS Backend Server
echo ============================================================
echo.

REM Navigate to the backend directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run uvicorn with the correct module path
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
