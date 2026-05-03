#!/bin/bash

# MindDock - Start/Stop Script
# Usage: ./start.sh        Start frontend and backend
#        ./start.sh stop   Stop frontend and backend

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIDS_FILE="$ROOT_DIR/.pids"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_LOG="$ROOT_DIR/frontend.log"
BACKEND_LOG="$ROOT_DIR/backend.log"

stop_services() {
    if [ -f "$PIDS_FILE" ]; then
        while IFS='=' read -r name pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null
                echo "Stopped $name (PID: $pid)"
            else
                echo "$name (PID: $pid) was not running"
            fi
        done < "$PIDS_FILE"
        rm -f "$PIDS_FILE"
    else
        echo "No .pids file found. Checking ports..."
        lsof -ti:5173 | xargs kill 2>/dev/null && echo "Stopped process on port 5173"
        lsof -ti:8000 | xargs kill 2>/dev/null && echo "Stopped process on port 8000"
    fi
    echo "All services stopped."
}

status_services() {
    if [ ! -f "$PIDS_FILE" ]; then
        echo "MindDock services are not running."
        return
    fi

    while IFS='=' read -r name pid; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "$name running (PID: $pid)"
        else
            echo "$name not running (stale PID: $pid)"
        fi
    done < "$PIDS_FILE"
}

start_services() {
    # Check if already running
    if [ -f "$PIDS_FILE" ]; then
        echo "Services may already be running. Run './start.sh stop' first."
        exit 1
    fi

    # Check prerequisites
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo "Installing frontend dependencies..."
        (cd "$FRONTEND_DIR" && npm install)
    fi

    if [ ! -d "$BACKEND_DIR/.venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv "$BACKEND_DIR/.venv"
    fi
    echo "Installing backend dependencies..."
    "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"

    # Start backend
    echo "Starting backend (port 8000)..."
    cd "$BACKEND_DIR"
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    cd "$ROOT_DIR"

    # Start frontend
    echo "Starting frontend (port 5173)..."
    cd "$FRONTEND_DIR"
    npx vite --host 127.0.0.1 --port 5173 > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    cd "$ROOT_DIR"

    # Save PIDs
    echo "frontend=$FRONTEND_PID" > "$PIDS_FILE"
    echo "backend=$BACKEND_PID" >> "$PIDS_FILE"

    # Wait for services to start
    sleep 3

    # Verify
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "  Backend running at http://localhost:8000 (PID: $BACKEND_PID)"
        echo "  API docs at http://localhost:8000/docs"
    else
        echo "  Backend failed to start. Check $BACKEND_LOG"
    fi

    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "  Frontend running at http://localhost:5173 (PID: $FRONTEND_PID)"
    else
        echo "  Frontend failed to start. Check $FRONTEND_LOG"
    fi

    echo ""
    echo "MindDock is running! Open http://localhost:5173"
    echo "To stop: ./start.sh stop"
}

case "${1:-start}" in
    stop)
        stop_services
        ;;
    status)
        status_services
        ;;
    start|"")
        start_services
        ;;
    *)
        echo "Usage: ./start.sh [start|stop|status]"
        exit 1
        ;;
esac
