#!/bin/bash

echo "Stopping RAM Price Tracking System..."

# Stop backend
if [ -f backend.pid ]; then
    PID=$(cat backend.pid)
    kill $PID 2>/dev/null && echo "Backend stopped (PID: $PID)" || echo "Failed to stop backend"
    rm backend.pid
else
    echo "No backend PID file found"
fi

# Stop frontend
if [ -f frontend.pid ]; then
    PID=$(cat frontend.pid)
    kill $PID 2>/dev/null && echo "Frontend stopped (PID: $PID)" || echo "Failed to stop frontend"
    rm frontend.pid
else
    echo "No frontend PID file found"
fi

echo "System stopped."