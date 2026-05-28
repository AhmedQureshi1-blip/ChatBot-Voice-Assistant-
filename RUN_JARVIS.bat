REM Quick Start Jarvis with Ollama
REM This batch file handles starting Ollama and Jarvis properly

@echo off
setlocal enabledelayedexpansion

echo ========================================
echo JARVIS VOICE ASSISTANT - QUICK START
echo ========================================
echo.

REM Check if in correct directory
if not exist "jarvis.py" (
    echo Error: jarvis.py not found
    echo Please run this from: C:\Users\Humaira Kaleem\Desktop\Voice Assistant\Python-Voice-Assistant
    pause
    exit /b 1
)

REM Step 1: Check Ollama
echo [1/3] Checking Ollama...
python check_ollama.py
if !errorlevel! equ 0 (
    echo Ollama is ready
) else (
    echo.
    echo WARNING: Ollama not running
    echo Jarvis will work in OFFLINE mode only
    echo.
    echo To enable Ollama, open a NEW PowerShell window and run:
    echo   ^& "C:\Users\Humaira Kaleem\AppData\Local\Programs\Ollama\ollama.exe" serve
    echo.
    timeout /t 3
)

echo.
echo [2/3] Setting up environment...
set OPENAI_API_KEY=
set JARVIS_DEBUG=0

echo [3/3] Starting Jarvis...
echo.
echo Type 'help' for commands or just ask a question
echo Type 'quit' to exit
echo.

.\.venv\Scripts\python.exe jarvis.py

pause
