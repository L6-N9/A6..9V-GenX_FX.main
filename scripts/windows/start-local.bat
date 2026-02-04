@echo off
echo 🚀 Starting GenX-FX Local Server...
start "Backend API" python api/main.py
timeout /t 3
start "Frontend" npx serve dist -p 3000
echo ✅ GenX-FX is running locally:
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8080
echo 📊 API Docs: http://localhost:8080/docs
pause