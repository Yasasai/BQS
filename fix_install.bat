@echo off
echo ========================================
echo BQS Quick Fix - Manual Installation
echo ========================================
echo.

echo [1/3] Upgrading pip...
backend\venv\Scripts\python.exe -m pip install --upgrade pip

echo.
echo [2/3] Installing dependencies...
backend\venv\Scripts\pip.exe install -r backend\requirements.txt

echo.
echo [3/3] Verifying installation...
backend\venv\Scripts\python.exe -c "import psycopg2; import fastapi; import httpx; print('✓ All packages installed successfully!')"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next: Run the setup script again:
echo   python scripts\setup\setup_project.py --with-data
echo.
pause
