@echo off
echo Running database migration...
echo.

set PGPASSWORD=Yasasvi@2005

"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d bqs -c "ALTER TABLE opportunity ADD COLUMN IF NOT EXISTS workflow_status VARCHAR(50);"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to add workflow_status column
    pause
    exit /b 1
)

"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d bqs -c "ALTER TABLE opportunity ADD COLUMN IF NOT EXISTS assigned_sa VARCHAR(255);"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to add assigned_sa column
    pause
    exit /b 1
)

"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d bqs -c "UPDATE opportunity SET workflow_status = 'NEW' WHERE workflow_status IS NULL;"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to update default values
    pause
    exit /b 1
)

echo.
echo ✓ Migration completed successfully!
echo   - Added workflow_status column
echo   - Added assigned_sa column  
echo   - Set default status to 'NEW'
echo.
pause
