@echo off
echo ========================================
echo GenX FX D: Drive Setup Test
echo ========================================
echo.

REM Change to D: drive and GenX_FX directory
echo Changing to D:\GenX_FX...
cd /d "D:\GenX_FX"

if not exist "D:\GenX_FX" (
    echo ERROR: D:\GenX_FX directory not found!
    echo Please run organize-d-drive.bat first
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

echo ========================================
echo Step 1: Checking project structure
echo ========================================

REM Check for essential files
echo Checking for essential files...

if exist "genx_master_cli.py" (
    echo ✓ genx_master_cli.py found
) else (
    echo ✗ genx_master_cli.py missing
)

if exist "genx_unified_cli.py" (
    echo ✓ genx_unified_cli.py found
) else (
    echo ✗ genx_unified_cli.py missing
)

if exist "requirements.txt" (
    echo ✓ requirements.txt found
) else (
    echo ✗ requirements.txt missing
)

if exist "api\main.py" (
    echo ✓ API main.py found
) else (
    echo ✗ API main.py missing
)

if exist "expert-advisors" (
    echo ✓ expert-advisors folder found
) else (
    echo ✗ expert-advisors folder missing
)

echo.

echo ========================================
echo Step 2: Testing Python environment
echo ========================================

echo Testing Python installation...
python --version
if %errorLevel% == 0 (
    echo ✓ Python is working
) else (
    echo ✗ Python not found or not working
)

echo.
echo Testing pip installation...
pip --version
if %errorLevel% == 0 (
    echo ✓ pip is working
) else (
    echo ✗ pip not found or not working
)

echo.

echo ========================================
echo Step 3: Testing main CLI
echo ========================================

echo Testing genx_master_cli.py...
python genx_master_cli.py --help
if %errorLevel% == 0 (
    echo ✓ genx_master_cli.py is working
) else (
    echo ✗ genx_master_cli.py has issues
)

echo.

echo ========================================
echo Step 4: Testing API server
echo ========================================

echo Testing API server startup...
echo Starting API server in background...

REM Start API server in background
start /b python -m uvicorn api.main:app --host 0.0.0.0 --port 8080

REM Wait a moment for server to start
timeout /t 5 /nobreak >nul

REM Test API endpoint
echo Testing API health endpoint...
curl -s http://localhost:8080/health || echo "API server not responding"

REM Stop the background process
taskkill /f /im python.exe >nul 2>&1

echo.

echo ========================================
echo Step 5: Testing backup system
echo ========================================

echo Checking E: drive backup...
if exist "E:\GenX_FX_Backup" (
    echo ✓ E: drive backup folder exists
    if exist "E:\GenX_FX_Backup\credentials" (
        echo ✓ Credentials backup folder exists
    ) else (
        echo ✗ Credentials backup folder missing
    )
    if exist "E:\GenX_FX_Backup\configs" (
        echo ✓ Configs backup folder exists
    ) else (
        echo ✗ Configs backup folder missing
    )
) else (
    echo ✗ E: drive backup not set up
    echo Run setup-e-drive-backup.bat to set up backup
)

echo.

echo ========================================
echo Step 6: Testing file permissions
echo ========================================

echo Testing file write permissions...
echo Test file > test_write.tmp
if exist "test_write.tmp" (
    echo ✓ Write permissions working
    del test_write.tmp
) else (
    echo ✗ Write permissions issue
)

echo.

echo ========================================
echo Step 7: Checking disk space
echo ========================================

echo Checking D: drive space...
for /f "tokens=3" %%a in ('dir D:\ /-c ^| find "bytes free"') do echo D: drive free space: %%a bytes

echo.
echo Checking E: drive space (if available)...
if exist "E:\" (
    for /f "tokens=3" %%a in ('dir E:\ /-c ^| find "bytes free"') do echo E: drive free space: %%a bytes
) else (
    echo E: drive not available
)

echo.

echo ========================================
echo Step 8: Testing trading system components
echo ========================================

echo Testing gold signal generator...
if exist "gold-signal-generator.py" (
    echo ✓ gold-signal-generator.py found
    python gold-signal-generator.py --test
    if %errorLevel% == 0 (
        echo ✓ Gold signal generator working
    ) else (
        echo ✗ Gold signal generator has issues
    )
) else (
    echo ✗ gold-signal-generator.py missing
)

echo.

echo Testing robust backend...
if exist "genx_robust_backend.py" (
    echo ✓ genx_robust_backend.py found
) else (
    echo ✗ genx_robust_backend.py missing
)

echo.

echo ========================================
echo Test Summary
echo ========================================
echo.
echo Project location: D:\GenX_FX
echo Current working directory: %CD%
echo.
echo Next steps:
echo 1. If any tests failed, check the error messages above
echo 2. Run organize-d-drive.bat to fix any issues
echo 3. Run setup-e-drive-backup.bat to set up backup
echo 4. Test the trading system with: python genx_master_cli.py
echo.
echo To start the trading system:
echo - Run: start-simple.bat
echo - Or: python genx_master_cli.py
echo.
pause
