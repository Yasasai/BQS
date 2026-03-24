@echo off
echo ============================================================
echo Triggering Immediate Oracle CRM Sync
echo ============================================================
echo.
echo Backend must be running on http://localhost:8000
echo.

powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/sync-database' -Method POST; Write-Host '✓ Sync triggered successfully!' -ForegroundColor Green; Write-Host ($response | ConvertTo-Json); } catch { Write-Host '✗ Error: Backend not running or sync failed' -ForegroundColor Red; Write-Host $_.Exception.Message; }"

echo.
echo ============================================================
echo Check backend console for sync progress
echo ============================================================
echo.
pause
