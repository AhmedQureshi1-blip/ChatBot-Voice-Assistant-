#!/usr/bin/env powershell
<#
Quick Start Jarvis with Ollama (PowerShell Version)
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "JARVIS VOICE ASSISTANT - QUICK START" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "jarvis.py")) {
    Write-Host "Error: jarvis.py not found" -ForegroundColor Red
    Write-Host "Please run this from: C:\Users\Humaira Kaleem\Desktop\Voice Assistant\Python-Voice-Assistant" -ForegroundColor Red
    exit 1
}

# Step 1: Check Ollama
Write-Host "[1/3] Checking Ollama..." -ForegroundColor Yellow
$ollama_status = & .\.venv\Scripts\python.exe check_ollama.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host $ollama_status -ForegroundColor Green
} else {
    Write-Host $ollama_status -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WARNING: Ollama not running" -ForegroundColor Yellow
    Write-Host "Jarvis will work in OFFLINE mode only" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable Ollama, open a NEW PowerShell and run:" -ForegroundColor Yellow
    Write-Host '  & "C:\Users\Humaira Kaleem\AppData\Local\Programs\Ollama\ollama.exe" serve' -ForegroundColor Cyan
    Write-Host ""
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "[2/3] Setting up environment..." -ForegroundColor Yellow
$env:OPENAI_API_KEY = ""
$env:JARVIS_DEBUG = "0"

Write-Host "[3/3] Starting Jarvis..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Type 'help' for commands or just ask a question" -ForegroundColor Green
Write-Host "Type 'quit' to exit" -ForegroundColor Green
Write-Host ""

& .\.venv\Scripts\python.exe jarvis.py

Write-Host ""
Read-Host "Press Enter to exit"
