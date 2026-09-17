@echo off
title PastureRestore - N4-4
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-app.ps1"
pause
