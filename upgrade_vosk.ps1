# Install Better Vosk Model for Improved Recognition
# This downloads the full-size English model (1.8 GB) for better accuracy

param(
    [string]$ModelName = "vosk-model-en-us-0.22"  # Large, accurate model
)

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "     UPGRADING TO BETTER VOSK MODEL FOR ACCURACY               " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Current model: vosk-model-small-en-us-0.15 (40 MB, fast but less accurate)" -ForegroundColor Yellow
Write-Host "New model:     $ModelName (1.8 GB, slower but MUCH more accurate)" -ForegroundColor Green
Write-Host ""

$response = Read-Host "Download large model for better accuracy? (y/N)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Keeping current small model." -ForegroundColor Yellow
    exit 0
}

$ErrorActionPreference = "Stop"

# Paths
$projectRoot = $PSScriptRoot
$modelsDir = Join-Path $projectRoot "models"
$tempDir = Join-Path $projectRoot "temp_downloads"
$targetDir = Join-Path $modelsDir $ModelName

# Create directories
Write-Host ""
Write-Host "[*] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Write-Host "[+] Directories created" -ForegroundColor Green

# URL
$modelUrl = "https://alphacephei.com/vosk/models/$ModelName.zip"

# Download Vosk model
Write-Host ""
Write-Host "[*] Downloading large Vosk model ($ModelName)..." -ForegroundColor Yellow
Write-Host "    Size: ~1.8 GB - This will take several minutes..." -ForegroundColor Cyan
$modelZip = Join-Path $tempDir "vosk_model_large.zip"

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

# Cleanup
Write-Host ""
Write-Host "[*] Cleaning up..." -ForegroundColor Yellow
Remove-Item -Path $tempDir -Recurse -Force
Write-Host "[+] Cleanup complete" -ForegroundColor Green

# Update config
Write-Host ""
Write-Host "[*] Updating configuration..." -ForegroundColor Yellow
$configPath = Join-Path $projectRoot "src\config.py"

if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    
    # Update model path
    $configContent = $configContent -replace 'vosk-model-small-en-us-0\.15', $ModelName
    
    Set-Content -Path $configPath -Value $configContent
    
    Write-Host "[+] Configuration updated to use: $ModelName" -ForegroundColor Green
} else {
    Write-Host "[!] config.py not found, manual update needed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[SUCCESS] BETTER VOSK MODEL INSTALLED!" -ForegroundColor Green
Write-Host ""
Write-Host "Model upgraded:" -ForegroundColor White
Write-Host "  OLD: vosk-model-small-en-us-0.15 (40 MB, basic accuracy)" -ForegroundColor Gray
Write-Host "  NEW: $ModelName (1.8 GB, high accuracy)" -ForegroundColor Green
Write-Host ""
Write-Host "Expected improvements:" -ForegroundColor White
Write-Host "  + Much better word recognition" -ForegroundColor Green
Write-Host "  + Better handling of accents" -ForegroundColor Green
Write-Host "  + More accurate transcription" -ForegroundColor Green
Write-Host "  - Slightly slower processing (~100-200ms extra)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next: Run Pluto again to test improved recognition!" -ForegroundColor Cyan
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
