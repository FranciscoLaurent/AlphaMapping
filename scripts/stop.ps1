<#
.SYNOPSIS
    Stop AlphaMapping Services
.DESCRIPTION
    Kills all Python processes to stop the backend and frontend servers.
#>

Write-Host "[INFO] Stopping AlphaMapping Services..." -ForegroundColor Cyan

# Find and kill all Python processes
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "[INFO] Found $($pythonProcesses.Count) Python process(es)" -ForegroundColor Yellow
    
    foreach ($proc in $pythonProcesses) {
        Write-Host "  Stopping PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force
    }
    
    Write-Host "[SUCCESS] All Python processes stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No Python processes found running" -ForegroundColor Yellow
}

# Optional: Also kill any http.server processes
$httpProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*http.server*" }
if ($httpProcesses) {
    Write-Host "[INFO] Stopping HTTP server processes..." -ForegroundColor Yellow
    $httpProcesses | Stop-Process -Force
}

Write-Host "[SUCCESS] AlphaMapping stopped successfully" -ForegroundColor Green
Write-Host ""
Write-Host "To restart, run: .\scripts\run.ps1" -ForegroundColor Cyan
