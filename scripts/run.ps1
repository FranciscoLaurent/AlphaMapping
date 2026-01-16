<#
.SYNOPSIS
    AlphaMapping Startup Script
.DESCRIPTION
    Automates the setup and execution of the AlphaMapping system.
    Handles dependency installation, database checks, and service startup.
#>

$ErrorActionPreference = "Stop"

function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }

Write-Info "Initializing AlphaMapping System..."

# 1. Check Python Environment
try {
    $pythonVersion = python --version 2>&1
    Write-Info "Detected Python: $pythonVersion"
} catch {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8+."
    exit 1
}

# 2. Setup Backend
Write-Info "Setting up Backend..."
Push-Location backend

# Check Dependencies
if (-not (Test-Path "venv")) {
    Write-Info "Creating virtual environment..."
    python -m venv venv
}

# Activate Venv (Optional logic if running in current shell, but for Start-Process we rely on system python or simple install)
# For simplicity in this dev script, we install to current python environment if venv logic is complex to pass to Start-Process
Write-Info "Installing dependencies..."
pip install -r requirements.txt | Out-Null

# Environment Config
if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Warn "Created .env from template. Please update backend/.env with your API keys!"
    } else {
        Write-Warn ".env.example not found!"
    }
}

# Create necessary directories
Write-Info "Setting up data directories..."
$dataDir = Join-Path $PSScriptRoot "..\data"
$reportsDir = Join-Path $dataDir "reports"

if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
    Write-Success "Created data directory"
}

if (-not (Test-Path $reportsDir)) {
    New-Item -ItemType Directory -Path $reportsDir | Out-Null
    Write-Success "Created reports directory"
}

# 3. Start Backend Service
Write-Info "Starting Backend API (Port 8000)..."
$backendProcess = Start-Process python -ArgumentList "-m uvicorn app.main:app --reload --port 8000" -PassThru -NoNewWindow
Pop-Location

# 4. Start Frontend Service
Write-Info "Starting Frontend Service (Port 3000)..."
Push-Location frontend
$frontendProcess = Start-Process python -ArgumentList "-m http.server 3000" -PassThru -NoNewWindow
Pop-Location

# 5. Launch Browser
$url = "http://localhost:3000"
Write-Success "AlphaMapping is taking off!"
Write-Success "Dashboard: $url"
Write-Info "Backend API: http://localhost:8000/docs"

Start-Process $url

Write-Warn "Services are running in background. Close this window to keep them running, or manually stop python processes to exit."
