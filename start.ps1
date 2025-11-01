# Quick Start Script - Military AI Screening System
# This script sets up and runs the application

Write-Host "`n🎯 Military AI Screening System - Quick Start" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Gray

# Step 1: Check if we're in the right directory
$currentDir = Get-Location
if ($currentDir.Path -notlike "*military_screening*") {
    Write-Host "⚠️  Warning: Not in military_screening folder" -ForegroundColor Yellow
    Write-Host "Current location: $currentDir" -ForegroundColor Yellow
    $confirm = Read-Host "Continue anyway? (y/n)"
    if ($confirm -ne 'y') {
        Write-Host "Exiting..." -ForegroundColor Red
        exit
    }
}

# Step 2: Check if venv exists
Write-Host "`n📦 Step 1: Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Step 3: Activate venv
Write-Host "`n🔌 Step 2: Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Could not activate virtual environment" -ForegroundColor Red
    Write-Host "Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit
}

# Step 4: Install dependencies
Write-Host "`n📥 Step 3: Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Step 5: Ask about CSV feature
Write-Host "`n📊 Step 4: CSV Batch Processing Feature" -ForegroundColor Yellow
if (Test-Path "app_with_csv.py") {
    Write-Host "CSV batch processing is available!" -ForegroundColor Cyan
    Write-Host "This allows uploading CSV files with multiple candidates." -ForegroundColor White
    $useCSV = Read-Host "`nEnable CSV feature? (y/n)"
    
    if ($useCSV -eq 'y') {
        # Backup current app.py
        if (Test-Path "app.py") {
            Copy-Item app.py app_backup.py -Force
            Write-Host "✅ Backed up current app.py" -ForegroundColor Green
        }
        # Replace with CSV version
        Copy-Item app_with_csv.py app.py -Force
        Write-Host "✅ CSV batch processing enabled!" -ForegroundColor Green
        
        # Check for enhanced template
        if (Test-Path "templates\index_enhanced.html") {
            Copy-Item templates\index.html templates\index_backup.html -Force -ErrorAction SilentlyContinue
            Copy-Item templates\index_enhanced.html templates\index.html -Force
            Write-Host "✅ Enhanced UI installed" -ForegroundColor Green
        }
    } else {
        Write-Host "ℹ️  Using standard version (no CSV upload)" -ForegroundColor Cyan
    }
}

# Step 6: Start the application
Write-Host "`n🚀 Step 5: Starting the application..." -ForegroundColor Yellow
Write-Host "Please wait while AI model loads (30-60 seconds)..." -ForegroundColor Cyan
Write-Host "`nLook for: 'CRITICAL COMPONENTS LOADED - SYSTEM READY!'" -ForegroundColor White
Write-Host ("="*60) -ForegroundColor Gray
Write-Host "`n"

# Open browser after 5 seconds
Start-Sleep -Seconds 5
Start-Process "http://localhost:5000"

# Start the app
python app.py
