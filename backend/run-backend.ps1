# Start FastAPI Backend
# This script activates the venv and starts the backend
cd D:\Devops_project\backend
.\venv\Scripts\Activate.ps1
python.exe -m uvicorn app.main:app --reload --port 8000
