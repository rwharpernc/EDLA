@echo off
REM Build script for creating EDLA executable
REM Session data uses SQLite (Python stdlib - no extra runtime).
REM Author: R.W. Harper
REM Last Updated: 2025-02-04

echo ========================================
echo EDLA Executable Builder
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to create the virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Checking for PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable...
echo This may take a few minutes...
echo.

pyinstaller EDLA.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo Executable location: dist\EDLA.exe
echo.
echo Next steps:
echo   1. Test the executable: dist\EDLA.exe
echo   2. Create installer using Inno Setup or NSIS
echo   3. See documents/DEVELOPER_GUIDE.md for details
echo.
pause

