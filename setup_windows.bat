@echo off
setlocal EnableExtensions EnableDelayedExpansion
title AI Security EWS - Windows Setup

cd /d "%~dp0"

echo ============================================================
echo   AI-ASSISTED EARLY WARNING SYSTEM
echo   WINDOWS SETUP
echo ============================================================
echo.

set "PY311="

where py >nul 2>&1
if not errorlevel 1 (
    py -3.11 --version >nul 2>&1
    if not errorlevel 1 set "PY311=py -3.11"
)

if not defined PY311 (
    where python >nul 2>&1
    if not errorlevel 1 (
        for /f "tokens=2" %%V in ('python --version 2^>^&1') do set "PYVER=%%V"
        echo !PYVER! | findstr /b "3.11." >nul 2>&1
        if not errorlevel 1 set "PY311=python"
    )
)

if not defined PY311 (
    echo [ERROR] Python 3.11 was not found.
    echo.
    echo This project requires Python 3.11.x.
    echo Install Python 3.11, tick "Add python.exe to PATH",
    echo then double-click setup_windows.bat again.
    echo.
    pause
    exit /b 1
)

echo [PASS] Python 3.11 detected.
%PY311% --version
echo.

if exist ".venv\Scripts\python.exe" (
    for /f "tokens=2" %%V in ('".venv\Scripts\python.exe" --version 2^>^&1') do set "VENVVER=%%V"

    echo [INFO] Existing virtual environment: Python !VENVVER!
    echo !VENVVER! | findstr /b "3.11." >nul 2>&1

    if errorlevel 1 (
        echo [WARN] Existing .venv uses the wrong Python version.
        echo [INFO] Removing incompatible .venv...
        rmdir /s /q ".venv"

        if exist ".venv" (
            echo [ERROR] Could not remove the old .venv folder.
            echo Close VS Code terminals or Python processes using it,
            echo then run setup_windows.bat again.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo [PASS] Existing .venv uses Python 3.11.
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [INFO] Creating Python 3.11 virtual environment...
    %PY311% -m venv ".venv"

    if errorlevel 1 (
        echo [ERROR] Virtual environment creation failed.
        echo.
        pause
        exit /b 1
    )

    echo [PASS] Virtual environment created.
)

for /f "tokens=2" %%V in ('".venv\Scripts\python.exe" --version 2^>^&1') do set "VENVVER=%%V"
echo !VENVVER! | findstr /b "3.11." >nul 2>&1

if errorlevel 1 (
    echo [ERROR] .venv is using Python !VENVVER!, not Python 3.11.
    echo.
    pause
    exit /b 1
)

echo [PASS] Virtual environment verified: Python !VENVVER!
echo.

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt was not found.
    echo.
    pause
    exit /b 1
)

echo [INFO] Upgrading pip, setuptools and wheel...
".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel

if errorlevel 1 (
    echo [ERROR] Could not upgrade Python packaging tools.
    echo Check the internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Installing project dependencies...
".venv\Scripts\python.exe" -m pip install --no-cache-dir -r "requirements.txt"

if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    echo Review the error above, then run setup_windows.bat again.
    echo.
    pause
    exit /b 1
)

echo [PASS] Project dependencies installed.
echo.

echo [INFO] Verifying scikit-learn installation...
".venv\Scripts\python.exe" -c "import sklearn; print('[PASS] scikit-learn', sklearn.__version__, 'loaded successfully.')"

if errorlevel 1 (
    echo [ERROR] scikit-learn could not be imported correctly.
    echo The virtual environment contains an incompatible installation.
    echo Delete .venv and run this setup again.
    echo.
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo [PASS] Created .env from .env.example.
        echo [INFO] Review .env if your MySQL settings differ from the defaults.
    ) else (
        echo [WARN] .env is missing and .env.example was not found.
    )
) else (
    echo [PASS] Existing .env retained.
)

echo.
echo ============================================================
echo   WINDOWS SETUP COMPLETED
echo ============================================================
echo.
echo Python environment: READY
echo Dependencies:       INSTALLED
echo.
echo NEXT STEP:
echo Double-click run_setup_check.bat
echo.
pause
exit /b 0
