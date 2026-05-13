#!/bin/bash

ROOT="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  echo ""
  echo "Stopping servers..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
  exit 0
}

trap cleanup INT TERM

# Backend
echo "Starting backend..."
cd "$ROOT/backend"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Frontend
echo "Starting frontend..."
cd "$ROOT/frontend"
npm start &
FRONTEND_PID=$!

echo ""
echo "Backend : http://127.0.0.1:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers."

wait
