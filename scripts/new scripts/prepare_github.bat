@echo off
echo ========================================
echo BQS - GitHub Push Preparation
echo ========================================
echo.

echo [1/4] Cleaning up test files...
del /Q test_oracle_permissions.py 2>nul
del /Q test_oracle_data.py 2>nul
del /Q direct_api_test.py 2>nul
del /Q diagnose_sync.py 2>nul
del /Q quick_verify_fix.py 2>nul
del /Q find_oracle_url.py 2>nul
del /Q fetch_all_methods.py 2>nul
del /Q extract_names.py 2>nul
del /Q api_test.txt 2>nul
del /Q sync_output*.txt 2>nul
del /Q oracle_api_config.txt 2>nul
del /Q opportunity_names.txt 2>nul
del /Q fetched_opportunities.json 2>nul
echo    Done!

echo.
echo [2/4] Checking for hardcoded credentials...
findstr /s /i "Welcome@123" *.py >nul 2>&1
if %errorlevel%==0 (
    echo    WARNING: Found hardcoded passwords! Check files manually.
    findstr /s /i /n "Welcome@123" *.py
) else (
    echo    OK - No hardcoded passwords found
)

echo.
echo [3/4] Verifying .env is in .gitignore...
findstr /i "^\.env$" .gitignore >nul 2>&1
if %errorlevel%==0 (
    echo    OK - .env is excluded from git
) else (
    echo    WARNING: .env might not be in .gitignore!
)

echo.
echo [4/4] Git status check...
git status --short

echo.
echo ========================================
echo Ready for GitHub Push!
echo ========================================
echo.
echo Next steps:
echo 1. Review the changes above
echo 2. Run: git add .
echo 3. Run: git commit -m "feat: Complete Oracle CRM sync system"
echo 4. Run: git push origin main
echo.
pause
