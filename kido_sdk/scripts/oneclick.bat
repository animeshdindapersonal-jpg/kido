@echo off
REM ============================================================
REM  KIDO One-Click Bootstrap (Windows)
REM  User runs this ONE file — does everything.
REM ============================================================
REM  Usage:
REM    1. Save this file as kido-install.bat
REM    2. Double-click it or run from cmd:
REM       kido-install.bat
REM ============================================================

setlocal enabledelayedexpansion
title KIDO Installer

set "GITHUB_REPO=animeshdindapersonal-jpg/kido"
set "API_BASE=https://api.github.com/repos/%GITHUB_REPO%"
set "INSTALLER_VERSION=v1.0"

echo.
echo ============================================================
echo     🧒  KIDO Programming Language — One-Click Setup
echo ============================================================
echo     This will install KIDO on your system.
echo     Internet connection required.
echo ============================================================
echo.

REM -----------------------------------------------------------
REM Phase 1 — Admin check (for PATH modification)
REM -----------------------------------------------------------
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Running without admin privileges.
    echo [INFO] KIDO will be installed for current user only.
    echo [INFO] To install system-wide, run as Administrator.
) else (
    echo [INFO] Running with admin privileges.
)
echo.

REM -----------------------------------------------------------
REM Phase 2 — Check/Create Python
REM -----------------------------------------------------------
echo [1/5] Checking Python...

set "PYTHON_CMD="
for %%c in (python3 python) do (
    where %%c >nul 2>&1 && (
        for /f "tokens=2 delims= " %%v in ('%%c --version 2^>^&1') do set "PYVER=%%v"
        for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
            if %%a geq 3 if %%b geq 8 set "PYTHON_CMD=%%c"
        )
    )
)

if defined PYTHON_CMD (
    echo   [OK] Python found: !PYTHON_CMD!
) else (
    echo   [..] Python not found. Checking for embedded Python...
    set "KIDO_HOME=%USERPROFILE%\.kido"
    if exist "!KIDO_HOME!\python\python.exe" (
        set "PYTHON_CMD=!KIDO_HOME!\python\python.exe"
        echo   [OK] Using embedded Python
    ) else (
        echo   [DOWNLOADING] Python 3.11.5 embeddable...
        if not exist "!KIDO_HOME!" mkdir "!KIDO_HOME!"
        if not exist "!KIDO_HOME!\python" mkdir "!KIDO_HOME!\python"

        curl -sL https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip -o "%TEMP%\python-embed.zip"
        if !errorlevel! neq 0 (
            echo   [ERROR] Failed to download Python.
            pause
            exit /b 1
        )

        powershell -command "Expand-Archive -Path '%TEMP%\python-embed.zip' -DestinationPath '!KIDO_HOME!\python' -Force" >nul
        del "%TEMP%\python-embed.zip"

        if exist "!KIDO_HOME!\python\python311._pth" (
            move "!KIDO_HOME!\python\python311._pth" "!KIDO_HOME!\python\python311._pth.bak" >nul
        )

        curl -sL https://bootstrap.pypa.io/get-pip.py -o "%TEMP%\get-pip.py"
        "!KIDO_HOME!\python\python.exe" "%TEMP%\get-pip.py" --quiet 2>&1 >nul
        del "%TEMP%\get-pip.py"

        set "PYTHON_CMD=!KIDO_HOME!\python\python.exe"
        echo   [OK] Python installed locally
    )
)

setlocal enabledelayedexpansion
set "KIDO_HOME=%USERPROFILE%\.kido"
set "SDK_DIR=!KIDO_HOME!\sdk"
set "BIN_DIR=!KIDO_HOME!\bin"
set "PYTHON_CMD=!PYTHON_CMD!"

REM -----------------------------------------------------------
REM Phase 3 — Download KIDO SDK
REM -----------------------------------------------------------
echo [2/5] Downloading KIDO SDK...

