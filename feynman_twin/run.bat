@echo off
REM Feynman Digital Twin - Windows Launcher

cd /d "%~dp0"

if "%1"=="setup" (
    echo.
    echo Setting up Feynman Digital Twin...
    echo.
    python setup.py setup
) else if "%1"=="quickstart" (
    python setup.py quickstart
) else if "%1"=="chat" (
    cd src
    python main.py
) else if "%1"=="query" (
    if "%2"=="" (
        echo Usage: run.bat query "Your question here"
    ) else (
        cd src
        python main.py --query %2
    )
) else (
    echo.
    echo Feynman Digital Twin - Windows Launcher
    echo.
    echo Usage:
    echo   run.bat setup       - First time setup
    echo   run.bat quickstart  - Show quick start guide
    echo   run.bat chat        - Start interactive chat
    echo   run.bat query "Q"   - Ask a single question
    echo.
)
