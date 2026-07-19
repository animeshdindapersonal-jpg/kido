@echo off
echo ============================================================
echo KIDO Installer for Windows
echo ============================================================
echo.

REM Check if build exists
if not exist "dist\kido.exe" (
    echo ERROR: KIDO executable not found in dist\
    echo Please run build_windows.bat first to build KIDO.
    pause
    exit /b 1
)

REM Ask for installation type
echo Choose installation type:
echo   1. Install for all users (requires admin)
echo   2. Install for current user only
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    set INSTALL_DIR=C:\Program Files\KIDO
    set NEED_ADMIN=1
) else if "%choice%"=="2" (
    set INSTALL_DIR=%USERPROFILE%\AppData\Local\KIDO
    set NEED_ADMIN=0
) else (
    echo Invalid choice. Please run again and enter 1 or 2.
    pause
    exit /b 1
)

echo.
echo Installing KIDO to: %INSTALL_DIR%

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy /y "dist\kido.exe" "%INSTALL_DIR%\" >nul
echo [OK] KIDO executable installed

REM Copy examples
if exist "examples" (
    xcopy /e /i /y "examples" "%INSTALL_DIR%\examples" >nul
    echo [OK] Examples installed
)

REM Copy README
if exist "README.md" (
    copy /y "README.md" "%INSTALL_DIR%\" >nul
)

REM Add to PATH
if "%NEED_ADMIN%"=="1" (
    echo.
    echo Adding KIDO to system PATH...
    setx /M PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Could not add to system PATH.
        echo Please add manually: %INSTALL_DIR%
    ) else (
        echo [OK] Added to system PATH
    )
) else (
    echo.
    echo Adding KIDO to user PATH...
    setx PATH "%PATH%;%INSTALL_DIR%" >nul 2>&1
    echo [OK] Added to user PATH
)

echo.
echo ============================================================
echo Installation complete!
echo ============================================================
echo.
echo IMPORTANT: Please close this window and open a NEW Command Prompt
echo to use KIDO. The PATH changes need a new window to take effect.
echo.
echo Then try:
echo   kido version
echo   kido help
echo   kido run "%INSTALL_DIR%\examples\hello.kd"
echo.
pause
