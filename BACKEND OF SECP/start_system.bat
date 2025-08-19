@echo off
echo 🚀 Starting SECP Complaint Classification System
echo.

echo 📍 Starting Backend Server...
start cmd /k "cd /d "%~dp0" && .\.venv\Scripts\activate && uvicorn app.main:app --reload"

echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo 🌐 Starting Frontend Server...
cd frontend
python serve.py

pause
