@echo off
setlocal

echo Starting Feynman Twin backend API on http://127.0.0.1:8000
start "Feynman Backend" cmd /k "cd /d %~dp0src && python -m uvicorn api_server:app --host 127.0.0.1 --port 8000"

echo Starting frontend static server on http://127.0.0.1:5173
start "Feynman Frontend" cmd /k "python -m http.server 5173 --directory \"%~dp0frontend\""

echo Both servers launched.
echo Open: http://127.0.0.1:5173

endlocal
