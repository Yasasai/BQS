@echo off
echo ============================================================
echo Manual Oracle CRM Sync
echo ============================================================
echo.
echo This will sync data from Oracle CRM to PostgreSQL
echo.
pause

cd backend
python sync_manager.py

echo.
echo ============================================================
echo Sync Complete!
echo ============================================================
pause
