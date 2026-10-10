@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo FileWorkbench Module Test UI Starting...
echo ========================================================

rem 1. 仮想環境 (.venv) があれば有効化
if exist "..\.venv\Scripts\activate.bat" (
    echo [INFO] Activating .venv from parent folder...
    call "..\.venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating .venv...
    call ".venv\Scripts\activate.bat"
)

rem 2. Pythonの存在確認
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b 1
)

rem 3. 実行
echo [INFO] Running test_runner_ui.py...
python test_runner_ui.py

rem 終了コードの判定
if %ERRORLEVEL% neq 0 (
    echo.
    echo ========================================================
    echo [ERROR] Execution failed with exit code: %ERRORLEVEL%
    echo ========================================================
) else (
    echo.
    echo [INFO] Process finished successfully.
)

pause
endlocal