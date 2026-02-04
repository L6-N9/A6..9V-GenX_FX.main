@echo off
set /a count=1
:loop
echo === Test Cycle %count% ===
python -m pytest tests/ --tb=short
if errorlevel 1 (
    echo Tests failed. Fix and continue...
    pause
)
git add .
git commit -m "Test cycle %count% - fixes applied"
git push origin main
echo Deploying to environment...
timeout /t 300
set /a count+=1
goto loop