@echo off
setlocal enabledelayedexpansion
title Game Launcher
color 0A

echo ========================================================
echo                 GAME SETUP AND LAUNCHER
echo ========================================================
echo.

:: Step 1: Check Python
echo [1/5] Checking for Python...

set PYTHON_CMD=
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=py
    )
)

if "!PYTHON_CMD!"=="" (
    echo Python is not installed or not in PATH.
    echo Downloading Python 3.11 directly from python.org...
    curl -# -o python_installer.exe https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    if !errorlevel! neq 0 (
        echo.
        echo ERROR: Failed to download the Python installer. Check your internet connection.
        pause
        exit /b 1
    )
    
    echo Installing Python silently ^(this may take a few minutes^)...
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1
    
    if !errorlevel! neq 0 (
        echo.
        echo ERROR: Python installation failed.
        pause
        exit /b 1
    )
    
    echo Python installed successfully.
    del python_installer.exe
    
    echo Note: Windows environment variables need to refresh.
    echo Trying typical installation paths...
    
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311\Scripts\;%LOCALAPPDATA%\Programs\Python\Python311\;!PATH!"
    
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=python
    ) else (
        py --version >nul 2>&1
        if !errorlevel! equ 0 (
            set PYTHON_CMD=py
        ) else (
            if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
                set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
            ) else (
                echo.
                echo ERROR: Could not locate Python after installation.
                echo Please close this window and run setup.bat again to continue.
                pause
                exit /b 0
            )
        )
    )
)

echo Found Python: !PYTHON_CMD!
echo.

:: Step 2: Upgrade pip
echo [2/5] Upgrading pip to the latest version...
!PYTHON_CMD! -m pip install --upgrade pip --quiet
if !errorlevel! neq 0 (
    echo WARNING: Failed to upgrade pip. Continuing anyway...
) else (
    echo Pip upgraded successfully.
)
echo.

:: Step 3: Check and auto-generate requirements.txt
echo [3/5] Checking for game requirements...
if not exist requirements.txt (
    echo requirements.txt not found.
    echo Scanning project for imports and auto-generating requirements.txt...
    
    :: Install pipreqs to scan imports correctly
    !PYTHON_CMD! -m pip install pipreqs --quiet
    if !errorlevel! neq 0 (
        echo.
        echo ERROR: Failed to install pipreqs for auto-generating requirements.
        pause
        exit /b 1
    )
    
    !PYTHON_CMD! -m pipreqs.pipreqs . --force
    if !errorlevel! neq 0 (
        echo.
        echo ERROR: Failed to scan project and generate requirements.txt.
        pause
        exit /b 1
    )
    echo requirements.txt auto-generated successfully.
) else (
    echo requirements.txt found.
)
echo.

:: Step 4: Install packages for all games
echo [4/5] Installing required packages for all applications...

echo Installing Battle Sim requirements...
!PYTHON_CMD! -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo WARNING: Failed to install Battle Sim requirements.
)

echo.
echo Installing Minecraft AI requirements...
!PYTHON_CMD! -m pip install -r "minecarft_ai_project (2)\minecarft_ai_project\requirements.txt"
if !errorlevel! neq 0 (
    echo WARNING: Failed to install Minecraft AI requirements.
)

echo.
echo Installing Football Manager Sim requirements...
!PYTHON_CMD! -m pip install flask flask-sqlalchemy flask-socketio eventlet python-dotenv
if !errorlevel! neq 0 (
    echo WARNING: Failed to install Football Manager Sim requirements.
)

echo.
echo Installing Portal requirements...
!PYTHON_CMD! -m pip install flask flask-cors
if !errorlevel! neq 0 (
    echo WARNING: Failed to install Portal requirements.
)

echo All required packages are ready.
echo.

:: Step 5: Launch the portal
echo [5/5] Launching the NexusPlay Portal...

if not exist "portal\app.py" (
    echo.
    echo ERROR: Cannot find the portal\app.py entry point.
    pause
    exit /b 1
)

echo Starting NexusPlay Portal...
echo ========================================================
cd portal
!PYTHON_CMD! app.py

if !errorlevel! neq 0 (
    echo.
    echo ========================================================
    echo ERROR: The portal crashed or closed unexpectedly.
    echo ========================================================
    pause
    exit /b 1
)

echo.
echo Portal finished.
pause
