#!/usr/bin/env pwsh
<#
.SYNOPSIS
    KIDO Bootstrap Installer for Windows (PowerShell)
.DESCRIPTION
    One-liner:  iwr https://kido.dev/install.ps1 | iex
    Downloads Python (if missing), fetches KIDO SDK from GitHub Releases,
    builds, self-tests, and adds to PATH.
#>

$Host.UI.RawUI.WindowTitle = "KIDO Installer"
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$GITHUB_REPO = "animeshdindapersonal-jpg/kido"
$API_BASE     = "https://api.github.com/repos/$GITHUB_REPO"
$RELEASE_URL  = "$API_BASE/releases/latest"
$SCRIPT_URL   = "https://raw.githubusercontent.com/$GITHUB_REPO/main/kido_sdk/scripts"

$KIDO_HOME    = "$env:USERPROFILE\.kido"
$PYTHON_DIR   = "$KIDO_HOME\python"
$SDK_DIR      = "$KIDO_HOME\sdk"
$BIN_DIR      = "$KIDO_HOME\bin"

$PYTHON_EXE   = "$PYTHON_DIR\python.exe"
$PIP_EXE      = "$PYTHON_DIR\Scripts\pip.exe"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🧒  KIDO Programming Language — Bootstrap Installer" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------
# Phase 1 — Ensure Python
# -----------------------------------------------------------
function Ensure-Python {
    $found = $null
    # Try python3 first, then python
    foreach ($name in @("python3", "python")) {
        try {
            $v = & $name --version 2>&1
            if ($v -match "Python (\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -ge 3 -and $minor -ge 8) {
                    Write-Host "✅  Python $major.$minor found: $(Get-Command $name).Source" -ForegroundColor Green
                    return (Get-Command $name).Source
                }
            }
        } catch {}
    }

    Write-Host "📥  Python 3.8+ not found. Downloading embeddable Python..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $PYTHON_DIR | Out-Null

    $pyUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip"
    $pyZip = "$env:TEMP\python-embed.zip"
    try {
        Invoke-WebRequest -Uri $pyUrl -OutFile $pyZip -UseBasicParsing
    } catch {
        Write-Host "❌  Failed to download Python. Check your internet connection." -ForegroundColor Red
        exit 1
    }
    Expand-Archive -Path $pyZip -DestinationPath $PYTHON_DIR -Force

    # Enable pip by renaming _pth file
    Remove-Item "$PYTHON_DIR\python*._pth" -Force -ErrorAction SilentlyContinue

    # Download get-pip.py and install pip
    $getPip = "$env:TEMP\get-pip.py"
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip -UseBasicParsing
    & $PYTHON_EXE $getPip --no-warn-script-location 2>&1 | Out-Null

    Write-Host "✅  Python 3.11.5 installed locally (no admin needed)" -ForegroundColor Green
    return $PYTHON_EXE
}

# -----------------------------------------------------------
# Phase 2 — Download KIDO SDK
# -----------------------------------------------------------
function Get-KidoSDK {
    Write-Host "📥  Fetching latest KIDO SDK release..." -ForegroundColor Yellow

    try {
        $release = Invoke-RestMethod -Uri $RELEASE_URL -UseBasicParsing
    } catch {
        Write-Host "❌  Failed to fetch release info from GitHub." -ForegroundColor Red
        exit 1
    }

    $assetUrl = $null
    foreach ($asset in $release.assets) {
        if ($asset.name -eq "kido-sdk-windows.zip") {
            $assetUrl = $asset.browser_download_url
            break
        }
    }

    if (-not $assetUrl) {
        Write-Host "❌  No kido-sdk-windows.zip found in latest release." -ForegroundColor Red
        exit 1
    }

    $version = $release.tag_name
    $sdkZip = "$env:TEMP\kido-sdk.zip"
    Invoke-WebRequest -Uri $assetUrl -OutFile $sdkZip -UseBasicParsing

    New-Item -ItemType Directory -Force -Path $SDK_DIR | Out-Null
    Expand-Archive -Path $sdkZip -DestinationPath $SDK_DIR -Force

    Write-Host "✅  KIDO SDK $version downloaded" -ForegroundColor Green
    return $version
}

