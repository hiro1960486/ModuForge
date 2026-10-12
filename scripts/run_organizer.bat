@echo off
setlocal
set "ROOT=%~dp0.."
if not exist "%ROOT%\run_component.py" (
  echo [ERROR] Missing run_component.py
  exit /b 2
)
py "%ROOT%\run_component.py" organizer
set "RC=%ERRORLEVEL%"
exit /b %RC%
