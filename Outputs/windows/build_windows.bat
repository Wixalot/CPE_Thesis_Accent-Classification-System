@echo off
echo ========================================================
echo Building Accent Classification Executable for Windows (.exe)
echo ========================================================

:: Move to script directory
cd /d "%~dp0"

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+ from python.org.
    pause
    exit /b 1
)

:: Set up virtual environment for a clean build
if not exist ".build_env" (
    echo [*] Creating virtual environment...
    python -m venv .build_env
)

echo [*] Activating build environment...
call .build_env\Scripts\activate.bat

echo [*] Installing dependencies and PyInstaller...
python -m pip install --upgrade pip
pip install -r ..\..\requirements.txt pyinstaller

echo [*] Compiling standalone Windows executable...
pyinstaller --noconfirm --clean main_windows.spec

if exist "dist\AccentClassifier.exe" (
    echo ========================================================
    echo [SUCCESS] Windows executable built successfully!
    echo Location: %cd%\dist\AccentClassifier.exe
    echo ========================================================
) else (
    echo [ERROR] Build failed. Please check the logs above.
)

pause
