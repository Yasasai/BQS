@echo off
echo ========================================================
echo   Manual Trigger: Oracle CRM -> PostgreSQL Sync
echo ========================================================
echo.
echo Sending request to Backend API...
echo.

:: Try using curl (standard on Windows 10/11)
curl -X POST http://localhost:8000/api/v1/sync-crm
if %ERRORLEVEL% EQU 0 goto success

:: Fallback to PowerShell if curl fails
echo.
echo Curl not found or failed, trying PowerShell...
powershell -Command "Invoke-RestMethod -Uri http://localhost:8000/api/v1/sync-crm -Method Post"

:success
echo.
echo.
echo ========================================================
echo   REQUEST SENT!
echo   Check your Backend Terminal Window for progress logs.
echo ========================================================
pause
