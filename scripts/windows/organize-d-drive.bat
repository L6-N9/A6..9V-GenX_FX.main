@echo off
echo ========================================
echo GenX FX D: Drive Organization Script
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo WARNING: Not running as administrator. Some operations may fail.
    echo.
)

echo Current D: drive structure:
dir D:\ /b
echo.

echo ========================================
echo Step 1: Consolidating GenX FX folders
echo ========================================

REM Check if main GenX_FX folder exists
if exist "D:\GenX_FX" (
    echo Main GenX_FX folder found at D:\GenX_FX
) else (
    echo ERROR: Main GenX_FX folder not found at D:\GenX_FX
    pause
    exit /b 1
)

REM Check for duplicate GenX folders
if exist "D:\all in once\API key setup file\GenX_FX-1.0.0" (
    echo Found duplicate GenX_FX-1.0.0 folder
    echo Moving important files from duplicate folder...
    
    REM Create backup of important files from duplicate folder
    if not exist "D:\GenX_FX\backup\duplicate-files" mkdir "D:\GenX_FX\backup\duplicate-files"
    
    REM Copy any unique files from duplicate folder
    xcopy "D:\all in once\API key setup file\GenX_FX-1.0.0\*" "D:\GenX_FX\backup\duplicate-files\" /E /I /Y /Q
    
    echo Files from duplicate folder backed up to D:\GenX_FX\backup\duplicate-files\
)

if exist "D:\GenX-EA_Script" (
    echo Found GenX-EA_Script folder
    echo Moving EA scripts to main project...
    
    REM Move EA scripts to main project
    if not exist "D:\GenX_FX\expert-advisors\scripts" mkdir "D:\GenX_FX\expert-advisors\scripts"
    xcopy "D:\GenX-EA_Script\*" "D:\GenX_FX\expert-advisors\scripts\" /E /I /Y /Q
    
    echo EA scripts moved to D:\GenX_FX\expert-advisors\scripts\
)

echo.
echo ========================================
echo Step 2: Creating organized folder structure
echo ========================================

REM Create organized folder structure
if not exist "D:\GenX_FX\backup" mkdir "D:\GenX_FX\backup"
if not exist "D:\GenX_FX\backup\credentials" mkdir "D:\GenX_FX\backup\credentials"
if not exist "D:\GenX_FX\backup\configs" mkdir "D:\GenX_FX\backup\configs"
if not exist "D:\GenX_FX\backup\logs" mkdir "D:\GenX_FX\backup\logs"

echo Organized folder structure created:
echo - D:\GenX_FX\backup\credentials
echo - D:\GenX_FX\backup\configs  
echo - D:\GenX_FX\backup\logs

echo.
echo ========================================
echo Step 3: Backing up credentials and configs
echo ========================================

REM Backup important credentials and configs
if exist "D:\GenX_FX\.env" (
    copy "D:\GenX_FX\.env" "D:\GenX_FX\backup\credentials\" /Y
    echo .env file backed up
)

if exist "D:\GenX_FX\amp_config.json" (
    copy "D:\GenX_FX\amp_config.json" "D:\GenX_FX\backup\configs\" /Y
    echo amp_config.json backed up
)

if exist "D:\GenX_FX\amp_auth.json" (
    copy "D:\GenX_FX\amp_auth.json" "D:\GenX_FX\backup\credentials\" /Y
    echo amp_auth.json backed up
)

if exist "D:\GenX_FX\service-account-key.json" (
    copy "D:\GenX_FX\service-account-key.json" "D:\GenX_FX\backup\credentials\" /Y
    echo service-account-key.json backed up
)

echo.
echo ========================================
echo Step 4: Setting up USB backups (E: and F:)
echo ========================================

REM Check if E: drive is available
if exist "E:\" (
    echo E: drive (TOSHIBA) found, setting up backup structure...
    if not exist "E:\GenX_FX_Backup" mkdir "E:\GenX_FX_Backup"
    echo E: drive backup structure ready
)

REM Check if F: drive is available
if exist "F:\" (
    echo F: drive (SSK) found, setting up backup structure...
    if not exist "F:\GenX_FX_Backup" mkdir "F:\GenX_FX_Backup"
    echo F: drive backup structure ready
)

if not exist "E:\" if not exist "F:\" (
    echo WARNING: No USB backup drives (E: or F:) found.
)

echo.
echo ========================================
echo Step 5: Cleaning up duplicate folders
echo ========================================

REM Ask user before deleting duplicate folders
echo Found duplicate folders that can be removed:
if exist "D:\all in once\API key setup file\GenX_FX-1.0.0" echo - D:\all in once\API key setup file\GenX_FX-1.0.0
if exist "D:\GenX-EA_Script" echo - D:\GenX-EA_Script

echo.
set /p cleanup="Do you want to remove duplicate folders? (y/n): "
if /i "%cleanup%"=="y" (
    if exist "D:\all in once\API key setup file\GenX_FX-1.0.0" (
        rmdir /s /q "D:\all in once\API key setup file\GenX_FX-1.0.0"
        echo Removed duplicate GenX_FX-1.0.0 folder
    )
    if exist "D:\GenX-EA_Script" (
        rmdir /s /q "D:\GenX-EA_Script"
        echo Removed GenX-EA_Script folder
    )
) else (
    echo Duplicate folders kept for manual review
)

echo.
echo ========================================
echo Step 6: Creating quick access shortcuts
echo ========================================

REM Create desktop shortcuts for easy access
if exist "%USERPROFILE%\Desktop" (
    echo Creating desktop shortcuts...
    
    REM Create shortcut to main project folder
    powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\GenX_FX.lnk'); $Shortcut.TargetPath = 'D:\GenX_FX'; $Shortcut.Save()"
    
    REM Create shortcut to backup folder
    powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\GenX_FX_Backup.lnk'); $Shortcut.TargetPath = 'D:\GenX_FX\backup'; $Shortcut.Save()"
    
    echo Desktop shortcuts created
)

echo.
echo ========================================
echo Step 7: Updating project paths
echo ========================================

REM Update any hardcoded paths in key files
echo Updating project paths in configuration files...

REM Update .env file if it exists
if exist "D:\GenX_FX\.env" (
    echo Updating .env file paths...
    powershell -Command "(Get-Content 'D:\GenX_FX\.env') -replace 'C:\\\\Users\\\\lengk\\\\GenX_FX-1', 'D:\\\\GenX_FX' | Set-Content 'D:\GenX_FX\.env'"
)

REM Update any batch files with new paths
for /r "D:\GenX_FX" %%f in (*.bat) do (
    echo Updating paths in %%~nxf...
    powershell -Command "(Get-Content '%%f') -replace 'C:\\\\Users\\\\lengk\\\\GenX_FX-1', 'D:\\\\GenX_FX' | Set-Content '%%f'"
)

echo.
echo ========================================
echo Organization Complete!
echo ========================================
echo.
echo Summary:
echo - Main project: D:\GenX_FX
echo - Backup folder: D:\GenX_FX\backup
echo - USB backups: E:\GenX_FX_Backup and F:\GenX_FX_Backup (if available)
echo - Desktop shortcuts created for easy access
echo - Duplicate folders cleaned up
echo - Configuration files updated with new paths
echo.
echo Next steps:
echo 1. Test the system from D:\GenX_FX
echo 2. Set up automated backup to E: drive
echo 3. Update any remaining hardcoded paths
echo.
pause
