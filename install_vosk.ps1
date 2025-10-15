# Automated Vosk STT Model Installation Script for Project Pluto
# This script downloads and extracts Vosk speech recognition model automatically

param(
    [string]$ModelName = "vosk-model-small-en-us-0.15"
)

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "        VOSK STT - AUTOMATED MODEL INSTALLATION                 " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Paths
$projectRoot = $PSScriptRoot
$modelsDir = Join-Path $projectRoot "models"
$tempDir = Join-Path $projectRoot "temp_downloads"
$targetDir = Join-Path $modelsDir $ModelName

# Create directories
Write-Host "[*] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Write-Host "[+] Directories created" -ForegroundColor Green

# URLs
$modelUrl = "https://alphacephei.com/vosk/models/$ModelName.zip"

# Check if already installed
if (Test-Path $targetDir) {
    Write-Host ""
    Write-Host "[!] Vosk model already exists at:" -ForegroundColor Yellow
    Write-Host "    $targetDir" -ForegroundColor Cyan
    $response = Read-Host "    Do you want to re-download? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host ""
        Write-Host "[SUCCESS] Using existing Vosk model" -ForegroundColor Green
        Write-Host ""
        exit 0
    }
    Remove-Item -Path $targetDir -Recurse -Force
}

# Download Vosk model
Write-Host ""
Write-Host "[*] Downloading Vosk model ($ModelName)..." -ForegroundColor Yellow
Write-Host "    This may take a few minutes (~40 MB)..." -ForegroundColor Cyan
$modelZip = Join-Path $tempDir "vosk_model.zip"

try {
    Invoke-WebRequest -Uri $modelUrl -OutFile $modelZip -UseBasicParsing
    $zipSize = (Get-Item $modelZip).Length / 1MB
    $zipSizeRounded = [math]::Round($zipSize, 1)
    Write-Host "[+] Vosk model downloaded ($zipSizeRounded MB)" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to download Vosk model" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual download: $modelUrl" -ForegroundColor Yellow
    exit 1
}

# Extract Vosk model
Write-Host ""
Write-Host "[*] Extracting Vosk model..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $modelZip -DestinationPath $modelsDir -Force
    Write-Host "[+] Vosk model extracted to: models\$ModelName\" -ForegroundColor Green
} catch {
    Write-Host "[-] Failed to extract Vosk model" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    exit 1
}

# Cleanup temp files
Write-Host ""
Write-Host "[*] Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path $tempDir -Recurse -Force
Write-Host "[+] Cleanup complete" -ForegroundColor Green

# Verify model files
Write-Host ""
Write-Host "[*] Verifying model files..." -ForegroundColor Yellow
$requiredFiles = @("am/final.mdl", "conf/model.conf", "graph/HCLr.fst")
$allFilesPresent = $true

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $targetDir $file
    if (-not (Test-Path $filePath)) {
        Write-Host "[-] Missing file: $file" -ForegroundColor Red
        $allFilesPresent = $false
    }
}

if ($allFilesPresent) {
    Write-Host "[+] All required model files present" -ForegroundColor Green
} else {
    Write-Host "[-] Model verification failed" -ForegroundColor Red
    exit 1
}

# Update config.py
Write-Host ""
Write-Host "[*] Updating configuration..." -ForegroundColor Yellow
$configPath = Join-Path $projectRoot "src\config.py"

if (Test-Path $configPath) {
    $voskModelPath = Join-Path $projectRoot "models\$ModelName"
    $voskModelPath = $voskModelPath -replace '\\', '/'
    
    Write-Host "    Vosk model: $voskModelPath" -ForegroundColor Cyan
    Write-Host "[+] Configuration paths ready" -ForegroundColor Green
    Write-Host ""
    Write-Host "    Note: config.py uses this path:" -ForegroundColor Yellow
    Write-Host "      VOSK_CONFIG['model_path'] = 'models/$ModelName'" -ForegroundColor Cyan
} else {
    Write-Host "[!] config.py not found, skipping update" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[SUCCESS] VOSK MODEL INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "Files installed:" -ForegroundColor White
Write-Host "   +- models\$ModelName\" -ForegroundColor Cyan
Write-Host "      +- am/final.mdl         (Acoustic model)" -ForegroundColor Gray
Write-Host "      +- conf/model.conf      (Configuration)" -ForegroundColor Gray
Write-Host "      +- graph/               (Language graph)" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "   1. Run pre-flight check: .\check_setup.ps1" -ForegroundColor Yellow
Write-Host "   2. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "   3. Start Pluto: python run.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
