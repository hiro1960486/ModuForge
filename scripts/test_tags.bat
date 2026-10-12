@echo off
setlocal
set "ROOT=%~dp0.."
if not exist "%ROOT%\run_tests.py" (
  echo [ERROR] Missing run_tests.py
  exit /b 2
)
py "%ROOT%\run_tests.py" --module tags
set "RC=%ERRORLEVEL%"
exit /b %RC%