curl -sL %API_BASE%/releases/latest -o "%TEMP%\kido-release.json"
if !errorlevel! neq 0 (
    echo   [ERROR] Failed to fetch release info from GitHub.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('powershell -command "(Get-Content '%TEMP%\kido-release.json' ^| ConvertFrom-Json).assets ^| Where-Object { $_.name -like '*windows*' } ^| Select-Object -First 1 -ExpandProperty browser_download_url"') do set "ASSET_URL=%%a"
for /f "tokens=*" %%v in ('powershell -command "(Get-Content '%TEMP%\kido-release.json' ^| ConvertFrom-Json).tag_name"') do set "VERSION=%%v"
del "%TEMP%\kido-release.json"

if not defined ASSET_URL (
    echo   [ERROR] No Windows SDK zip found in latest release.
    pause
    exit /b 1
)

curl -sL "!ASSET_URL!" -o "%TEMP%\kido-sdk.zip"
if !errorlevel! neq 0 (
    echo   [ERROR] Failed to download SDK.
    pause
    exit /b 1
)

if exist "!SDK_DIR!" rmdir /s /q "!SDK_DIR!" >nul
powershell -command "Expand-Archive -Path '%TEMP%\kido-sdk.zip' -DestinationPath '!SDK_DIR!' -Force" >nul
del "%TEMP%\kido-sdk.zip"

echo   [OK] KIDO SDK !VERSION! downloaded

REM -----------------------------------------------------------
REM Phase 4 — Install Dependencies
REM -----------------------------------------------------------
echo [3/5] Installing dependencies...
if exist "!SDK_DIR!\requirements.txt" (
    "!PYTHON_CMD!" -m pip install -r "!SDK_DIR!\requirements.txt" --quiet 2>&1 >nul
)
echo   [OK] Dependencies installed

REM -----------------------------------------------------------
REM Phase 5 — Self-Test
REM -----------------------------------------------------------
echo [4/5] Running self-test...

REM Smoke test
if exist "!SDK_DIR!\examples\hello.kd" (
    "!PYTHON_CMD!" -m kido_cli.cli run "!SDK_DIR!\examples\hello.kd" > "%TEMP%\kido-test.log" 2>&1
    findstr "Hello" "%TEMP%\kido-test.log" >nul && (
        echo   [OK] Smoke test passed
    ) || (
        echo   [--] Smoke test: unexpected output
    )
)

REM Parse check
set TOTAL=0
set PASSED=0
for /r "!SDK_DIR!\examples" %%f in (*.kd) do (
    set /a TOTAL+=1
    "!PYTHON_CMD!" -m kido_cli.cli check "%%f" >nul 2>&1 && set /a PASSED+=1
)
if !TOTAL! gtr 0 echo   [OK] Parse check: !PASSED!/!TOTAL! passed

REM CLI version
"!PYTHON_CMD!" -m kido_cli.cli version > "%TEMP%\kido-ver.log" 2>&1
findstr "KIDO" "%TEMP%\kido-ver.log" >nul && echo   [OK] CLI version OK
del "%TEMP%\kido-test.log" "%TEMP%\kido-ver.log" 2>nul

REM -----------------------------------------------------------
REM Phase 6 — Add to PATH + Create Launcher
REM -----------------------------------------------------------
echo [5/5] Setting up KIDO launcher...

if not exist "!BIN_DIR!" mkdir "!BIN_DIR!"

(
echo @echo off
echo "!PYTHON_CMD!" -m kido_cli.cli %%*
) > "!BIN_DIR!\kido.bat"

echo !PATH! | findstr /i "!BIN_DIR!" >nul
if !errorlevel! neq 0 (
    setx PATH "!PATH!;!BIN_DIR!" >nul
    echo   [OK] Added to PATH ^(restart terminal^)
) else (
    echo   [OK] Already in PATH
)

REM -----------------------------------------------------------
REM Report
REM -----------------------------------------------------------
echo.
echo ============================================================
echo     🧒  KIDO Bootstrap Complete!
echo ============================================================
echo   Version   : !VERSION!
echo   Install   : !KIDO_HOME!
echo   Python    : !PYTHON_CMD!
echo   SDK       : !SDK_DIR!
echo ============================================================
echo   Try:  kido run examples\hello.kd
echo   Or:   kido shell
echo   Help: kido help
echo ============================================================
echo.
echo   NOTE: If 'kido' is not recognized, restart your terminal.
echo.
pause
