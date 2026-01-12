# launch.ps1 - GuardianSensor Launcher for Windows
param(
    [string]$Command = "help",
    [int]$Port = 8000
)

Write-Host "`n🚗 GuardianSensor Launcher" -ForegroundColor Yellow
Write-Host "==========================" -ForegroundColor Yellow
Write-Host ""

switch ($Command.ToLower()) {
    "api" {
        Write-Host "Starting API on port $Port..." -ForegroundColor Cyan
        if (Test-Path "venv\Scripts\activate.ps1") {
            & .\venv\Scripts\activate.ps1
        }
        & uvicorn api.main:app --host 0.0.0.0 --port $Port --reload
    }
    
    "dashboard" {
        Write-Host "Starting Dashboard on port 8501..." -ForegroundColor Cyan
        if (Test-Path "venv\Scripts\activate.ps1") {
            & .\venv\Scripts\activate.ps1
        }
        & streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
    }
    
    "test" {
        Write-Host "Running tests..." -ForegroundColor Cyan
        if (Test-Path "venv\Scripts\activate.ps1") {
            & .\venv\Scripts\activate.ps1
        }
        & python -m pytest tests/ -v
    }
    
    "process" {
        Write-Host "Running signal processing..." -ForegroundColor Cyan
        if (Test-Path "venv\Scripts\activate.ps1") {
            & .\venv\Scripts\activate.ps1
        }
        & python run.py process
    }
    
    "simulate" {
        Write-Host "Generating simulation data..." -ForegroundColor Cyan
        if (Test-Path "venv\Scripts\activate.ps1") {
            & .\venv\Scripts\activate.ps1
        }
        & python run.py simulate
    }
    
    "setup" {
        Write-Host "Setting up environment..." -ForegroundColor Cyan
        & .\scripts\setup.ps1
    }
    
    "docker" {
        Write-Host "Building Docker image..." -ForegroundColor Cyan
        & docker build -t guardiansensor:latest .
    }
    
    "help" {
        Write-Host "Available commands:" -ForegroundColor Green
        Write-Host "  .\launch.ps1 api [port]     - Start API (default: 8000)" -ForegroundColor White
        Write-Host "  .\launch.ps1 dashboard      - Start Dashboard" -ForegroundColor White
        Write-Host "  .\launch.ps1 test           - Run tests" -ForegroundColor White
        Write-Host "  .\launch.ps1 process        - Run signal processing" -ForegroundColor White
        Write-Host "  .\launch.ps1 simulate       - Generate simulation data" -ForegroundColor White
        Write-Host "  .\launch.ps1 setup          - Setup environment" -ForegroundColor White
        Write-Host "  .\launch.ps1 docker         - Build Docker image" -ForegroundColor White
        Write-Host "  .\launch.ps1 help           - Show this help" -ForegroundColor White
    }
    
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use: .\launch.ps1 help" -ForegroundColor Yellow
    }
}