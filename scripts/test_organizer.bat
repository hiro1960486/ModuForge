@echo off
cd /d "%~dp0"
py run_tests.py --module organizer
pause
