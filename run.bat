@echo off
echo Elite Dangerous Log Analyzer
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    
    REM Check if PyQt6 is installed, if not install dependencies
    python -c "import PyQt6" 2>nul
    if errorlevel 1 (
        echo PyQt6 not found. Installing dependencies...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo ERROR: Failed to install dependencies
            pause
            exit /b 1
        )
    )
) else (
    echo No virtual environment found. Installing dependencies globally...
    echo (Consider running setup.bat to create a virtual environment)
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting application...
python main.py
