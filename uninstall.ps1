# to-markdown uninstaller for Windows
# Usage: .\uninstall.ps1 [-Yes]

param(
    [switch]$Yes
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Confirm-Action($msg) {
    if ($Yes) { return $true }
    $reply = Read-Host "$msg [y/N]"
    return $reply -match "^[Yy]$"
}

Write-Host ""
Write-Host "  to-markdown uninstaller" -ForegroundColor White
Write-Host ""

# --- Remove PowerShell function ---
Write-Host "1. " -ForegroundColor Yellow -NoNewline
Write-Host "PowerShell function"

$profilePath = $PROFILE.CurrentUserCurrentHost
if (Test-Path $profilePath) {
    $content = Get-Content $profilePath -Raw
    if ($content -and $content.Contains("function to-markdown")) {
        if (Confirm-Action "  Remove to-markdown function from PowerShell profile?") {
            $lines = Get-Content $profilePath
            $filtered = $lines | Where-Object {
                $_ -notmatch "function to-markdown" -and $_ -notmatch "# Added by to-markdown installer"
            }
            Set-Content -Path $profilePath -Value $filtered
            Write-Host "  Removed function from profile" -ForegroundColor Green
        } else {
            Write-Host "  Skipped"
        }
    } else {
        Write-Host "  No to-markdown function in profile"
    }
} else {
    Write-Host "  No PowerShell profile found"
}

# --- Remove virtual environment ---
Write-Host "2. " -ForegroundColor Yellow -NoNewline
Write-Host "Virtual environment"

$venvDir = Join-Path $ScriptDir ".venv"
if (Test-Path $venvDir) {
    if (Confirm-Action "  Remove virtual environment ($venvDir)?") {
        Remove-Item -Recurse -Force $venvDir
        Write-Host "  Removed .venv" -ForegroundColor Green
    } else {
        Write-Host "  Skipped"
    }
} else {
    Write-Host "  No .venv found"
}

# --- Remove data directory ---
Write-Host "3. " -ForegroundColor Yellow -NoNewline
Write-Host "Data directory"

$dataDir = Join-Path $env:USERPROFILE ".to-markdown"
if (Test-Path $dataDir) {
    if (Confirm-Action "  Remove data directory ($dataDir)?") {
        Remove-Item -Recurse -Force $dataDir
        Write-Host "  Removed $dataDir" -ForegroundColor Green
    } else {
        Write-Host "  Skipped"
    }
} else {
    Write-Host "  No data directory found"
}

# --- Remove .env file ---
Write-Host "4. " -ForegroundColor Yellow -NoNewline
Write-Host "Configuration"

$envFile = Join-Path $ScriptDir ".env"
if (Test-Path $envFile) {
    if (Confirm-Action "  Remove configuration file ($envFile)?") {
        Remove-Item $envFile
        Write-Host "  Removed .env" -ForegroundColor Green
    } else {
        Write-Host "  Skipped"
    }
} else {
    Write-Host "  No .env file found"
}

Write-Host ""
Write-Host "  Uninstall complete." -ForegroundColor Green
Write-Host "  Converted .md files have been preserved."
Write-Host "  To fully remove, delete the project directory: Remove-Item -Recurse $ScriptDir"
Write-Host ""
