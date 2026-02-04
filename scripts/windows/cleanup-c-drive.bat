@echo off
echo ========================================
echo C: Drive Cleanup Script
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo WARNING: This will clean up C: drive to free space
echo Make sure you have backed up important data first!
echo.
set /p confirm="Continue with cleanup? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Cleanup cancelled
    pause
    exit /b 0
)

echo [1/6] Cleaning temporary files...
del /q /f /s "%TEMP%\*" 2>nul
del /q /f /s "C:\Windows\Temp\*" 2>nul
del /q /f /s "C:\Windows\Prefetch\*" 2>nul

echo [2/6] Cleaning browser cache...
del /q /f /s "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache\*" 2>nul
del /q /f /s "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache\*" 2>nul
del /q /f /s "%APPDATA%\Mozilla\Firefox\Profiles\*\cache2\*" 2>nul

echo [3/6] Cleaning Windows Update files...
del /q /f /s "C:\Windows\SoftwareDistribution\Download\*" 2>nul

echo [4/6] Cleaning old log files...
del /q /f /s "C:\Windows\Logs\*" 2>nul
del /q /f /s "C:\Windows\System32\LogFiles\*" 2>nul

echo [5/6] Running disk cleanup...
cleanmgr /sagerun:1

echo [6/6] Removing old GenX FX files from C: drive...
if exist "C:\Users\lengk\GenX_FX-1" (
    echo Removing old project directory...
    rmdir /s /q "C:\Users\lengk\GenX_FX-1" 2>nul
    echo Old project directory removed
)

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Checking drive space after cleanup...
wmic logicaldisk where caption="C:" get size,freespace,caption
echo.
echo C: drive has been cleaned up.
echo You can now use D: drive for your GenX FX project.
echo.
pause

