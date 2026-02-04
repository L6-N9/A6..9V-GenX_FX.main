@echo off
echo ========================================
echo GenX FX E: Drive Backup Setup
echo ========================================
echo.

REM Check if E: drive is available
if not exist "E:\" (
    echo ERROR: E: drive not found!
    echo Please ensure your USB drive is connected and assigned to E: drive
    pause
    exit /b 1
)

echo E: drive found. Setting up backup system...
echo.

REM Create backup directory structure
echo Creating backup directory structure...
if not exist "E:\GenX_FX_Backup" mkdir "E:\GenX_FX_Backup"
if not exist "E:\GenX_FX_Backup\credentials" mkdir "E:\GenX_FX_Backup\credentials"
if not exist "E:\GenX_FX_Backup\configs" mkdir "E:\GenX_FX_Backup\configs"
if not exist "E:\GenX_FX_Backup\project" mkdir "E:\GenX_FX_Backup\project"
if not exist "E:\GenX_FX_Backup\logs" mkdir "E:\GenX_FX_Backup\logs"
if not exist "E:\GenX_FX_Backup\expert-advisors" mkdir "E:\GenX_FX_Backup\expert-advisors"

echo Backup directories created on E: drive
echo.

REM Copy critical files to E: drive
echo Copying critical files to E: drive backup...

REM Copy credentials
if exist "D:\GenX_FX\.env" (
    copy "D:\GenX_FX\.env" "E:\GenX_FX_Backup\credentials\" /Y
    echo .env file backed up
)

if exist "D:\GenX_FX\amp_auth.json" (
    copy "D:\GenX_FX\amp_auth.json" "E:\GenX_FX_Backup\credentials\" /Y
    echo amp_auth.json backed up
)

if exist "D:\GenX_FX\service-account-key.json" (
    copy "D:\GenX_FX\service-account-key.json" "E:\GenX_FX_Backup\credentials\" /Y
    echo service-account-key.json backed up
)

if exist "D:\GenX_FX\amp-trading-key" (
    copy "D:\GenX_FX\amp-trading-key" "E:\GenX_FX_Backup\credentials\" /Y
    echo amp-trading-key backed up
)

if exist "D:\GenX_FX\amp-trading-key.pub" (
    copy "D:\GenX_FX\amp-trading-key.pub" "E:\GenX_FX_Backup\credentials\" /Y
    echo amp-trading-key.pub backed up
)

REM Copy configs
if exist "D:\GenX_FX\amp_config.json" (
    copy "D:\GenX_FX\amp_config.json" "E:\GenX_FX_Backup\configs\" /Y
    echo amp_config.json backed up
)

if exist "D:\GenX_FX\firebase.json" (
    copy "D:\GenX_FX\firebase.json" "E:\GenX_FX_Backup\configs\" /Y
    echo firebase.json backed up
)

if exist "D:\GenX_FX\docker-compose.yml" (
    copy "D:\GenX_FX\docker-compose.yml" "E:\GenX_FX_Backup\configs\" /Y
    echo docker-compose.yml backed up
)

REM Copy Expert Advisors
if exist "D:\GenX_FX\expert-advisors" (
    xcopy "D:\GenX_FX\expert-advisors\*" "E:\GenX_FX_Backup\expert-advisors\" /E /I /Y /Q
    echo Expert Advisors backed up
)

REM Copy important scripts
if exist "D:\GenX_FX\genx_master_cli.py" (
    copy "D:\GenX_FX\genx_master_cli.py" "E:\GenX_FX_Backup\" /Y
    echo genx_master_cli.py backed up
)

if exist "D:\GenX_FX\genx_unified_cli.py" (
    copy "D:\GenX_FX\genx_unified_cli.py" "E:\GenX_FX_Backup\" /Y
    echo genx_unified_cli.py backed up
)

if exist "D:\GenX_FX\requirements.txt" (
    copy "D:\GenX_FX\requirements.txt" "E:\GenX_FX_Backup\" /Y
    echo requirements.txt backed up
)

REM Copy recent logs
if exist "D:\GenX_FX\logs" (
    xcopy "D:\GenX_FX\logs\*" "E:\GenX_FX_Backup\logs\" /E /I /Y /Q
    echo Logs backed up
)

echo.
echo ========================================
echo Creating automated backup script
echo ========================================

REM Create automated backup script
echo @echo off > "E:\GenX_FX_Backup\backup-genx.bat"
echo echo GenX FX Automated Backup >> "E:\GenX_FX_Backup\backup-genx.bat"
echo echo ================================ >> "E:\GenX_FX_Backup\backup-genx.bat"
echo echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo echo Backing up GenX FX project... >> "E:\GenX_FX_Backup\backup-genx.bat"
echo echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo REM Backup credentials >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\.env" copy "D:\GenX_FX\.env" "E:\GenX_FX_Backup\credentials\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\amp_auth.json" copy "D:\GenX_FX\amp_auth.json" "E:\GenX_FX_Backup\credentials\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\service-account-key.json" copy "D:\GenX_FX\service-account-key.json" "E:\GenX_FX_Backup\credentials\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo REM Backup configs >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\amp_config.json" copy "D:\GenX_FX\amp_config.json" "E:\GenX_FX_Backup\configs\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\firebase.json" copy "D:\GenX_FX\firebase.json" "E:\GenX_FX_Backup\configs\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo REM Backup Expert Advisors >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\expert-advisors" xcopy "D:\GenX_FX\expert-advisors\*" "E:\GenX_FX_Backup\expert-advisors\" /E /I /Y /Q >> "E:\GenX_FX_Backup\backup-genx.bat"
echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo REM Backup important scripts >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\genx_master_cli.py" copy "D:\GenX_FX\genx_master_cli.py" "E:\GenX_FX_Backup\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\genx_unified_cli.py" copy "D:\GenX_FX\genx_unified_cli.py" "E:\GenX_FX_Backup\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo if exist "D:\GenX_FX\requirements.txt" copy "D:\GenX_FX\requirements.txt" "E:\GenX_FX_Backup\" /Y >> "E:\GenX_FX_Backup\backup-genx.bat"
echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo echo Backup completed! >> "E:\GenX_FX_Backup\backup-genx.bat"
echo echo. >> "E:\GenX_FX_Backup\backup-genx.bat"
echo pause >> "E:\GenX_FX_Backup\backup-genx.bat"

