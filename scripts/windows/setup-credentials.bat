@echo off
echo ========================================
echo GenX FX Credentials Setup
echo ========================================
echo.

echo Setting up secure credential storage...
echo.

REM Create credentials directory
if not exist "D:\GenX_FX\credentials" mkdir "D:\GenX_FX\credentials"
if not exist "E:\GenX_FX_Backup\credentials" mkdir "E:\GenX_FX_Backup\credentials"

echo [1/4] Creating VPS credentials file...
echo # Vultr VPS Credentials > "D:\GenX_FX\credentials\vps_credentials.env"
echo VULTR_SERVER_IP=192.248.146.114 >> "D:\GenX_FX\credentials\vps_credentials.env"
echo VULTR_SERVER_USERNAME=root >> "D:\GenX_FX\credentials\vps_credentials.env"
echo VULTR_SERVER_PASSWORD=g-S2iz=e.D9xql6P >> "D:\GenX_FX\credentials\vps_credentials.env"
echo VULTR_SERVER_OS=Alma Linux 8 x64 >> "D:\GenX_FX\credentials\vps_credentials.env"
echo VULTR_SERVER_LOCATION=London >> "D:\GenX_FX\credentials\vps_credentials.env"

echo [2/4] Creating MT4 account credentials...
echo # MT4 Account Credentials > "D:\GenX_FX\credentials\mt4_credentials.env"
echo MT4_LOGIN=205875 >> "D:\GenX_FX\credentials\mt4_credentials.env"
echo MT4_BROKER=Capital.com-Real >> "D:\GenX_FX\credentials\mt4_credentials.env"
echo MT4_ACCOUNT_1=GoD Mode >> "D:\GenX_FX\credentials\mt4_credentials.env"
echo MT4_BALANCE_1=0.17 >> "D:\GenX_FX\credentials\mt4_credentials.env"
echo MT4_ACCOUNT_2=GoD Mode 2 >> "D:\GenX_FX\credentials\mt4_credentials.env"
echo MT4_BALANCE_2=3.76 >> "D:\GenX_FX\credentials\mt4_credentials.env"
echo MT4_STATUS=Active >> "D:\GenX_FX\credentials\mt4_credentials.env"

echo [3/4] Creating API keys file...
echo # API Keys and Secrets > "D:\GenX_FX\credentials\api_keys.env"
echo GEMINI_API_KEY=your_gemini_api_key_here >> "D:\GenX_FX\credentials\api_keys.env"
echo EXNESS_LOGIN=your_exness_login >> "D:\GenX_FX\credentials\api_keys.env"
echo EXNESS_PASSWORD=your_exness_password >> "D:\GenX_FX\credentials\api_keys.env"
echo EXNESS_SERVER=Exness-MT5Trial8 >> "D:\GenX_FX\credentials\api_keys.env"
echo SECRET_KEY=your_secret_key_here >> "D:\GenX_FX\credentials\api_keys.env"

echo [4/4] Creating backup of credentials...
if exist "E:\" (
    copy "D:\GenX_FX\credentials\*" "E:\GenX_FX_Backup\credentials\" /Y
    echo Credentials backed up to USB drive E:
) else (
    echo WARNING: USB drive E: not found, credentials not backed up
)

echo.
echo ========================================
echo Credentials Setup Complete!
echo ========================================
echo.
echo Credential files created in:
echo   D:\GenX_FX\credentials\
echo.
echo Files created:
echo   - vps_credentials.env (Vultr VPS details)
echo   - mt4_credentials.env (MT4 account info)
echo   - api_keys.env (API keys and secrets)
echo.
echo IMPORTANT: Update the API keys in api_keys.env with your actual keys!
echo.
pause

