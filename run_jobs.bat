@echo off
echo Starting Jobs... > job_log.txt
echo Running Sync Manager... >> job_log.txt
python backend/sync_manager.py >> job_log.txt 2>&1
echo. >> job_log.txt
echo Sync Manager Finished. >> job_log.txt
echo. >> job_log.txt
echo Running Status Check... >> job_log.txt
python read_sync_status.py >> job_log.txt 2>&1
echo Done. >> job_log.txt
