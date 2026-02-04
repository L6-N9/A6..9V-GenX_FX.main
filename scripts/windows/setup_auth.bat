@echo off
echo 🔐 GenX FX Authentication Setup
echo ================================
echo.

echo 📋 Current Authentication Status:
echo UID: qGQFOuQA6seDPGdDmvYgOmD0GAl1
echo.

echo 🔥 Setting up Firebase authentication...
python firebase_auth.py
echo.

echo 🌐 Firebase login (use the UID above when prompted):
firebase login --no-localhost
echo.

echo ☁️ Checking Google Cloud authentication:
gcloud auth list
echo.

echo ✅ Authentication setup complete!
echo.
echo 🚀 Ready to deploy GenX FX system!
pause