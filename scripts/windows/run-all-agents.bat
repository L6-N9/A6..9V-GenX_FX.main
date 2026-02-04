@echo off
echo 🚀 GenX FX Multi-Agent Deployment Launcher
echo ==========================================
echo.
echo Starting 4 agents in parallel...
echo.

echo 🌐 Agent 1: Frontend Deployment (Firebase)
start "Agent 1 - Frontend" cmd /k "echo Agent 1 - Frontend Specialist && cd client && npm install && npm run build && firebase deploy --only hosting && echo ✅ Frontend deployment complete!"

timeout /t 2

echo ☁️ Agent 2: Backend Deployment (Cloud Run)  
start "Agent 2 - Backend" cmd /k "echo Agent 2 - Backend Specialist && gcloud run deploy genx-api --source . --region us-central1 --allow-unauthenticated && echo ✅ Backend deployment complete!"

timeout /t 2

echo 🔐 Agent 3: Authentication Setup
start "Agent 3 - Auth" cmd /k "echo Agent 3 - Authentication Specialist && python firebase_auth.py && firebase login --no-localhost && docker login && echo ✅ Authentication setup complete!"

timeout /t 2

echo 🔗 Agent 4: Integration Testing
start "Agent 4 - Integration" cmd /k "echo Agent 4 - Integration Specialist && python amp_cli.py status && python run_tests.py && echo ✅ Integration testing complete!"

echo.
echo ✅ All 4 agents launched successfully!
echo.
echo 📊 Monitor progress in the opened terminal windows
echo 🎯 Each agent will report completion status
echo.
pause