@echo off
echo 🚀 GenX FX 24/7 Service Setup
echo =============================

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo 📦 Installing required packages...
pip install pywin32
if errorlevel 1 (
    echo ❌ Failed to install pywin32
    pause
    exit /b 1
)

echo 🔧 Installing Windows service...
python genx_24_7_service.py install
if errorlevel 1 (
    echo ❌ Failed to install service
    pause
    exit /b 1
)

echo 🚀 Starting service...
net start GenX24_7Backend
if errorlevel 1 (
    echo ❌ Failed to start service
    echo Check the logs for details
    pause
    exit /b 1
)

echo ✅ GenX FX 24/7 Service installed and started successfully!
echo.
echo 📊 Service Information:
echo   • Service Name: GenX24_7Backend
echo   • Display Name: GenX FX 24/7 Trading Backend
echo   • Status: Running
echo.
echo 🔧 Management Commands:
echo   • Start: net start GenX24_7Backend
echo   • Stop: net stop GenX24_7Backend
echo   • Restart: net stop GenX24_7Backend && net start GenX24_7Backend
echo   • Remove: python genx_24_7_service.py remove
echo.
echo 📊 Access URLs:
echo   • API: http://localhost:8080
echo   • Docs: http://localhost:8080/docs
echo   • Health: http://localhost:8080/health
echo.
echo 📡 VPS Integration:
echo   • Sending signals to: http://34.71.143.222:8080
echo   • EA Communication: localhost:9090
echo.
pause
