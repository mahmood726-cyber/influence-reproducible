@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0v2\tools\run_full.ps1"
exit /b %errorlevel%
