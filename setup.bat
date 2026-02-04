@echo off
echo Elite Dangerous Log Analyzer - Setup
echo.

REM Check Python version
python --version
echo.

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo Data storage:
echo   - Session and processed-file data use SQLite (Python standard library).
echo   - Database file: %%USERPROFILE%%\.edla\edla.db
echo   - Commander profiles remain in %%USERPROFILE%%\.edla\profiles\ (JSON).
echo.
echo To run the application:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run: python main.py
echo.
echo Or use run.bat which will do this automatically.
pause

