@echo off
echo Running BQS No-Safety Snapshot...
del /F /Q .gitignore 2>nul
del /F /Q "backend\debug_init_db.py" "backend\check_db.py" "backend\check_tables.py" "backend\migrate_db.py" "backend\test_minimal.py" 2>nul
git add -A
git commit -m "BQS Full Snapshot: Code, Cache, and Environment"
git push origin main
echo Done.
pause
