@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\bootstrap-portable.ps1"
if errorlevel 1 (
 echo Ripple installation did not finish. See the error above.
 pause
)