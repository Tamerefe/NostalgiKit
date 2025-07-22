@echo off
title NostalgiKit Launcher
echo.
echo  ████████████████████████████████████████████
echo  █                                          █
echo  █          🎮 NOSTALGIK 🎮           █
echo  █                                          █
echo  █       Vintage Handheld Gaming Hub        █
echo  █                                          █
echo  ████████████████████████████████████████████
echo.
echo  Starting NostalgiKit...
echo  Please wait while we boot up your console...
echo.
timeout /t 2 /nobreak >nul
python main.py
if errorlevel 1 (
    echo.
    echo ❌ Error: Could not start NostalgiKit
    echo Please make sure Python and required dependencies are installed.
    echo.
    pause
) else (
    echo.
    echo ✅ NostalgiKit closed successfully
    echo Thank you for playing!
    timeout /t 2 /nobreak >nul
)
