#!/bin/bash

echo "Starting RAM Price Tracking System..."

# Start backend in background
nohup uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
echo $! > backend.pid

# Wait a moment
sleep 5

# Start frontend in background
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &
echo $! > ../frontend.pid

echo "System started. Backend at http://localhost:8000, Frontend at http://localhost:5173"
echo "PID files: backend.pid, frontend.pid"