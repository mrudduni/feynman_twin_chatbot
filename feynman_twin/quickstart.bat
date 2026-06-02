@echo off
REM Feynman Digital Twin - Quick Start on Windows
REM This batch file makes it easy to use the system

setlocal enabledelayedexpansion

cd /d "%~dp0"

if "%1"=="" (
    call :show_menu
) else (
    call :%1 %2 %3 %4 %5
    if errorlevel 1 (
        echo Unknown command: %1
        call :show_menu
    )
)

goto :eof

:show_menu
    cls
    echo.
    echo ================================================================================
    echo             FEYNMAN DIGITAL TWIN - Quick Start Menu
    echo ================================================================================
    echo.
    echo Commands:
    echo   quickstart.bat setup     - First-time setup (install + configure)
    echo   quickstart.bat chat      - Start interactive conversation
    echo   quickstart.bat query "Q" - Ask a single question
    echo   quickstart.bat demo      - Run demo (no API key needed)
    echo   quickstart.bat collect   - Collect data and build embeddings
    echo.
    echo Examples:
    echo   quickstart.bat query "What is the Feynman Technique?"
    echo   quickstart.bat chat
    echo.
    echo ================================================================================
    echo.
    goto :eof

:setup
    echo.
    echo [1] Setting up Feynman Digital Twin...
    echo.
    python setup.py setup
    if errorlevel 1 (
        echo Setup failed. Please check the error above.
        pause
        exit /b 1
    )
    echo.
    echo Next steps:
    echo   1. cd src
    echo   2. python main.py --setup   (collect data, takes 5-10 min)
    echo   3. python main.py           (start chatting)
    echo.
    pause
    goto :eof

:chat
    echo.
    echo Starting Feynman Digital Twin...
    echo.
    cd src
    python main.py
    cd ..
    goto :eof

:query
    if "%2"=="" (
        echo Usage: quickstart.bat query "Your question here"
        exit /b 1
    )
    echo.
    echo Question: %2
    echo.
    cd src
    python main.py --query "%2"
    cd ..
    goto :eof

:demo
    echo.
    echo Running Feynman Digital Twin Demos...
    echo (No API key required for most demos)
    echo.
    python demo.py --all
    pause
    goto :eof

:collect
    echo.
    echo Collecting data and building embeddings...
    echo This will take 5-10 minutes.
    echo.
    cd src
    python main.py --setup
    cd ..
    goto :eof

:error
    echo Unknown command
    call :show_menu
    exit /b 1
