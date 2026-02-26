# to-markdown installer for Windows
# Usage: .\install.ps1
# Requires: PowerShell 5.1+ (default on Windows 10/11)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TotalSteps = 7
$CurrentStep = 0

# --- Helpers ---
function Step($msg) {
    $script:CurrentStep++
    Write-Host ""
    Write-Host "[$script:CurrentStep/$TotalSteps] " -ForegroundColor Blue -NoNewline
    Write-Host $msg -ForegroundColor White
}

function Ok($msg) { Write-Host "  OK " -ForegroundColor Green -NoNewline; Write-Host $msg }
function Warn($msg) { Write-Host "  WARNING " -ForegroundColor Yellow -NoNewline; Write-Host $msg }
function Fail($msg) { Write-Host "  FAILED " -ForegroundColor Red -NoNewline; Write-Host $msg; exit 1 }
function Info($msg) { Write-Host "  $msg" }

# --- Banner ---
Write-Host ""
Write-Host "  to-markdown installer for Windows" -ForegroundColor White
Write-Host ""

# --- Check execution policy ---
$policy = Get-ExecutionPolicy -Scope CurrentUser
if ($policy -eq "Restricted") {
    Write-Host "  PowerShell execution policy is Restricted." -ForegroundColor Yellow
    Write-Host "  Run this command first (as Administrator):" -ForegroundColor Yellow
    Write-Host "    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# --- Step 1: Check uv ---
Step "Checking uv package manager"
try {
    $uvVersion = & uv --version 2>$null
    if ($uvVersion) {
        Ok "uv found ($uvVersion)"
    } else {
        throw "not found"
    }
} catch {
    Info "uv not found. Installing..."
    try {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
        $uvVersion = & uv --version 2>$null
        if ($uvVersion) {
            Ok "uv installed successfully"
        } else {
            Fail "uv installed but not found in PATH. Restart PowerShell and re-run this script."
        }
    } catch {
        Fail "Failed to install uv. Install manually: irm https://astral.sh/uv/install.ps1 | iex"
    }
}

# --- Step 2: Check Python 3.14+ ---
Step "Checking Python 3.14+"
$pythonOk = $false
try {
    $pythonList = & uv python list --only-installed 2>$null
    if ($pythonList -match "3\.1[4-9]|3\.[2-9][0-9]") {
        $pyMatch = ($pythonList | Select-String "3\.1[4-9]|3\.[2-9][0-9]" | Select-Object -First 1).ToString().Trim().Split()[0]
        Ok "Python $pyMatch found"
        $pythonOk = $true
    }
} catch {}

if (-not $pythonOk) {
    Info "Python 3.14+ not found. Installing via uv..."
    try {
        & uv python install 3.14 2>$null
        Ok "Python 3.14 installed"
    } catch {
        Warn "Python 3.14 not available. Trying 3.13..."
        try {
            & uv python install 3.13 2>$null
            Ok "Python 3.13 installed (3.14 unavailable)"
        } catch {
            Fail "Could not install Python. Run: uv python install 3.14 (or 3.13)"
        }
    }
}

# --- Step 3: Check Tesseract (optional) ---
Step "Checking Tesseract OCR (optional)"
try {
    $tessVersion = & tesseract --version 2>$null | Select-Object -First 1
    if ($tessVersion) {
        Ok "Tesseract found ($tessVersion)"
    } else {
        throw "not found"
    }
} catch {
    Info "Tesseract not found. It enables OCR for scanned PDFs and images."
    $wingetAvailable = $false
    try { $null = Get-Command winget -ErrorAction Stop; $wingetAvailable = $true } catch {}

    if ($wingetAvailable) {
        $reply = Read-Host "  Install Tesseract via winget? [y/N]"
        if ($reply -match "^[Yy]$") {
            try {
                & winget install UB-Mannheim.TesseractOCR --accept-package-agreements --accept-source-agreements 2>$null
                Ok "Tesseract installed"
            } catch {
                Warn "Tesseract install failed. OCR features won't work."
                Info "Install manually: https://github.com/UB-Mannheim/tesseract/wiki"
            }
        } else {
            Info "Skipped. OCR features won't work without Tesseract."
        }
    } else {
        Warn "winget not found. Tesseract install skipped."
        Info "Install manually: https://github.com/UB-Mannheim/tesseract/wiki"
    }
}

# --- Step 4: Install dependencies ---
Step "Installing dependencies"
Set-Location $ScriptDir
try {
    & uv sync --all-extras 2>&1
    Ok "All dependencies installed"
} catch {
    Fail "Dependency install failed. Try: uv sync --all-extras --verbose"
}

# --- Step 5: Validate installation ---
Step "Validating installation"
try {
    $version = & uv run to-markdown --version 2>$null
    if ($version) {
        Ok $version
    } else {
        throw "no output"
    }
} catch {
    Fail "Installation validation failed. Try: uv run to-markdown --version"
}

# --- Step 6: Set up PowerShell function ---
Step "Setting up PowerShell alias"
$functionLine = "function to-markdown { uv run --directory `"$ScriptDir`" to-markdown @args }"
$functionComment = "# Added by to-markdown installer"

# Get or create PowerShell profile
$profilePath = $PROFILE.CurrentUserCurrentHost
$profileDir = Split-Path -Parent $profilePath

if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}

# Check if function already exists
$profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
if ($profileContent -and $profileContent.Contains("function to-markdown")) {
    Ok "PowerShell function already configured in $profilePath"
} else {
    Add-Content -Path $profilePath -Value ""
    Add-Content -Path $profilePath -Value $functionComment
    Add-Content -Path $profilePath -Value $functionLine
    Ok "Added function to $profilePath"
    Info "Run: . `$PROFILE (or open a new PowerShell window)"
}

# --- Step 7: Success ---
Step "Installation complete!"
Write-Host ""
Write-Host "  to-markdown is ready to use!" -ForegroundColor Green
Write-Host ""
Write-Host "  Quick start:"
Write-Host "    to-markdown yourfile.pdf          # Convert a file"
Write-Host "    to-markdown docs\                 # Convert a directory"
Write-Host "    to-markdown --setup               # Configure smart features (optional)"
Write-Host ""
Write-Host "  For detailed instructions, see: INSTALL.md"
Write-Host ""
Write-Host "  Note: " -ForegroundColor Yellow -NoNewline
Write-Host "Open a new PowerShell window or run '. `$PROFILE' to use the function."
Write-Host ""
