@echo off
setlocal
cd /d "%~dp0"
py run_tests.py
set "RC=%ERRORLEVEL%"
echo.
echo All module tests exit code: %RC%
pause
exit /b %RC%
