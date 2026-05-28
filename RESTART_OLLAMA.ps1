#!/usr/bin/env powershell
<#
Restart Ollama Service
This script safely stops Ollama and starts it fresh
#>

Write-Host "Restarting Ollama..." -ForegroundColor Cyan
Write-Host ""

# Try to stop existing Ollama processes
Write-Host "Step 1: Stopping existing Ollama processes..." -ForegroundColor Yellow
Get-Process -Name ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Kill any lingering processes on port 11434
Write-Host "Step 2: Clearing port 11434..." -ForegroundColor Yellow
$processes = netstat -ano 2>$null | Select-String "11434" | ForEach-Object { ($_ -split '\s+')[-1] }
if ($processes) {
    $processes | ForEach-Object {
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 2

# Start Ollama fresh
Write-Host "Step 3: Starting Ollama service..." -ForegroundColor Yellow
$ollama_exe = "C:\Users\Humaira Kaleem\AppData\Local\Programs\Ollama\ollama.exe"

if (Test-Path $ollama_exe) {
    & $ollama_exe serve
}
else {
    Write-Host "Error: Ollama not found at $ollama_exe" -ForegroundColor Red
    exit 1
}
