@echo off
REM run.bat - Simple Windows launcher for GuardianSensor

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║               🚗 GuardianSensor v2.0                     ║
echo ║                                                          ║
echo ║    mmWave Radar Child Safety System                      ║
echo ║    Built for Woven by Toyota Internship Application      ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo A privacy-first child safety system using mmWave radar technology
echo Repository: https://github.com/KazeAsh/GuardianSensor
echo.

if "%1"=="" goto help

if "%1"=="api" goto api
if "%1"=="dashboard" goto dashboard
if "%1"=="process" goto process
if "%1"=="simulate" goto simulate
if "%1"=="test" goto test
if "%1"=="setup" goto setup
if "%1"=="help" goto help

echo Unknown command: %1
goto help

:api
echo 🚀 Starting GuardianSensor API server...
echo    Port: %2 (default: 8000)
echo    Docs: http://localhost:%2/docs
echo.
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
python -m uvicorn api.main:app --host 0.0.0.0 --port %2 --reload
goto end

:dashboard
echo 📊 Starting GuardianSensor Dashboard...
echo    Port: 8501
echo    URL: http://localhost:8501
echo.
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
goto end

:process
echo 🔬 Running mmWave signal processing pipeline...
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
python run.py process
goto end

:simulate
echo 🧪 Generating simulation data...
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
python run.py simulate
goto end

:test
echo 🧪 Running test suite...
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
python run.py test
goto end

:setup
echo 🔧 Setting up development environment...
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    echo ⚠️  requirements.txt not found, installing basic dependencies...
    python -m pip install fastapi uvicorn numpy pandas scipy requests
)
mkdir data\raw\mmwave 2>nul
mkdir data\processed 2>nul
mkdir outputs\visualizations 2>nul
echo.
echo 🎉 Setup complete!
echo To activate the environment next time:
echo    venv\Scripts\activate.bat
goto end

:help
echo.
echo Usage: run.bat [command] [options]
echo.
echo Commands:
echo   api [port]      Start FastAPI server (default port: 8000)
echo   dashboard       Start Streamlit dashboard
echo   process         Run signal processing pipeline
echo   simulate        Generate simulation data
echo   test            Run test suite
echo   setup           Setup development environment
echo   help            Show this help
echo.
echo Examples:
echo   run.bat api
echo   run.bat api 8080
echo   run.bat dashboard
echo   run.bat setup
echo.

:end