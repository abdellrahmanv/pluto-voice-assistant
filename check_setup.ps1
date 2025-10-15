# 🔍 Project Pluto - Pre-Flight Checklist Script
# Run this before starting Pluto to verify everything is ready

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           🪐 PROJECT PLUTO - PRE-FLIGHT CHECK 🪐                 ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Python version
Write-Host "🐍 Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.([89]|1[0-9])") {
        Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Python 3.8+ required, found: $pythonVersion" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "   ❌ Python not found in PATH" -ForegroundColor Red
    $allGood = $false
}

# Check 2: Virtual environment
Write-Host ""
Write-Host "📦 Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "   ✅ Virtual environment exists" -ForegroundColor Green
    
    # Check if activated
    $currentPython = python -c "import sys; print(sys.prefix)" 2>&1
    if ($currentPython -like "*pluto\venv*") {
        Write-Host "   ✅ Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Virtual environment not activated" -ForegroundColor Yellow
        Write-Host "      Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Virtual environment not found" -ForegroundColor Red
    Write-Host "      Run: python -m venv venv" -ForegroundColor Yellow
    $allGood = $false
}

# Check 3: Dependencies
Write-Host ""
Write-Host "📚 Checking Python dependencies..." -ForegroundColor Yellow
$requiredPackages = @("vosk", "pyaudio", "requests", "psutil", "numpy")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    $installed = python -c "import $package" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $package installed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $package NOT installed" -ForegroundColor Red
        $missingPackages += $package
        $allGood = $false
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "      Run: pip install -r requirements.txt" -ForegroundColor Yellow
}

# Check 4: Vosk model
Write-Host ""
Write-Host "🎤 Checking Vosk STT model..." -ForegroundColor Yellow
if (Test-Path "models\vosk-model-small-en-us-0.15") {
    $voskFiles = Get-ChildItem "models\vosk-model-small-en-us-0.15" -Recurse | Measure-Object
    Write-Host "   ✅ Vosk model found ($($voskFiles.Count) files)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Vosk model NOT found" -ForegroundColor Red
    Write-Host "      Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -ForegroundColor Yellow
    Write-Host "      Extract to: models\vosk-model-small-en-us-0.15\" -ForegroundColor Yellow
    $allGood = $false
}

# Check 5: Piper model
Write-Host ""
Write-Host "🔊 Checking Piper TTS model..." -ForegroundColor Yellow
if (Test-Path "models\en_US-lessac-medium.onnx") {
    $piperSize = (Get-Item "models\en_US-lessac-medium.onnx").Length / 1MB
    Write-Host "   ✅ Piper model found ($([math]::Round($piperSize, 1)) MB)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Piper model NOT found" -ForegroundColor Red
    Write-Host "      Download: https://github.com/rhasspy/piper/releases" -ForegroundColor Yellow
    Write-Host "      File: en_US-lessac-medium.onnx" -ForegroundColor Yellow
    Write-Host "      Place in: models\" -ForegroundColor Yellow
    $allGood = $false
}

# Check 6: Piper binary
Write-Host ""
Write-Host "🔧 Checking Piper binary..." -ForegroundColor Yellow
try {
    $piperVersion = piper --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Piper binary accessible: $piperVersion" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Piper binary not working" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "   ❌ Piper binary not found in PATH" -ForegroundColor Red
    Write-Host "      Download: https://github.com/rhasspy/piper/releases" -ForegroundColor Yellow
    Write-Host "      Add to PATH or update src\config.py with full path" -ForegroundColor Yellow
    $allGood = $false
}

# Check 7: Ollama server
Write-Host ""
Write-Host "🧠 Checking Ollama server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Ollama server is running" -ForegroundColor Green
    
    # Check model
    $models = ($response.Content | ConvertFrom-Json).models
    $hasQwen = $false
    foreach ($model in $models) {
        if ($model.name -like "*qwen2.5*1.5b*") {
            Write-Host "   ✅ Qwen2.5 model found: $($model.name)" -ForegroundColor Green
            $hasQwen = $true
            break
        }
    }
    
    if (-not $hasQwen) {
        Write-Host "   ⚠️  Qwen2.5 model NOT found" -ForegroundColor Yellow
        Write-Host "      Run: ollama pull qwen2.5:1.5b-instruct-q4_K_M" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   ❌ Ollama server NOT running" -ForegroundColor Red
    Write-Host "      In separate terminal, run: ollama serve" -ForegroundColor Yellow
    $allGood = $false
}

# Check 8: Audio devices
Write-Host ""
Write-Host "🎙️ Checking audio devices..." -ForegroundColor Yellow
try {
    $deviceCount = python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count()); p.terminate()" 2>&1
    if ($deviceCount -match "^\d+$" -and [int]$deviceCount -gt 0) {
        Write-Host "   ✅ Audio devices detected: $deviceCount" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  No audio devices found" -ForegroundColor Yellow
        Write-Host "      Check microphone in Windows Sound Settings" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not check audio devices (PyAudio issue?)" -ForegroundColor Yellow
}

# Check 9: Directory structure
Write-Host ""
Write-Host "📁 Checking directory structure..." -ForegroundColor Yellow
$requiredDirs = @("src", "src\workers", "models", "logs", "tests")
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "   ✅ $dir\" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $dir\ NOT found" -ForegroundColor Red
        $allGood = $false
    }
}

# Final summary
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($allGood) {
    Write-Host ""
    Write-Host "✅ ALL CHECKS PASSED! Ready to run Pluto! 🚀" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start:" -ForegroundColor White
    Write-Host "   python run.py" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ SOME CHECKS FAILED - Fix issues above before running" -ForegroundColor Red
    Write-Host ""
    Write-Host "See HOW_TO_RUN.md for detailed setup instructions" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
