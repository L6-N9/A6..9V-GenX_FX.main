@echo off
echo 🔄 GenX FX VS Code Clean Restart
echo =================================

echo 🛑 Closing VS Code...
taskkill /f /im Code.exe 2>nul

echo 🧹 Clearing VS Code cache...
if exist "%APPDATA%\Code\User\workspaceStorage" (
    echo    Clearing workspace storage...
    rmdir /s /q "%APPDATA%\Code\User\workspaceStorage" 2>nul
)

if exist "%APPDATA%\Code\logs" (
    echo    Clearing logs...
    rmdir /s /q "%APPDATA%\Code\logs" 2>nul
)

echo 🔧 Refreshing environment variables...
call refreshenv 2>nul

echo 🐍 Verifying Python environment...
python --version
pip --version

echo ☁️ Verifying Google Cloud CLI...
"%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" --version

echo 📦 Installing additional VS Code Python tools...
pip install pylsp-mypy python-lsp-black python-lsp-isort

echo 🚀 Starting VS Code with clean workspace...
timeout /t 3
start "" code "%~dp0GenX_FX.code-workspace"

echo ✅ VS Code restarted! 
echo 💡 If issues persist:
echo    1. Press Ctrl+Shift+P
echo    2. Type "Python: Select Interpreter"
echo    3. Choose Python 3.13.7
echo    4. Reload window (Ctrl+Shift+P -> "Developer: Reload Window")

pause