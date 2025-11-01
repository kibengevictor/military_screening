# Test Deployment Script
Write-Host "🧪 Testing Military AI Screening System..." -ForegroundColor Cyan

# Test 1: Check files
Write-Host "`n📁 Test 1: Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "app.py",
    "scaler.pkl",
    "label_encoder.pkl",
    "military_knowledge_graph.pkl",
    "requirements.txt",
    "kg.py"
)

$allPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file MISSING!" -ForegroundColor Red
        $allPresent = $false
    }
}

# Test 2: Check model file
Write-Host "`n📦 Test 2: Checking model file..." -ForegroundColor Yellow
if (Test-Path "military_screening_cnn.h5") {
    Write-Host "  ✅ military_screening_cnn.h5 (extracted)" -ForegroundColor Green
} elseif (Test-Path "military_screening_cnn.7z") {
    Write-Host "  ⚠️  military_screening_cnn.7z (needs extraction - app will do this)" -ForegroundColor Yellow
} else {
    Write-Host "  ❌ No model file found!" -ForegroundColor Red
    $allPresent = $false
}

# Test 3: Check Python
Write-Host "`n🐍 Test 3: Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
    
    # Check if version is 3.9+
    if ($pythonVersion -match "Python 3\.(\d+)\.") {
        $minorVersion = [int]$Matches[1]
        if ($minorVersion -lt 9) {
            Write-Host "  ⚠️  Python 3.9+ recommended (you have 3.$minorVersion)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ❌ Python not found!" -ForegroundColor Red
    $allPresent = $false
}

# Test 4: Check if venv exists
Write-Host "`n🌐 Test 4: Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✅ Virtual environment exists" -ForegroundColor Green
    
    # Check if it's activated
    if ($env:VIRTUAL_ENV) {
        Write-Host "  ✅ Virtual environment is ACTIVATED" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Virtual environment exists but NOT activated" -ForegroundColor Yellow
        Write-Host "  Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ⚠️  Virtual environment not created yet" -ForegroundColor Yellow
    Write-Host "  Run: python -m venv venv" -ForegroundColor Cyan
}

# Test 5: Check templates folder
Write-Host "`n📄 Test 5: Checking templates..." -ForegroundColor Yellow
if (Test-Path "templates\index.html") {
    Write-Host "  ✅ templates\index.html" -ForegroundColor Green
} else {
    Write-Host "  ❌ templates\index.html MISSING!" -ForegroundColor Red
    $allPresent = $false
}

if (Test-Path "templates\index_enhanced.html") {
    Write-Host "  ✅ templates\index_enhanced.html (CSV version available)" -ForegroundColor Green
}

# Test 6: Check enhanced app
Write-Host "`n🚀 Test 6: Checking for enhanced features..." -ForegroundColor Yellow
if (Test-Path "app_with_csv.py") {
    Write-Host "  ✅ app_with_csv.py (CSV batch processing available)" -ForegroundColor Green
    Write-Host "  💡 To use: Copy-Item app_with_csv.py app.py -Force" -ForegroundColor Cyan
}

# Test 7: Check if dependencies are installed (if venv is activated)
if ($env:VIRTUAL_ENV) {
    Write-Host "`n📦 Test 7: Checking installed packages..." -ForegroundColor Yellow
    $requiredPackages = @("flask", "tensorflow", "numpy", "scikit-learn", "joblib", "pandas")
    
    foreach ($package in $requiredPackages) {
        $installed = pip show $package 2>$null
        if ($installed) {
            Write-Host "  ✅ $package" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $package NOT INSTALLED" -ForegroundColor Red
        }
    }
} else {
    Write-Host "`n📦 Test 7: Package check skipped (activate venv first)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "📊 SUMMARY" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Cyan

if ($allPresent) {
    Write-Host "`n✅ All required files present - Ready to deploy!" -ForegroundColor Green
    
    Write-Host "`n🚀 Quick Start Commands:" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    
    if (-not (Test-Path "venv")) {
        Write-Host "1. python -m venv venv" -ForegroundColor White
        Write-Host "2. .\venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host "3. pip install -r requirements.txt" -ForegroundColor White
        Write-Host "4. python app.py" -ForegroundColor White
        Write-Host "5. Start-Process 'http://localhost:5000'" -ForegroundColor White
    } elseif (-not $env:VIRTUAL_ENV) {
        Write-Host "1. .\venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host "2. pip install -r requirements.txt" -ForegroundColor White
        Write-Host "3. python app.py" -ForegroundColor White
        Write-Host "4. Start-Process 'http://localhost:5000'" -ForegroundColor White
    } else {
        Write-Host "1. pip install -r requirements.txt  (if not done)" -ForegroundColor White
        Write-Host "2. python app.py" -ForegroundColor White
        Write-Host "3. Start-Process 'http://localhost:5000'" -ForegroundColor White
    }
    
    Write-Host "`n💡 To enable CSV batch processing:" -ForegroundColor Cyan
    Write-Host "   Copy-Item app_with_csv.py app.py -Force" -ForegroundColor White
    
} else {
    Write-Host "`n❌ Some files are missing - Please check above" -ForegroundColor Red
    Write-Host "   Review the ❌ items and ensure all files are present" -ForegroundColor Yellow
}

Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "✅ Test Complete!" -ForegroundColor Green
Write-Host ("="*60) -ForegroundColor Cyan
