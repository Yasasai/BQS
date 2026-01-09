@echo off
cd backend
call venv\Scripts\activate.bat
python sync_manager.py
pause
