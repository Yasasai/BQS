@echo off
set PGPASSWORD=admin
set PG17="C:\Program Files\PostgreSQL\17\bin\pg_restore"
%PG17% -h localhost -p 5432 -U postgres -d bqs --clean --if-exists -v "c:\Coding\BQS\DB_Backup\BQS.sql"
echo Exit code: %ERRORLEVEL%
