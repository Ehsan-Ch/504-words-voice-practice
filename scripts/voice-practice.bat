@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0.."
set "PYTHONUTF8=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m voice_practice %*
) else (
  python -m voice_practice %*
)
exit /b %errorlevel%
