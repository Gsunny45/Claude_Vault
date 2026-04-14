#!/bin/bash
# Start both backend and frontend in development mode.
# Prerequisites: Python 3.11+, Node 18+, pip deps installed.

set -e

echo "=== LLM Orchestrator ==="

# Backend
echo "[1/2] Starting FastAPI backend on :8000 ..."
cd "$(dirname "$0")/backend"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  -> Created .env from .env.example — add your API keys!"
fi
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Frontend
echo "[2/2] Starting Vite dev server on :5173 ..."
cd "$(dirname "$0")/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000/api/health"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
