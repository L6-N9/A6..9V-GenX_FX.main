@echo off
echo ========================================
echo GenX FX Complete 24/7 Trading System
echo ========================================
echo.

REM Set console to UTF-8 for proper emoji display
chcp 65001 >nul 2>&1

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Install required packages
echo [1/4] Installing required packages...
pip install requests fastapi uvicorn google-generativeai >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some packages may not have installed correctly
    echo Continuing with available packages...
)

REM Create necessary directories
echo [2/4] Setting up directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backup" mkdir backup

REM Configure Windows Firewall (requires admin)
echo [3/4] Configuring firewall...
netsh advfirewall firewall add rule name="GenX FX API Port 8080" dir=in action=allow protocol=TCP localport=8080 >nul 2>&1
netsh advfirewall firewall add rule name="GenX FX EA Port 9090" dir=in action=allow protocol=TCP localport=9090 >nul 2>&1
netsh advfirewall firewall add rule name="GenX FX VPS Outbound" dir=out action=allow protocol=TCP remoteport=8080 remoteip=34.71.143.222 >nul 2>&1

REM Set environment variables
echo [4/4] Setting environment variables...
set GEMINI_API_KEY=your_gemini_api_key_here
set EXNESS_LOGIN=your_exness_login
set EXNESS_PASSWORD=your_exness_password
set EXNESS_SERVER=Exness-MT5Trial8
set SECRET_KEY=your_secret_key_here

echo.
echo ========================================
echo Starting GenX FX 24/7 System
echo ========================================
echo.

REM Start API server in background
echo Starting API Server...
start "GenX API Server" cmd /k "echo GenX FX API Server && chcp 65001 >nul && python simple-api-server.py"

REM Wait a moment for API server to start
timeout /t 3 /nobreak >nul

REM Start signal generator
echo Starting Gold Signal Generator...
start "GenX Signal Generator" cmd /k "echo GenX FX Gold Signal Generator && chcp 65001 >nul && python genx_robust_backend.py"

echo.
echo ========================================
echo GenX FX System Started Successfully!
echo ========================================
echo.
echo Services Running:
echo   - API Server: http://localhost:8080
echo   - API Docs: http://localhost:8080/docs
echo   - Health Check: http://localhost:8080/health
echo   - Signals: http://localhost:8080/api/v1/signals
echo   - Signal File: MT4_Signals.csv
echo.
echo VPS Integration:
echo   - VPS URL: http://34.71.143.222:8080
echo   - EA Communication: localhost:9090
echo   - Signal File: MT4_Signals.csv (for EA consumption)
echo.
echo Gold Pairs Monitored:
echo   - XAUUSD (Gold/USD) - Primary
echo   - XAUEUR (Gold/EUR) - Secondary
echo   - XAUGBP (Gold/GBP) - Secondary
echo   - XAUAUD (Gold/AUD) - Secondary
echo.
echo Signal Generation:
echo   - Interval: 30 seconds
echo   - Min Confidence: 75%%
echo   - Max Signals/Hour: 8
echo   - AI Analysis: Available (if GEMINI_API_KEY set)
echo.
echo Logs:
echo   - API Server: api-server.log
echo   - Signal Generator: genx-backend.log
echo   - General: logs/ directory
echo.
echo Press any key to open the API documentation...
pause >nul

REM Open API docs in browser
start http://localhost:8080/docs

echo.
echo GenX FX 24/7 Trading System is now running!
echo Close the command windows to stop the services.
echo.
pause
