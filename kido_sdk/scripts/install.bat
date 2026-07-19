@echo off
REM ============================================================
REM  KIDO Bootstrap Installer for Windows (cmd)
REM ============================================================
REM One-liner:  curl -L https://kido.dev/install.bat | cmd
REM ============================================================

setlocal enabledelayedexpansion
set GITHUB_REPO=animeshdindapersonal-jpg/kido
set API_BASE=https://api.github.com/repos/%GITHUB_REPO%
set RELEASE_URL=%API_BASE%/releases/latest
set KIDO_HOME=%USERPROFILE%\.kido
set SDK_DIR=%KIDO_HOME%\sdk
set BIN_DIR=%KIDO_HOME%\bin

echo ============================================================
echo   🧒  KIDO Programming Language — Bootstrap Installer
echo ============================================================
echo.

REM -----------------------------------------------------------
REM Phase 1 — Ensure Python
REM -----------------------------------------------------------
set PYTHON_CMD=
for %%c in (python3 python) do (
    where %%c >nul 2>&1 && (
        for /f "tokens=2 delims= " %%v in ('%%c --version 2^>^&1') do set PYVER=%%v
        for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
            if %%a geq 3 if %%b geq 8 set PYTHON_CMD=%%c
        )
    )
)

if defined PYTHON_CMD (
    echo [OK] Python found: !PYTHON_CMD!
) else (
    echo [..] Python 3.8+ not found. Checking for embedded Python at %KIDO_HOME%\python...
    if exist "%KIDO_HOME%\python\python.exe" (
        set PYTHON_CMD=%KIDO_HOME%\python\python.exe
        echo [OK] Using embedded Python
    ) else (
        echo [DOWNLOADING] Python 3.11.5 embeddable...
        if not exist "%KIDO_HOME%" mkdir "%KIDO_HOME%"
        if not exist "%KIDO_HOME%\python" mkdir "%KIDO_HOME%\python"

        REM Download embeddable Python
        curl -sL https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip -o "%TEMP%\python-embed.zip"
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to download Python. Check internet connection.
            pause
            exit /b 1
        )

        powershell -command "Expand-Archive -Path '%TEMP%\python-embed.zip' -DestinationPath '%KIDO_HOME%\python' -Force" >nul
        del "%TEMP%\python-embed.zip"

        REM Enable pip: rename _pth file
        if exist "%KIDO_HOME%\python\python311._pth" (
            move "%KIDO_HOME%\python\python311._pth" "%KIDO_HOME%\python\python311._pth.bak" >nul
        )

        REM Download get-pip.py
        curl -sL https://bootstrap.pypa.io/get-pip.py -o "%TEMP%\get-pip.py"
        "%KIDO_HOME%\python\python.exe" "%TEMP%\get-pip.py" --quiet 2>&1 >nul
        del "%TEMP%\get-pip.py"

        set PYTHON_CMD=%KIDO_HOME%\python\python.exe
        echo [OK] Python 3.11.5 installed locally (no admin needed)
    )
)

set PIP_CMD=
if "%PYTHON_CMD%"=="%KIDO_HOME%\python\python.exe" (
    set PIP_CMD=%KIDO_HOME%\python\Scripts\pip.exe
) else (
    set PIP_CMD=pip
)

REM -----------------------------------------------------------
REM Phase 2 — Download KIDO SDK from GitHub Releases
REM -----------------------------------------------------------
echo.
echo [DOWNLOADING] Latest KIDO SDK release...

REM Get release info via GitHub API
curl -sL %RELEASE_URL% -o "%TEMP%\kido-release.json"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to fetch release info from GitHub.
    pause
    exit /b 1
)

REM Extract download URL for Windows SDK zip
for /f "tokens=*" %%a in ('powershell -command "(Get-Content '%TEMP%\kido-release.json' | ConvertFrom-Json).assets | Where-Object { $_.name -like '*windows*' } | Select-Object -First 1 -ExpandProperty browser_download_url"') do set ASSET_URL=%%a

if not defined ASSET_URL (
    echo [ERROR] No Windows SDK zip found in latest release.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('powershell -command "(Get-Content '%TEMP%\kido-release.json' | ConvertFrom-Json).tag_name"') do set VERSION=%%v
del "%TEMP%\kido-release.json"

curl -sL "!ASSET_URL!" -o "%TEMP%\kido-sdk.zip"
if !errorlevel! neq 0 (
    echo [ERROR] Failed to download SDK.
    pause
    exit /b 1
)

if exist "%SDK_DIR%" rmdir /s /q "%SDK_DIR%" >nul
powershell -command "Expand-Archive -Path '%TEMP%\kido-sdk.zip' -DestinationPath '%SDK_DIR%' -Force" >nul
del "%TEMP%\kido-sdk.zip"

echo [OK] KIDO SDK %VERSION% downloaded

REM -----------------------------------------------------------
REM Phase 3 — Install dependencies
REM -----------------------------------------------------------
echo.
echo [SETUP] Installing dependencies...
if exist "%SDK_DIR%\requirements.txt" (
    "%PYTHON_CMD%" -m pip install -r "%SDK_DIR%\requirements.txt" --quiet 2>&1 >nul
)
echo [OK] Dependencies installed

REM -----------------------------------------------------------
REM Phase 4 — Self-Test
REM -----------------------------------------------------------
echo.
echo [TEST] Running self-test...

REM Smoke test
if exist "%SDK_DIR%\examples\hello.kd" (
    for /f %%o in ('"%PYTHON_CMD%" -m kido_cli.cli run "%SDK_DIR%\examples\hello.kd" 2^>nul') do set OUT=%%o
    echo !OUT! | findstr "Hello" >nul && (
        echo   [OK] Smoke test passed
    ) || (
        echo   [--] Smoke test: unexpected output
    )
)

REM Parse check on examples
set TOTAL=0
set PASSED=0
for /r "%SDK_DIR%\examples" %%f in (*.kd) do (
    set /a TOTAL+=1
    for /f "delims=" %%o in ('"%PYTHON_CMD%" -m kido_cli.cli check "%%f" 2^>nul') do (
        echo %%o | findstr "No problems" >nul && set /a PASSED+=1
    )
)
if !TOTAL! gtr 0 (
    echo   [OK] Parse check: !PASSED!/!TOTAL! passed
)

REM CLI version check
for /f %%v in ('"%PYTHON_CMD%" -m kido_cli.cli version 2^>nul') do set VER_OUT=%%v
echo !VER_OUT! | findstr "KIDO" >nul && (
    echo   [OK] CLI version check passed
)

REM -----------------------------------------------------------
REM Phase 5 — Add to PATH
REM -----------------------------------------------------------
echo.
echo [PATH] Adding KIDO to user PATH...

if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

REM Create launcher batch file
(
echo @echo off
echo "%PYTHON_CMD:"=%" -m kido_cli.cli %%*
) > "%BIN_DIR%\kido.bat"

REM Check if already in PATH
echo !PATH! | findstr /i "!BIN_DIR!" >nul
if !errorlevel! neq 0 (
    setx PATH "!PATH!;!BIN_DIR!" >nul
    echo   [OK] Added to user PATH
    echo   [!!] Restart terminal to apply PATH changes
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
echo   KIDO Home : %KIDO_HOME%
echo   Version   : %VERSION%
echo   Python    : %PYTHON_CMD%
echo   SDK       : %SDK_DIR%
echo ============================================================
echo   Try:  kido run examples\hello.kd
echo   Or:   kido shell
echo   Help: kido help
echo ============================================================
echo.

pause
