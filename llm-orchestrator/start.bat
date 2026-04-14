@echo off
REM Start both backend and frontend in dev mode (Windows).

echo === LLM Orchestrator ===

cd /d "%~dp0backend"
if not exist .env copy .env.example .env

echo [1/2] Starting FastAPI backend on :8000 ...
start "LLM-Backend" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Vite dev server on :5173 ...
cd /d "%~dp0frontend"
start "LLM-Frontend" cmd /c "npm run dev"

echo.
echo Backend:  http://localhost:8000/api/health
echo Frontend: http://localhost:5173
echo.
echo Close the spawned windows to stop.
pause
