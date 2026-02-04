@echo off
echo 🚀 GenX FX Immediate Startup - Gold Trading Signals
echo ==================================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Install minimal dependencies
echo 📦 Installing essential packages...
pip install requests fastapi uvicorn
if errorlevel 1 (
    echo ❌ Failed to install packages
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Start the backend API
echo 🚀 Starting GenX FX Backend API...
start "GenX Backend API" cmd /k "cd /d %~dp0 && python -m uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload"

REM Wait a moment for API to start
timeout /t 3 /nobreak >nul

REM Start the gold signal generator
echo 🥇 Starting Gold Signal Generator...
start "Gold Signal Generator" cmd /k "cd /d %~dp0 && python gold-signal-generator.py"

echo.
echo ✅ GenX FX System Started!
echo.
echo 📊 Services Running:
echo   • Backend API: http://localhost:8080
echo   • API Docs: http://localhost:8080/docs
echo   • Health Check: http://localhost:8080/health
echo   • Gold Signals: MT4_Signals.csv
echo.
echo 📡 VPS Integration:
echo   • VPS URL: http://34.71.143.222:8080
echo   • Signal file: MT4_Signals.csv (for EA consumption)
echo   • EA can read from: http://34.71.143.222:8080/MT4_Signals.csv
echo.
echo 🎯 Gold Pairs Monitored:
echo   • XAUUSD (Gold/USD) - Primary
echo   • XAUEUR (Gold/EUR) - Secondary  
echo   • XAUGBP (Gold/GBP) - Secondary
echo   • XAUAUD (Gold/AUD) - Secondary
echo.
echo 📈 Signal Generation:
echo   • Interval: 30 seconds
echo   • Min Confidence: 75%%
echo   • Max Signals/Hour: 8
echo   • AI Analysis: Available (if GEMINI_API_KEY set)
echo.
echo Press any key to open the API documentation...
pause >nul

REM Open API docs in browser
start http://localhost:8080/docs

echo.
echo 🎉 GenX FX Gold Trading System is now running 24/7!
echo Close the command windows to stop the services.
