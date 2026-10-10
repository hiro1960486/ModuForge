@echo off
cd /d "%~dp0"
py run_component.py tags
if errorlevel 1 pause
