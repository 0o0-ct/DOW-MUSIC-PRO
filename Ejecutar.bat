@echo off
title YouTube Music Downloader Pro++ v4.0
color 0A
cls
echo ========================================================
echo    INICIANDO YOUTUBE MUSIC DOWNLOADER PRO++ v4.0
echo ========================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python desde python.org
    pause
    exit
)

if not exist Principal.py (
    echo [ERROR] No se encuentra el archivo Principal.py
    pause
    exit
)

python Principal.py
pause
