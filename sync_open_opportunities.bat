@echo off
echo ========================================
echo  Sync OPEN Opportunities from Oracle
echo ========================================
echo.
echo This will:
echo 1. Use the updated sync script
echo 2. Fetch OPEN opportunities from Oracle CRM
echo 3. Save them to your database
echo.
echo URL: https://eijs-test.fa.em2.oraclecloud.com/crmRestApi/resources/11.12.1.0/opportunities
echo Filter: StatusCode='OPEN'
echo.
pause

echo.
echo Running sync...
cd backend
python sync_manager.py

echo.
echo ========================================
echo  Sync Complete!
echo ========================================
echo.
echo Check the output above to see how many opportunities were saved.
echo.
echo If you see "Total Saved: 0", it means:
echo   - No OPEN opportunities exist in Oracle CRM, OR
echo   - Your user doesn't have permission to see them
echo.
echo If you see "Total Saved: X" (where X > 0):
echo   - Success! Opportunities are now in your database
echo   - Refresh your browser to see them in the dashboard
echo.
pause
