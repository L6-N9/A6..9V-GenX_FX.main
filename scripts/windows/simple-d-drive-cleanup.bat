@echo off
echo ========================================
echo Simple D: Drive Cleanup
echo ========================================
echo.

echo Current D: drive contents:
dir D:\ /b
echo.

echo ========================================
echo Step 1: Check main GenX_FX folder
echo ========================================

if exist "D:\GenX_FX" (
    echo ✓ Main GenX_FX folder found at D:\GenX_FX
    echo.
    echo Main project files:
    dir "D:\GenX_FX" /b | findstr /i "genx\|main\|api\|expert"
    echo.
) else (
    echo ✗ Main GenX_FX folder not found!
    pause
    exit /b 1
)

echo ========================================
echo Step 2: Check for duplicate folders
echo ========================================

if exist "D:\all in once\API key setup file\GenX_FX-1.0.0" (
    echo Found duplicate: D:\all in once\API key setup file\GenX_FX-1.0.0
    echo This folder can be safely deleted after confirming main project is working
) else (
    echo No duplicate GenX_FX-1.0.0 folder found
)

if exist "D:\GenX-EA_Script" (
    echo Found: D:\GenX-EA_Script
    echo This contains EA scripts that should be moved to main project
) else (
    echo No GenX-EA_Script folder found
)

echo.
echo ========================================
echo Step 3: Create organized structure
echo ========================================

REM Create backup folders in main project
if not exist "D:\GenX_FX\backup" mkdir "D:\GenX_FX\backup"
if not exist "D:\GenX_FX\backup\credentials" mkdir "D:\GenX_FX\backup\credentials"
if not exist "D:\GenX_FX\backup\configs" mkdir "D:\GenX_FX\backup\configs"

echo Created backup folders in D:\GenX_FX\backup\

echo.
echo ========================================
echo Step 4: Test main project
echo ========================================

echo Testing main project from D: drive...
cd /d "D:\GenX_FX"

echo Current directory: %CD%
echo.

if exist "genx_master_cli.py" (
    echo ✓ genx_master_cli.py found
    echo Testing CLI...
    python genx_master_cli.py --help
    if %errorLevel% == 0 (
        echo ✓ CLI is working
    ) else (
        echo ✗ CLI has issues
    )
) else (
    echo ✗ genx_master_cli.py not found
)

echo.
echo ========================================
echo Step 5: Setup E: drive backup
echo ========================================

if exist "E:\" (
    echo E: drive found, setting up backup...
    if not exist "E:\GenX_FX_Backup" mkdir "E:\GenX_FX_Backup"
    if not exist "E:\GenX_FX_Backup\credentials" mkdir "E:\GenX_FX_Backup\credentials"
    if not exist "E:\GenX_FX_Backup\configs" mkdir "E:\GenX_FX_Backup\configs"
    
    echo E: drive backup folders created
) else (
    echo E: drive not available for backup
)

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Summary:
echo - Main project: D:\GenX_FX
echo - Backup folders created in main project
echo - E: drive backup setup (if available)
echo.
echo Next steps:
echo 1. Test the system: python genx_master_cli.py
echo 2. Delete duplicate folders if main project works
echo 3. Set up automated backup to E: drive
echo.
pause
