@echo off
REM Build script for creating EDLA installer
REM This is a template - requires Inno Setup to be installed
REM Author: R.W. Harper
REM Last Updated: 2025-12-09

echo ========================================
echo EDLA Installer Builder
echo ========================================
echo.

REM Check if executable exists
if not exist dist\EDLA.exe (
    echo ERROR: Executable not found!
    echo Please run build_exe.bat first to create the executable.
    pause
    exit /b 1
)

REM Check if Inno Setup is installed
where iscc >nul 2>&1
if errorlevel 1 (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo After installation, add Inno Setup to your PATH or
    echo update this script with the full path to iscc.exe
    echo.
    pause
    exit /b 1
)

echo Building installer...
echo.

REM Build installer using Inno Setup script
REM Note: installer_script.iss needs to be created
if exist installer_script.iss (
    iscc installer_script.iss
    if errorlevel 1 (
        echo ERROR: Installer build failed!
        pause
        exit /b 1
    )
    echo.
    echo ========================================
    echo Installer build complete!
    echo ========================================
    echo.
    echo Installer location: Output\EDLA_Setup.exe
    echo.
) else (
    echo ERROR: installer_script.iss not found!
    echo.
    echo Please create an Inno Setup script file.
    echo See documents/DEVELOPER_GUIDE.md for template.
    echo.
)

pause

