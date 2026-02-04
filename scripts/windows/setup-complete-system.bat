@echo off
echo ========================================
echo GenX FX Complete System Setup
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

echo [1/8] Installing Python dependencies...
pip install requests fastapi uvicorn google-generativeai
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo [2/8] Configuring Windows Firewall...
REM Allow inbound connections on port 8080
netsh advfirewall firewall add rule name="GenX FX API Port 8080" dir=in action=allow protocol=TCP localport=8080
if errorlevel 1 (
    echo WARNING: Failed to add firewall rule for port 8080
)

REM Allow inbound connections on port 9090
netsh advfirewall firewall add rule name="GenX FX EA Communication Port 9090" dir=in action=allow protocol=TCP localport=9090
if errorlevel 1 (
    echo WARNING: Failed to add firewall rule for port 9090
)

REM Allow outbound connections to VPS
netsh advfirewall firewall add rule name="GenX FX VPS Outbound" dir=out action=allow protocol=TCP remoteport=8080 remoteip=34.71.143.222
if errorlevel 1 (
    echo WARNING: Failed to add firewall rule for VPS outbound
)

echo [3/8] Creating system directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backup" mkdir backup

echo [4/8] Setting up environment variables...
setx GEMINI_API_KEY "your_gemini_api_key_here" /M
setx EXNESS_LOGIN "your_exness_login" /M
setx EXNESS_PASSWORD "your_exness_password" /M
setx EXNESS_SERVER "Exness-MT5Trial8" /M
setx SECRET_KEY "your_secret_key_here" /M

echo [5/8] Configuring proxy settings (if needed)...
REM Check if proxy is configured
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable >nul 2>&1
if errorlevel 1 (
    echo No proxy configuration found
) else (
    echo Proxy configuration detected - please configure manually if needed
)

echo [6/8] Optimizing Cursor/VSCode settings...
REM Create .vscode settings for optimal development
if not exist ".vscode" mkdir .vscode

echo { > .vscode\settings.json
echo   "python.defaultInterpreterPath": "python", >> .vscode\settings.json
echo   "python.terminal.activateEnvironment": true, >> .vscode\settings.json
echo   "python.linting.enabled": true, >> .vscode\settings.json
echo   "python.linting.pylintEnabled": false, >> .vscode\settings.json
echo   "python.linting.flake8Enabled": true, >> .vscode\settings.json
echo   "files.encoding": "utf8", >> .vscode\settings.json
echo   "terminal.integrated.shell.windows": "cmd.exe", >> .vscode\settings.json
echo   "terminal.integrated.shellArgs.windows": ["/k", "chcp 65001"] >> .vscode\settings.json
echo } >> .vscode\settings.json

echo [7/8] Creating startup scripts...
REM Create robust startup script
echo @echo off > start-genx-robust.bat
echo echo Starting GenX FX Robust Backend Service... >> start-genx-robust.bat
echo chcp 65001 >nul >> start-genx-robust.bat
echo python genx_robust_backend.py >> start-genx-robust.bat
echo pause >> start-genx-robust.bat

REM Create API server script
echo @echo off > start-api-server.bat
echo echo Starting GenX FX API Server... >> start-api-server.bat
echo chcp 65001 >nul >> start-api-server.bat
echo python -m uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload >> start-api-server.bat
echo pause >> start-api-server.bat

echo [8/8] Testing system configuration...
echo Testing Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo Testing network connectivity...
ping -n 1 8.8.8.8 >nul 2>&1
if errorlevel 1 (
    echo WARNING: No internet connectivity detected
) else (
    echo Internet connectivity: OK
)

echo Testing VPS connectivity...
curl -s --connect-timeout 5 http://34.71.143.222:8080/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: VPS not reachable (this is normal if VPS is down)
) else (
    echo VPS connectivity: OK
)

echo.
echo ========================================
echo GenX FX System Setup Complete!
echo ========================================
echo.
echo System Configuration:
echo   - Python: Installed and configured
echo   - Firewall: Ports 8080 and 9090 opened
echo   - Directories: Created (logs, data, backup)
echo   - Environment: Variables set
echo   - VSCode: Settings optimized
echo   - Scripts: Startup scripts created
echo.
echo Available Commands:
echo   - start-genx-robust.bat    : Start robust backend service
echo   - start-api-server.bat     : Start API server only
echo   - python genx_robust_backend.py : Direct Python execution
echo.
echo Next Steps:
echo   1. Set your API keys in environment variables
echo   2. Run: start-genx-robust.bat
echo   3. Monitor logs in logs/ directory
echo.
echo Press any key to continue...
pause >nul
