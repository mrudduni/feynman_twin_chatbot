@echo off
REM Feynman Digital Twin - Start All Servers
REM This script starts both backend and frontend servers

echo ========================================
echo  Feynman Digital Twin - Starting...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".virtual\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python setup.py setup
    pause
    exit /b 1
)

echo [1/2] Starting Backend API Server (Port 8000)...
start "Feynman Backend" cmd /k "cd feynman_twin\src && ..\..\..virtual\Scripts\python.exe -m uvicorn api_server:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server (Port 5173)...
start "Feynman Frontend" cmd /k "cd feynman_twin\frontend && python -m http.server 5173"

timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo  Servers Started Successfully!
echo ========================================
echo.
echo Frontend: http://127.0.0.1:5173
echo Backend:  http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Memory:   http://127.0.0.1:5173/memory.html
echo.
echo Press any key to open the frontend in your browser...
pause > nul

start http://127.0.0.1:5173

echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
