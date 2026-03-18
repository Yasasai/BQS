@echo off
set PYTHONPATH=.
backend\venv\Scripts\python.exe -m pytest backend/tests/test_infrastructure.py