# -----------------------------------------------------------
# Phase 3 — Install Dependencies
# -----------------------------------------------------------
function Install-Deps {
    Write-Host "📦  Installing dependencies..." -ForegroundColor Yellow

    $req = "$SDK_DIR\requirements.txt"
    if (Test-Path $req) {
        & $PIP_EXE install -r $req --quiet 2>&1 | Out-Null
    }
    Write-Host "✅  Dependencies installed" -ForegroundColor Green
}

# -----------------------------------------------------------
# Phase 4 — Self-Test
# -----------------------------------------------------------
function Run-SelfTest {
    Write-Host "🧪  Running self-test..." -ForegroundColor Yellow

    # Smoke test
    $helloFile = "$SDK_DIR\examples\hello.kd"
    if (Test-Path $helloFile) {
        $out = & $PYTHON_EXE -m kido_cli.cli run $helloFile 2>&1
        if ($out -match "Hello") {
            Write-Host "  ✅  Smoke test passed" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️   Smoke test: unexpected output" -ForegroundColor Yellow
        }
    }

    # Parse check on all examples (quick)
    $total = 0
    $passed = 0
    $exDir = "$SDK_DIR\examples"
    if (Test-Path $exDir) {
        $files = Get-ChildItem -Path $exDir -Recurse -Filter "*.kd"
        foreach ($f in $files) {
            $total++
            $out = & $PYTHON_EXE -m kido_cli.cli check $f.FullName 2>&1
            if ($out -match "No problems") { $passed++ }
        }
    }

    if ($total -gt 0) {
        Write-Host "  ✅  Parse check: $passed/$total passed" -ForegroundColor Green
    }

    # CLI check
    $v = & $PYTHON_EXE -m kido_cli.cli version 2>&1
    if ($v -match "KIDO") {
        Write-Host "  ✅  CLI version check passed" -ForegroundColor Green
    }
}

# -----------------------------------------------------------
# Phase 5 — Add to PATH
# -----------------------------------------------------------
function Add-ToPath {
    Write-Host "🔧  Adding KIDO to PATH..." -ForegroundColor Yellow

    New-Item -ItemType Directory -Force -Path $BIN_DIR | Out-Null

    # Create a launcher batch file
@"
@echo off
"$PYTHON_EXE" -m kido_cli.cli %*
"@ | Out-File -FilePath "$BIN_DIR\kido.bat" -Encoding ascii

    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*$BIN_DIR*") {
        $newPath = "$userPath;$BIN_DIR"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        $env:PATH = "$env:PATH;$BIN_DIR"
        Write-Host "  ✅  Added to user PATH (restart terminal to apply)" -ForegroundColor Green
    } else {
        Write-Host "  ✅  Already in PATH" -ForegroundColor Green
    }
}

# -----------------------------------------------------------
# Report
# -----------------------------------------------------------
function Show-Report {
    param($Version)

    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║       🧒  KIDO Bootstrap Complete!                        ║" -ForegroundColor Cyan
    Write-Host "╠═══════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "║  KIDO Home : $KIDO_HOME" -ForegroundColor White
    Write-Host "║  Version   : $Version" -ForegroundColor White
    Write-Host "║  Python    : $PYTHON_EXE" -ForegroundColor White
    Write-Host "║  SDK       : $SDK_DIR" -ForegroundColor White
    Write-Host "╠═══════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
    Write-Host "║  Try it now:  kido run examples\hello.kd                  ║" -ForegroundColor White
    Write-Host "║  Or:          kido shell                                   ║" -ForegroundColor White
    Write-Host "║  Help:        kido help                                    ║" -ForegroundColor White
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

# ===========================================================
# MAIN
# ===========================================================
try {
    $pythonExe = Ensure-Python
    $version   = Get-KidoSDK
    Install-Deps
    Run-SelfTest
    Add-ToPath
    Show-Report -Version $version
} catch {
    Write-Host "❌  Installation failed: $_" -ForegroundColor Red
    exit 1
}
