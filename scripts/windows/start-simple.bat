@echo off
echo ========================================
echo GenX FX Simple 24/7 Trading System
echo ========================================
echo.

REM Set console to UTF-8
chcp 65001 >nul 2>&1

echo Starting API Server...
start "GenX API Server" cmd /k "echo GenX FX API Server && python simple-api-server.py"

echo Waiting for API server to start...
timeout /t 3 /nobreak >nul

echo Starting Gold Signal Generator...
start "GenX Signal Generator" cmd /k "echo GenX FX Gold Signal Generator && python genx_robust_backend.py"

echo.
echo ========================================
echo GenX FX System Started!
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
echo   - Signal File: MT4_Signals.csv (for EA consumption)
echo.
echo Gold Pairs Monitored:
echo   - XAUUSD (Gold/USD) - Primary
echo   - XAUEUR (Gold/EUR) - Secondary
echo   - XAUGBP (Gold/GBP) - Secondary
echo   - XAUAUD (Gold/AUD) - Secondary
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
