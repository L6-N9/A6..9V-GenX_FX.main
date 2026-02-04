@echo off
setlocal enabledelayedexpansion

echo ========================================
echo GenX FX Unified USB Backup System
echo ========================================
echo.

set "BACKUP_DIR=GenX_FX_Backup"
set "SOURCE_DIR=D:\GenX_FX"

if not exist "%SOURCE_DIR%" (
    echo ERROR: Project source directory not found at %SOURCE_DIR%
    echo Please ensure the project is migrated to D: drive.
    pause
    exit /b 1
)

echo [1/3] Detecting available USB drives...
set "found_drives="

for %%d in (E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\" (
        REM Try to detect if it's a USB drive or just a fixed disk
        REM For simplicity in batch, we just check if it exists and is not C: or D:
        if not "%%d"=="C" if not "%%d"=="D" (
            echo Found drive %%d:
            set "found_drives=!found_drives! %%d"
        )
    )
)

if "%found_drives%"=="" (
    echo ERROR: No suitable USB drives detected (E: or higher).
    echo Please connect your USB drive and try again.
    pause
    exit /b 1
)

echo.
echo [2/3] Select backup destination:
echo ----------------------------------------
set "count=0"
for %%d in (%found_drives%) do (
    set /a count+=1
    echo !count!. %%d: drive
    set "drive_!count!=%%d"
)
set /a count+=1
echo !count!. ALL available drives (Redundant Backup)
set "drive_!count!=ALL"

echo.
set /p choice="Enter your choice (1-!count!): "

if "!drive_%choice%!"=="" (
    echo Invalid choice. Exiting.
    pause
    exit /b 1
)

set "target_drives="
if "!drive_%choice%!"=="ALL" (
    set "target_drives=%found_drives%"
) else (
    set "target_drives=!drive_%choice%!"
)

echo.
echo [3/3] Starting backup to: !target_drives!
echo.

for %%d in (%target_drives%) do (
    echo ----------------------------------------
    echo Backing up to %%d:\%BACKUP_DIR%...

    set "TARGET=%%d:\%BACKUP_DIR%"

    if not exist "!TARGET!" mkdir "!TARGET!"
    if not exist "!TARGET!\credentials" mkdir "!TARGET!\credentials"
    if not exist "!TARGET!\configs" mkdir "!TARGET!\configs"
    if not exist "!TARGET!\project" mkdir "!TARGET!\project"
    if not exist "!TARGET!\logs" mkdir "!TARGET!\logs"
    if not exist "!TARGET!\expert-advisors" mkdir "!TARGET!\expert-advisors"

    echo Copying credentials...
    if exist "%SOURCE_DIR%\.env" copy "%SOURCE_DIR%\.env" "!TARGET!\credentials\" /Y
    if exist "%SOURCE_DIR%\amp_auth.json" copy "%SOURCE_DIR%\amp_auth.json" "!TARGET!\credentials\" /Y
    if exist "%SOURCE_DIR%\service-account-key.json" copy "%SOURCE_DIR%\service-account-key.json" "!TARGET!\credentials\" /Y

    echo Copying configs...
    if exist "%SOURCE_DIR%\amp_config.json" copy "%SOURCE_DIR%\amp_config.json" "!TARGET!\configs\" /Y
    if exist "%SOURCE_DIR%\firebase.json" copy "%SOURCE_DIR%\firebase.json" "!TARGET!\configs\" /Y

    echo Copying Expert Advisors...
    if exist "%SOURCE_DIR%\expert-advisors" xcopy "%SOURCE_DIR%\expert-advisors\*" "!TARGET!\expert-advisors\" /E /I /Y /Q

    echo Copying Project Files (Core & Scripts)...
    xcopy "%SOURCE_DIR%\*.py" "!TARGET!\project\" /Y /Q
    xcopy "%SOURCE_DIR%\*.bat" "!TARGET!\project\" /Y /Q
    xcopy "%SOURCE_DIR%\requirements.txt" "!TARGET!\project\" /Y /Q

    echo Copying Logs...
    if exist "%SOURCE_DIR%\logs" xcopy "%SOURCE_DIR%\logs\*" "!TARGET!\logs\" /E /I /Y /Q

    echo.
    echo Backup to %%d: completed!
)

echo.
echo ========================================
echo All backups completed successfully!
echo ========================================
echo.
pause
