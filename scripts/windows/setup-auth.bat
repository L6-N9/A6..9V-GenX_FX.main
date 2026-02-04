@echo off
echo 🔐 GenX FX Authentication Setup
echo ===============================

echo 🔑 Setting up Git credentials...
git config --global user.name "KEA MOUYLENG"
git config --global user.email "Lengkundee01@gmail.com"
git config --global credential.helper manager-core

echo ☁️ GCloud authentication (already done)...
echo Current account: lengkundee01@gmail.com
echo Current project: genx-467217

echo 🔥 Firebase authentication...
echo Please run: firebase login
echo Then run: firebase use genx-467217

echo 🌐 AWS authentication...
echo Please run: aws configure
echo Use your AWS credentials

echo 🐳 Docker authentication...
echo Please ensure Docker Desktop is running
echo Then run: docker login

echo ✅ Authentication setup guide complete!
echo 📝 Next steps:
echo   1. Run firebase login
echo   2. Run aws configure  
echo   3. Start Docker Desktop
echo   4. Open GenX_FX.code-workspace in VS Code
pause