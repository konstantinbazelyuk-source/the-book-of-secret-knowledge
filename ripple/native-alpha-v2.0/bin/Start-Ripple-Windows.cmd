@echo off
setlocal
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
 ".venv\Scripts\python.exe" -m ripple_native daemon
) else (
 python -m ripple_native daemon
)
endlocal
