@echo off
title OmniSave Media Downloader
color 0b

echo ============================================================
echo         OmniSave Media Downloader - Starting Application
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and try again.
    pause
    exit /b 1
)

echo [2/3] Checking and installing dependencies...
python -m pip install -r requirements.txt --quiet

echo [3/3] Launching web server at http://127.0.0.1:5000 ...
start "" "http://127.0.0.1:5000"

python app.py
pause
