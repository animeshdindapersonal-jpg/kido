@echo off
echo ============================================================
echo KIDO SDK Builder for Windows
echo ============================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo Installing build dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt >nul 2>&1

echo.
echo Building KIDO executable...
python build.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Build complete!
echo ============================================================
echo.
echo To install KIDO:
echo   1. Extract kido-windows.zip
echo   2. Add the folder to your PATH environment variable
echo   3. Open a new command prompt
echo   4. Run: kido version
echo.
pause
