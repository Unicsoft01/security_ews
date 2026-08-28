@echo off
setlocal
title AI Security EWS - Setup Check

REM ============================================================
REM AI-Assisted Early Warning System
REM Automatic Setup Check Launcher
REM ============================================================

REM Always work from the folder where this BAT file is located.
cd /d "%~dp0"

echo ============================================================
echo   AI-ASSISTED EARLY WARNING SYSTEM
echo   AUTOMATIC SETUP CHECK
echo ============================================================
echo.

REM ------------------------------------------------------------
REM 1. Confirm setup_check.py exists
REM ------------------------------------------------------------
if not exist "setup_check.py" (
    echo [ERROR] setup_check.py was not found.
    echo.
    echo Make sure this file is placed in the project root folder,
    echo beside setup_check.py and app.py.
    echo.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM 2. Prefer the project's virtual environment if it exists
REM ------------------------------------------------------------
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Project virtual environment found.
    echo [INFO] Using .venv\Scripts\python.exe
    echo.
    ".venv\Scripts\python.exe" "setup_check.py"
    set "CHECK_RESULT=%ERRORLEVEL%"
    goto RESULT
)

REM ------------------------------------------------------------
REM 3. Fall back to Python Launcher for Python 3.11
REM ------------------------------------------------------------
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3.11 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Virtual environment not found.
        echo [INFO] Using installed Python 3.11.
        echo.
        py -3.11 "setup_check.py"
        set "CHECK_RESULT=%ERRORLEVEL%"
        goto RESULT
    )
)

REM ------------------------------------------------------------
REM 4. Fall back to python command
REM ------------------------------------------------------------
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Virtual environment not found.
    echo [INFO] Using the Python available on this computer.
    echo.
    python "setup_check.py"
    set "CHECK_RESULT=%ERRORLEVEL%"
    goto RESULT
)

REM ------------------------------------------------------------
REM 5. No usable Python installation found
REM ------------------------------------------------------------
echo [ERROR] Python could not be found on this computer.
echo.
echo Install Python 3.11 first, then run this file again.
echo During Python installation, ensure "Add Python to PATH" is enabled.
echo.
pause
exit /b 1

:RESULT
echo.
echo ============================================================

if "%CHECK_RESULT%"=="0" (
    echo   SETUP CHECK COMPLETED SUCCESSFULLY
    echo ============================================================
    echo.
    echo The system setup check has finished.
    echo If the report above says SYSTEM STATUS: READY,
    echo the application is ready to run.
) else (
    echo   SETUP CHECK FOUND A PROBLEM
    echo ============================================================
    echo.
    echo Review the FAIL or ERROR message shown above.
    echo Correct that item, then double-click this file again.
)

echo.
echo Press any key to close this window.
pause >nul
endlocal
