@echo off
cd /d "c:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\scripts"
"..\backend\venv\Scripts\python.exe" check_sync_status.py > verification.log 2>&1
"..\backend\venv\Scripts\python.exe" enhanced_oracle_sync.py >> verification.log 2>&1
"..\backend\venv\Scripts\python.exe" check_sync_status.py >> verification.log 2>&1
echo Done >> verification.log
