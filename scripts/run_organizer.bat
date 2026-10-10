@echo off
cd /d "%~dp0"
py run_component.py organizer
if errorlevel 1 pause
