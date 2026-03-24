@echo off
TITLE BQS Phase 4.6 - Seed Only
color 0E
echo ================================================================
echo   BQS Phase 4.6 - Seed Opportunities (DB only, no server)
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/2] Seeding users (if not already present)...
backend\venv\Scripts\python backend\seed_users.py
echo.

echo [2/2] Seeding 30 opportunity records into PostgreSQL...
backend\venv\Scripts\python backend\phase46_seed.py
echo.

echo ================================================================
echo   Done! Now start the backend and frontend servers.
echo ================================================================
pause
