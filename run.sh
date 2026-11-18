#!/usr/bin/env bash

# Trekking Management Application - V2
# Startup script

set -e

# Activate or create virtual environment
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating .venv and installing requirements..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Check if frontend build exists, build if missing and npm is available
if [ ! -d "frontend/dist" ]; then
    echo "Frontend build not found. Building frontend..."
    if command -v npm >/dev/null 2>&1; then
        (cd frontend && npm install && npm run build)
    else
        echo "Warning: npm not found. If UI is missing, run 'cd frontend && npm install && npm run build'."
    fi
fi

# Ensure redis is running
if ! redis-cli ping >/dev/null 2>&1; then
    echo "Starting Redis..."
    redis-server --daemonize yes 2>/dev/null || true
fi

# Start celery worker in background
echo "Starting Celery worker..."
cd backend
celery -A celery_worker worker --loglevel=info --detach 2>/dev/null || true

# Start Flask server
echo "Starting Flask server on http://127.0.0.1:5001"
python3 run.py
