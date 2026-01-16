<#
.SYNOPSIS
    Restart AlphaMapping Services
.DESCRIPTION
    Stops all running services and starts them again.
#>

Write-Host "================================" -ForegroundColor Cyan
Write-Host "AlphaMapping Restart Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Stop existing services
Write-Host "[1/2] Stopping existing services..." -ForegroundColor Yellow
& "$PSScriptRoot\stop.ps1"

Write-Host ""
Start-Sleep -Seconds 2

# Start services
Write-Host "[2/2] Starting services..." -ForegroundColor Yellow
& "$PSScriptRoot\run.ps1"
