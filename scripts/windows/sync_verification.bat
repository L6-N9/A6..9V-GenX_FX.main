@echo off
echo ============================================
echo GenX_FX Repository Sync Verification
echo ============================================
echo.

echo [1] Checking current directory...
cd /d "%~dp0"
echo Current directory: %CD%

echo.
echo [2] Checking if this is a Git repository...
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This is not a Git repository or Git is not installed
    echo Please make sure you're in the GenX_FX folder and Git is installed
    pause
    exit /b 1
)

echo [3] Current Git status:
git status

echo.
echo [4] Current branch and remote info:
git branch -vv

echo.
echo [5] Fetching latest changes from GitHub...
git fetch origin

echo.
echo [6] Checking remote repository URL:
git remote get-url origin

echo.
echo [7] Current commit hash (LOCAL):
git rev-parse HEAD

echo.
echo [8] Latest commit hash (REMOTE main):
git rev-parse origin/main

echo.
echo [9] Expected commit hash (from Linux verification):
echo a7c541b4058014610b70c3e6a115ae6673dd53da

echo.
echo [10] Comparison check:
for /f %%i in ('git rev-parse HEAD') do set LOCAL_HASH=%%i
for /f %%i in ('git rev-parse origin/main') do set REMOTE_HASH=%%i

if "%LOCAL_HASH%"=="a7c541b4058014610b70c3e6a115ae6673dd53da" (
    echo ✅ SUCCESS: Your Windows laptop is FULLY SYNCED with the repository!
    echo ✅ Local commit matches the expected Linux commit hash
) else (
    echo ⚠️  WARNING: Your Windows laptop may need updates
    echo Expected: a7c541b4058014610b70c3e6a115ae6673dd53da
    echo Current:  %LOCAL_HASH%
    echo.
    echo To sync your Windows laptop, run:
    echo   git checkout main
    echo   git pull origin main
)

echo.
echo [11] Recent commits (last 5):
git log --oneline -5

echo.
echo ============================================
echo Verification Complete
echo ============================================
pause