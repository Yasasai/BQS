@echo off
echo ========================================
echo  Sync Workflow Status Script
echo ========================================
echo.
echo This will populate the workflow_status field
echo for all opportunities in the database.
echo.
echo This is needed for the Action Required dashboard
echo to show opportunities correctly.
echo.
pause

echo.
echo Running sync script...
cd backend
python sync_workflow_status.py

echo.
echo ========================================
echo  Sync Complete!
echo ========================================
echo.
echo Now refresh your browser:
echo   1. Go to: http://localhost:5176/practice-head/action-required
echo   2. Press: Ctrl + Shift + R
echo.
echo You should now see opportunities in the dashboard!
echo.
pause
