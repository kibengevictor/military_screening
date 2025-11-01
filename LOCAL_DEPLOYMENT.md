# 🚀 Local Deployment - Military AI Screening System

## 📋 Files You Need (All Present ✅)

Your `military_screening` folder already has everything:

```
military_screening/
├── app.py                          ← Flask app (current version)
├── app_with_csv.py                 ← Enhanced with CSV upload ⭐
├── kg.py                           ← Knowledge graph helper
├── gunicorn_conf.py                ← Gunicorn config
├── requirements.txt                ← Python dependencies
├── runtime.txt                     ← Python version
├── Procfile                        ← Process file for deployment
├── render.yaml                     ← Render config
│
├── military_screening_cnn.7z       ← AI model (compressed) ⭐
├── scaler.pkl                      ← Data preprocessor ⭐
├── label_encoder.pkl               ← Label encoder ⭐
├── military_knowledge_graph.pkl    ← Knowledge graph ⭐
│
└── templates/
    └── index.html                  ← Web interface
```

**Status:** ✅ All required files present!

---

## 🚀 OPTION 1: Deploy WITHOUT CSV (Use Current app.py)

### Step 1: Setup Environment

```powershell
# You're already in the right folder
cd "C:\Users\VICTOR KIBENGE\Desktop\Dep\dep\military_screening"

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies

```powershell
# Install all requirements
pip install -r requirements.txt

# This will install:
# - tensorflow-cpu (AI model)
# - flask (web framework)
# - numpy, pandas (data processing)
# - scikit-learn (preprocessing)
# - joblib (model loading)
# - py7zr (extract compressed model)
# - flask-cors (API access)
```

### Step 3: Run the App

```powershell
# Start the Flask app
python app.py

# You should see:
# 🚀 Military AI Screening System Starting...
# 🔄 Loading AI components...
# ✅ Model loaded
# ✅ Scaler loaded
# ✅ Label encoder loaded
# ✅ Knowledge graph loaded
# 🎯 CRITICAL COMPONENTS LOADED - SYSTEM READY!
# 🌐 Starting server on port 5000
```

### Step 4: Test in Browser

```powershell
# Open browser
Start-Process "http://localhost:5000"

# Or manually go to: http://localhost:5000
```

### Step 5: Test the System

1. **Page should load** with Military AI Screening System interface
2. **Click "Candidate A"** (Excellent) → Should show PASS
3. **Click "Candidate B"** (Average) → Should show CONDITIONAL PASS
4. **Click "Candidate C"** (Poor) → Should show FAIL
5. **Check results** show biomarkers and recommended roles

**✅ If all work, your deployment is successful!**

---

## 🚀 OPTION 2: Deploy WITH CSV Upload (Use app_with_csv.py) ⭐ RECOMMENDED

### Step 1: Replace app.py with Enhanced Version

```powershell
# Backup current app.py
Copy-Item app.py app_original_backup.py

# Replace with CSV-enabled version
Copy-Item app_with_csv.py app.py -Force

# Confirm
Write-Host "✅ app.py now has CSV batch processing!"
```

### Step 2: Check if Enhanced Template Exists

```powershell
# Check if enhanced template exists
$enhancedTemplate = ".\templates\index_enhanced.html"
if (Test-Path $enhancedTemplate) {
    # Backup current template
    Copy-Item templates\index.html templates\index_original.html
    # Replace with enhanced version
    Copy-Item templates\index_enhanced.html templates\index.html -Force
    Write-Host "✅ Enhanced template installed!"
} else {
    Write-Host "⚠️ Using existing template (CSV upload may not have UI)"
}
```

### Step 3: Setup Environment (Same as Option 1)

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run Enhanced App

```powershell
# Start the app
python app.py

# Should see same startup messages as Option 1
```

### Step 5: Test Enhanced Features

```powershell
# Open browser
Start-Process "http://localhost:5000"
```

**Test these features:**

1. **Single Candidate Tab**
   - Click demo candidates → All work ✅

2. **Batch CSV Upload Tab** (NEW!)
   - Click "Download CSV Template" → File downloads ✅
   - Upload the template file → Processing works ✅
   - View results table → All candidates shown ✅
   - Click "Download Results" → CSV exports ✅

3. **Help Tab** (NEW!)
   - Documentation visible ✅

**✅ If all features work, enhanced deployment is successful!**

---

## 🧪 Quick Test Script

Save this as `test_deployment.ps1`:

```powershell
# Test Deployment Script
Write-Host "🧪 Testing Military AI Screening System..." -ForegroundColor Cyan

