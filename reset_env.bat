@echo off
echo Resetting virtual environment for PyQt6...
echo.

REM Check if venv exists
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
    echo Old environment removed.
) else (
    echo No existing virtual environment found.
)

echo.
echo Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Installing PyQt6 and dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete! Ready to run.
echo ========================================
echo.
echo Run: python main.py
echo Or use: run.bat
echo.
pause

