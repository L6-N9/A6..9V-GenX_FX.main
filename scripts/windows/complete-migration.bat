@echo off
echo ========================================
echo GenX FX Complete Migration & Deployment
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo This script will:
echo 1. Move GenX FX project from C: to D: drive
echo 2. Set up credentials and backup system
echo 3. Clean up C: drive
echo 4. Deploy to Vultr VPS
echo.
set /p confirm="Continue with complete migration? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Migration cancelled
    pause
    exit /b 0
)

echo.
echo [PHASE 1] Migrating project to D: drive...
call migrate-to-d-drive.bat
if errorlevel 1 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)

echo.
echo [PHASE 2] Setting up credentials...
cd /d "D:\GenX_FX"
call setup-credentials.bat

echo.
echo [PHASE 3] Cleaning up C: drive...
call cleanup-c-drive.bat

echo.
echo [PHASE 4] Testing new setup...
cd /d "D:\GenX_FX"
echo Testing Python and dependencies...
python -c "import requests, json; print('Dependencies OK')"
if errorlevel 1 (
    echo WARNING: Some dependencies may be missing
    echo Run: pip install requests fastapi uvicorn google-generativeai
)

echo.
echo [PHASE 5] Creating VPS deployment script...
echo #!/bin/bash > "D:\GenX_FX\deploy-to-vultr.sh"
echo echo "Deploying GenX FX to Vultr VPS..." >> "D:\GenX_FX\deploy-to-vultr.sh"
echo cd /root >> "D:\GenX_FX\deploy-to-vultr.sh"
echo git clone https://github.com/Mouy-leng/GenX_FX.git >> "D:\GenX_FX\deploy-to-vultr.sh"
echo cd GenX_FX >> "D:\GenX_FX\deploy-to-vultr.sh"
echo pip3 install -r requirements.txt >> "D:\GenX_FX\deploy-to-vultr.sh"
echo python3 simple-api-server.py ^& >> "D:\GenX_FX\deploy-to-vultr.sh"
echo python3 genx_robust_backend.py ^& >> "D:\GenX_FX\deploy-to-vultr.sh"
echo echo "GenX FX deployed and running on VPS!" >> "D:\GenX_FX\deploy-to-vultr.sh"

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo Project Location: D:\GenX_FX
echo Backup Location: E:\GenX_FX_Backup
echo VPS IP: 192.248.146.114
echo.
echo Next Steps:
echo 1. Update API keys in D:\GenX_FX\credentials\api_keys.env
echo 2. Run: D:\GenX_FX\start-genx-d.bat
echo 3. Deploy to VPS using the generated script
echo.
echo To start the system:
echo   D:\GenX_FX\start-genx-d.bat
echo.
echo To create backup:
echo   D:\GenX_FX\backup-to-usb.bat
echo.
pause

