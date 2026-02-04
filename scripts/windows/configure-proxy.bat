@echo off
echo ========================================
echo GenX FX Proxy Configuration Helper
echo ========================================
echo.

REM Check current proxy settings
echo Current proxy configuration:
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable 2>nul
if errorlevel 1 (
    echo No proxy configuration found
) else (
    echo Proxy is configured
    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer 2>nul
    if not errorlevel 1 (
        echo Proxy server details found
    )
)

echo.
echo Options:
echo 1. Configure proxy settings
echo 2. Disable proxy
echo 3. Test connectivity
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Enter proxy configuration:
    set /p proxy_server="Proxy server (e.g., proxy.company.com:8080): "
    set /p proxy_bypass="Bypass for (e.g., localhost;127.0.0.1;*.local): "
    
    if not "%proxy_server%"=="" (
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d "%proxy_server%" /f
        
        if not "%proxy_bypass%"=="" (
            reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "%proxy_bypass%" /f
        )
        
        echo Proxy configured successfully
        echo Please restart your applications for changes to take effect
    ) else (
        echo Invalid proxy server
    )
) else if "%choice%"=="2" (
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
    echo Proxy disabled
) else if "%choice%"=="3" (
    echo Testing connectivity...
    echo.
    echo Testing direct connection:
    ping -n 1 8.8.8.8
    echo.
    echo Testing VPS connection:
    curl -s --connect-timeout 5 http://34.71.143.222:8080/health
    echo.
    echo Testing local API:
    curl -s --connect-timeout 5 http://localhost:8080/health
) else if "%choice%"=="4" (
    exit /b 0
) else (
    echo Invalid choice
)

echo.
pause
