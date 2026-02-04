@echo off
echo 🚀 GenX FX VS Code Environment Setup
echo =====================================

echo 🐳 Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout /t 30

echo 📦 Installing Firebase CLI...
npm install -g firebase-tools

echo ☁️ Installing AWS CLI...
winget install Amazon.AWSCLI

echo 🔧 Updating GCloud components...
gcloud components update

echo ✅ Setup complete! Restart VS Code.
pause