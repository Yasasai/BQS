@echo off
echo Setting up BQS Environment...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo Installing/Updating dependencies...
.\venv\Scripts\python -m pip install --upgrade pip
.\venv\Scripts\pip install -r requirements.txt
echo Environment Setup Complete.
pause