# Test 1: Check files
Write-Host "`n📁 Test 1: Checking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "app.py",
    "scaler.pkl",
    "label_encoder.pkl",
    "military_knowledge_graph.pkl",
    "requirements.txt"
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
} catch {
    Write-Host "  ❌ Python not found!" -ForegroundColor Red
    $allPresent = $false
}

# Test 4: Check if venv exists
Write-Host "`n🌐 Test 4: Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ✅ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Virtual environment not created yet" -ForegroundColor Yellow
    Write-Host "  Run: python -m venv venv" -ForegroundColor Cyan
}

# Summary
Write-Host "`n📊 Summary:" -ForegroundColor Cyan
if ($allPresent) {
    Write-Host "✅ All required files present - Ready to deploy!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Create venv: python -m venv venv" -ForegroundColor White
    Write-Host "2. Activate: .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "3. Install: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "4. Run: python app.py" -ForegroundColor White
    Write-Host "5. Open: http://localhost:5000" -ForegroundColor White
} else {
    Write-Host "❌ Some files are missing - Please check above" -ForegroundColor Red
}
```

Run it:
```powershell
.\test_deployment.ps1
```

---

## 🐛 Troubleshooting

### Problem: "Cannot activate venv"

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Module not found" errors

**Solution:**
```powershell
# Ensure venv is activated (you should see (venv) in prompt)
.\venv\Scripts\Activate.ps1

# Reinstall everything
pip install -r requirements.txt --force-reinstall
```

### Problem: "Model file not found"

**Solution:**
```powershell
# Check if 7z file exists
if (Test-Path "military_screening_cnn.7z") {
    # The app will auto-extract on first run
    # Just run: python app.py
    # It will extract automatically
}
```

### Problem: "Port 5000 already in use"

**Solution:**
```powershell
# Find what's using port 5000
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

# Kill the process or change port in app.py
# Or simply restart your computer
```

### Problem: "Slow startup"

**Solution:**
- First run takes 30-60 seconds (loading AI model)
- Subsequent runs are faster
- This is normal for deep learning models

---

## 📊 Create Test CSV File

If you want to test CSV upload, create a test file:

```powershell
# Quick test CSV generator
$csv = "candidate_id," + (0..560 | ForEach-Object { "feature_$_" }) -join ","
$csv += "`n"

for ($i = 1; $i -le 10; $i++) {
    $row = "TEST_$($i.ToString('000')),"
    $features = 1..561 | ForEach-Object { 
        [math]::Round((Get-Random -Minimum -1.0 -Maximum 1.0), 4) 
    }
    $row += $features -join ","
    $csv += $row + "`n"
}

$csv | Out-File -FilePath "test_10_candidates.csv" -Encoding UTF8
Write-Host "✅ Created test_10_candidates.csv"
```

---

## ✅ Success Checklist

After running the app, verify:

- [ ] Terminal shows "SYSTEM READY!"
- [ ] Browser opens to http://localhost:5000
- [ ] Page displays without errors
- [ ] Demo candidates work (all 3)
- [ ] Results show activity, confidence, decision
- [ ] Biomarkers display correctly
- [ ] Recommended roles appear

**If using CSV version:**
- [ ] CSV template downloads
- [ ] Can upload CSV file
- [ ] Batch processing completes
- [ ] Results table displays
- [ ] Can export results

---

## 🎯 What's Next?

Once local deployment works:

1. **Test thoroughly** - Try all features
2. **Create real test data** - Use realistic sensor values
3. **Document any issues** - Note what doesn't work
4. **Prepare for Render** - Commit changes to GitHub
5. **Deploy to cloud** - Follow Render deployment guide

---

## 📞 Need Help?

- **Check logs** - Terminal shows detailed error messages
- **Read guides** - See DEPLOYMENT_GUIDE.md for details
- **Test components** - Run test_deployment.ps1
- **Check files** - Ensure all .pkl files present

---

## 🚀 Quick Start Command Sequence

**Copy-paste these commands:**

```powershell
# Navigate to project
cd "C:\Users\VICTOR KIBENGE\Desktop\Dep\dep\military_screening"

# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run (choose one)
python app.py              # Option 1: Without CSV
# OR after replacing:
# python app.py            # Option 2: With CSV

# Open browser
Start-Process "http://localhost:5000"
```

**That's it! Your system should be running! 🎉**
