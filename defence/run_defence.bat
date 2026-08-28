@echo off

title AI Security Early Warning System By Aleke Promise

cd /d "%~dp0.."

echo ==========================================
echo AI-Assisted Early Warning System
echo Aleke Promise
echo ==========================================
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Running system health check...
python -m defence.health_check

if errorlevel 1 (
    echo.
    echo HEALTH CHECK FAILED.
    echo Fix the reported issue before starting.
    pause
    exit /b 1
)

echo.
echo Starting Streamlit...
streamlit run app.py

pause