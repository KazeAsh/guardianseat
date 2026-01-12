# scripts/setup.ps1
Write-Host "🔧 GuardianSensor Setup Script" -ForegroundColor Yellow
Write-Host "==============================" -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Cyan
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate
Write-Host "Activating environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
} else {
    Write-Host "⚠️ requirements.txt not found" -ForegroundColor Yellow
    Write-Host "Creating basic requirements.txt..." -ForegroundColor Cyan
    @"
fastapi==0.104.1
uvicorn[standard]==0.24.0
numpy==1.24.3
pandas==2.0.3
scipy==1.11.4
matplotlib==3.8.0
streamlit==1.28.1
requests==2.31.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
    python -m pip install -r requirements.txt
}

# Create directories
Write-Host "`nCreating project directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "data/raw/mmwave" | Out-Null
New-Item -ItemType Directory -Force -Path "data/processed" | Out-Null
New-Item -ItemType Directory -Force -Path "outputs/visualizations" | Out-Null
New-Item -ItemType Directory -Force -Path "outputs/reports" | Out-Null

# Test import
Write-Host "`nTesting imports..." -ForegroundColor Cyan
python -c "
try:
    import fastapi
    import numpy
    import pandas
    print('✅ All imports successful!')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "`nNext time, activate with: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan