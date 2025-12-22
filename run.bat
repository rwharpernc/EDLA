@echo off
REM Elite Dangerous Log Analyzer - Run Script
REM This script runs the EDLA application with logging

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Get timestamp for log file (format: YYYYMMDD_HHMMSS)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set logfile=logs\run_%datetime:~0,8%_%datetime:~8,6%.log

REM Start logging
echo [%date% %time%] ======================================== >> "%logfile%"
echo [%date% %time%] Starting Elite Dangerous Log Analyzer >> "%logfile%"
echo [%date% %time%] ======================================== >> "%logfile%"
echo.

echo Elite Dangerous Log Analyzer
echo Logging to: %logfile%
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo [%date% %time%] Activating virtual environment... >> "%logfile%"
    echo Activating virtual environment...
    call venv\Scripts\activate.bat >> "%logfile%" 2>&1
    
    REM Check if PyQt6 is installed, if not install dependencies
    python -c "import PyQt6" >> "%logfile%" 2>&1
    if errorlevel 1 (
        echo [%date% %time%] PyQt6 not found. Installing dependencies... >> "%logfile%"
        echo PyQt6 not found. Installing dependencies...
        pip install -r requirements.txt >> "%logfile%" 2>&1
        if errorlevel 1 (
            echo [%date% %time%] ERROR: Failed to install dependencies >> "%logfile%"
            echo ERROR: Failed to install dependencies
            echo Check %logfile% for details.
            pause
            exit /b 1
        )
    )
) else (
    echo [%date% %time%] No virtual environment found. Installing dependencies globally... >> "%logfile%"
    echo No virtual environment found. Installing dependencies globally...
    echo (Consider running setup.bat to create a virtual environment)
    pip install -r requirements.txt >> "%logfile%" 2>&1
    if errorlevel 1 (
        echo [%date% %time%] ERROR: Failed to install dependencies >> "%logfile%"
        echo ERROR: Failed to install dependencies
        echo Check %logfile% for details.
        pause
        exit /b 1
    )
)

echo.
echo [%date% %time%] Starting application... >> "%logfile%"
echo Starting application...

REM Run the application and capture all output
python main.py >> "%logfile%" 2>&1
set exitcode=%ERRORLEVEL%

REM Log the exit code
echo [%date% %time%] Application exited with code: %exitcode% >> "%logfile%"
echo [%date% %time%] ======================================== >> "%logfile%"

REM If there was an error, also append to a general error log
if %exitcode% neq 0 (
    echo. >> logs\error.log
    echo ======================================== >> logs\error.log
    echo [%date% %time%] Application crashed with exit code %exitcode% >> logs\error.log
    echo ======================================== >> logs\error.log
    type "%logfile%" >> logs\error.log
    echo. >> logs\error.log
    echo.
    echo ERROR: Application crashed with exit code %exitcode%
    echo Check logs\error.log and logs\app.log for details.
    echo Latest run log: %logfile%
)

exit /b %exitcode%
