@echo off
title Football Manager Sim 25/26 - Setup
color 0a
cd /d "%~dp0"
cls
echo ================================================
echo     FOOTBALL MANAGER SIM 25/26 - SETUP
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during install
    echo Then run setup.bat again.
    echo.
    pause
    exit /b 1
)

echo Python found!
echo.
echo Installing required packages...
echo.

REM Install all required packages directly (no requirements.txt needed)
pip install flask --quiet
pip install flask-sqlalchemy --quiet
pip install flask-socketio --quiet
pip install eventlet --quiet
pip install python-dotenv --quiet

REM Also try requirements.txt if it exists
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
)

echo.
echo All packages installed!
echo.
echo Starting game...
echo Keep this window open while playing.
echo.
timeout /t 2 /nobreak >nul
python app.py
pause
