@echo off
echo Starting RAM Price Tracking System...

REM Start backend
start "Backend" cmd /k "uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment
timeout /t 5 /nobreak > nul

REM Start frontend
cd frontend
start "Frontend" cmd /k "npm run dev -- --host 0.0.0.0 --port 5173"

echo System started. Backend at http://localhost:8000, Frontend at http://localhost:5173
pause