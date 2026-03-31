@echo off
REM Start FastAPI Backend
REM This script activates the venv and starts the backend
cd /d D:\Devops_project\backend
call venv\Scripts\activate.bat
uvicorn app.main:app --reload --port 8000
pause
