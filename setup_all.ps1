# Master Installation Script for Project Pluto
# Automates complete setup: Piper TTS + Vosk STT models

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "     PROJECT PLUTO - COMPLETE AUTOMATED SETUP                   " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will install:" -ForegroundColor White
Write-Host "  1. Piper TTS (binary + voice model)" -ForegroundColor Cyan
Write-Host "  2. Vosk STT (speech recognition model)" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install Piper
Write-Host "=================================================================" -ForegroundColor Yellow
Write-Host "STEP 1/2: Installing Piper TTS" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Yellow
Write-Host ""

& "$PSScriptRoot\install_piper.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[-] Piper installation failed. Aborting." -ForegroundColor Red
    exit 1
}

# Step 2: Install Vosk
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Yellow
Write-Host "STEP 2/2: Installing Vosk STT Model" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Yellow
Write-Host ""

& "$PSScriptRoot\install_vosk.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[-] Vosk installation failed. Aborting." -ForegroundColor Red
    exit 1
}

# Final summary
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "     [SUCCESS] PROJECT PLUTO SETUP COMPLETE!                    " -ForegroundColor Green
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installation Summary:" -ForegroundColor White
Write-Host "  [+] Piper TTS binary installed" -ForegroundColor Green
Write-Host "  [+] Piper voice model installed (60 MB)" -ForegroundColor Green
Write-Host "  [+] Vosk STT model installed (40 MB)" -ForegroundColor Green
Write-Host "  [+] Ollama + Qwen2.5 (already installed by user)" -ForegroundColor Green
Write-Host ""
Write-Host "Ready to launch!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Run pre-flight check:" -ForegroundColor Yellow
Write-Host "     .\check_setup.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Start Ollama server (in separate terminal):" -ForegroundColor Yellow
Write-Host "     ollama serve" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Activate virtual environment and run Pluto:" -ForegroundColor Yellow
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "     python run.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host ""
