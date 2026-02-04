@echo off
echo Starting GenX-FX Local Machine...
echo.
echo [1/3] Starting Backend API...
start "GenX-FX Backend" /min python api/main.py
timeout /t 3 >nul

echo [2/3] Starting Frontend Server...
start "GenX-FX Frontend" /min npx serve dist -p 3000
timeout /t 3 >nul

echo [3/3] Opening Browser...
start http://localhost:3000

echo.
echo === GenX-FX Local Machine Status ===
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8080
echo API Docs: http://localhost:8080/docs
echo.
echo Press any key to stop servers...
pause >nul

taskkill /f /im python.exe /fi "WINDOWTITLE eq GenX-FX Backend"
taskkill /f /im node.exe /fi "WINDOWTITLE eq GenX-FX Frontend"
echo Servers stopped.