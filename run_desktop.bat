@echo off
title Diyargezer Desktop
cd /d "%~dp0"
echo Starting Diyargezer High-Fantasy Desktop Application...
python desktop/main_desktop.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running Diyargezer Desktop!
    pause
)