echo Automated backup script created: E:\GenX_FX_Backup\backup-genx.bat
echo.

REM Create restore script
echo @echo off > "E:\GenX_FX_Backup\restore-genx.bat"
echo echo GenX FX Restore from Backup >> "E:\GenX_FX_Backup\restore-genx.bat"
echo echo ================================ >> "E:\GenX_FX_Backup\restore-genx.bat"
echo echo. >> "E:\GenX_FX_Backup\restore-genx.bat"
echo echo WARNING: This will overwrite existing files! >> "E:\GenX_FX_Backup\restore-genx.bat"
echo set /p confirm="Are you sure you want to restore? (y/n): " >> "E:\GenX_FX_Backup\restore-genx.bat"
echo if /i not "%%confirm%%"=="y" exit /b >> "E:\GenX_FX_Backup\restore-genx.bat"
echo. >> "E:\GenX_FX_Backup\restore-genx.bat"
echo echo Restoring GenX FX project... >> "E:\GenX_FX_Backup\restore-genx.bat"
echo. >> "E:\GenX_FX_Backup\restore-genx.bat"
echo REM Restore credentials >> "E:\GenX_FX_Backup\restore-genx.bat"
echo if exist "E:\GenX_FX_Backup\credentials\.env" copy "E:\GenX_FX_Backup\credentials\.env" "D:\GenX_FX\" /Y >> "E:\GenX_FX_Backup\restore-genx.bat"
echo if exist "E:\GenX_FX_Backup\credentials\amp_auth.json" copy "E:\GenX_FX_Backup\credentials\amp_auth.json" "D:\GenX_FX\" /Y >> "E:\GenX_FX_Backup\restore-genx.bat"
echo if exist "E:\GenX_FX_Backup\credentials\service-account-key.json" copy "E:\GenX_FX_Backup\credentials\service-account-key.json" "D:\GenX_FX\" /Y >> "E:\GenX_FX_Backup\restore-genx.bat"
echo. >> "E:\GenX_FX_Backup\restore-genx.bat"
echo REM Restore configs >> "E:\GenX_FX_Backup\restore-genx.bat"
echo if exist "E:\GenX_FX_Backup\configs\amp_config.json" copy "E:\GenX_FX_Backup\configs\amp_config.json" "D:\GenX_FX\" /Y >> "E:\GenX_FX_Backup\restore-genx.bat"
echo if exist "E:\GenX_FX_Backup\configs\firebase.json" copy "E:\GenX_FX_Backup\configs\firebase.json" "D:\GenX_FX\" /Y >> "E:\GenX_FX_Backup\restore-genx.bat"
echo. >> "E:\GenX_FX_Backup\restore-genx.bat"
echo REM Restore Expert Advisors >> "E:\GenX_FX_Backup\restore-genx.bat"
echo if exist "E:\GenX_FX_Backup\expert-advisors" xcopy "E:\GenX_FX_Backup\expert-advisors\*" "D:\GenX_FX\expert-advisors\" /E /I /Y /Q >> "E:\GenX_FX_Backup\restore-genx.bat"
echo. >> "E:\GenX_FX_Backup\restore-genx.bat"
echo echo Restore completed! >> "E:\GenX_FX_Backup\restore-genx.bat"
echo echo. >> "E:\GenX_FX_Backup\restore-genx.bat"
echo pause >> "E:\GenX_FX_Backup\restore-genx.bat"

echo Restore script created: E:\GenX_FX_Backup\restore-genx.bat
echo.

echo ========================================
echo E: Drive Backup Setup Complete!
echo ========================================
echo.
echo Summary:
echo - Backup location: E:\GenX_FX_Backup
echo - Credentials backed up to: E:\GenX_FX_Backup\credentials
echo - Configs backed up to: E:\GenX_FX_Backup\configs
echo - Expert Advisors backed up to: E:\GenX_FX_Backup\expert-advisors
echo - Automated backup script: E:\GenX_FX_Backup\backup-genx.bat
echo - Restore script: E:\GenX_FX_Backup\restore-genx.bat
echo.
echo To run automated backup in the future:
echo 1. Connect your USB drive (E:)
echo 2. Run: E:\GenX_FX_Backup\backup-genx.bat
echo.
echo To restore from backup:
echo 1. Connect your USB drive (E:)
echo 2. Run: E:\GenX_FX_Backup\restore-genx.bat
echo.
pause
