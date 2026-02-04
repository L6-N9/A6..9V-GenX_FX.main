@echo off
REM GenX FX AWS Free Tier Deployment Script for Windows
REM Run this script to deploy your trading system to AWS

echo.
echo ========================================
echo   GenX FX AWS Free Tier Deployment
echo ========================================
echo.

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS CLI is not installed or not in PATH
    echo Please install AWS CLI from: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

REM Check if AWS credentials are configured
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS credentials are not configured
    echo Please run: aws configure
    pause
    exit /b 1
)

echo ✅ AWS CLI is configured

REM Set variables
set AWS_REGION=us-east-1
set KEY_PAIR_NAME=genx-fx-key
set STACK_NAME=production-genx-fx-free-tier

echo.
echo Configuration:
echo - Region: %AWS_REGION%
echo - Key Pair: %KEY_PAIR_NAME%
echo - Stack Name: %STACK_NAME%
echo.

REM Create key pair if it doesn't exist
echo Creating EC2 key pair...
aws ec2 describe-key-pairs --key-names %KEY_PAIR_NAME% --region %AWS_REGION% >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating new key pair: %KEY_PAIR_NAME%
    aws ec2 create-key-pair --key-name %KEY_PAIR_NAME% --region %AWS_REGION% --query "KeyMaterial" --output text > %KEY_PAIR_NAME%.pem
    echo ✅ Key pair created and saved as %KEY_PAIR_NAME%.pem
) else (
    echo ⚠️  Key pair %KEY_PAIR_NAME% already exists
)

REM Deploy CloudFormation stack
echo.
echo Deploying CloudFormation stack...
aws cloudformation deploy ^
    --template-file deploy/aws-free-tier-deploy.yml ^
    --stack-name %STACK_NAME% ^
    --parameter-overrides Environment=production KeyPairName=%KEY_PAIR_NAME% ^
    --capabilities CAPABILITY_IAM ^
    --region %AWS_REGION%

if %errorlevel% neq 0 (
    echo ERROR: CloudFormation deployment failed
    pause
    exit /b 1
)

echo ✅ CloudFormation stack deployed successfully

REM Get deployment outputs
echo.
echo Getting deployment information...

for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %AWS_REGION% --query "Stacks[0].Outputs[?OutputKey==`InstancePublicIP`].OutputValue" --output text') do set INSTANCE_IP=%%i
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %AWS_REGION% --query "Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue" --output text') do set APP_URL=%%i

echo.
echo ========================================
echo   🎉 DEPLOYMENT SUCCESSFUL! 🎉
echo ========================================
echo.
echo Instance IP: %INSTANCE_IP%
echo Application URL: %APP_URL%
echo SSH Command: ssh -i %KEY_PAIR_NAME%.pem ec2-user@%INSTANCE_IP%
echo.
echo ========================================
echo   Next Steps:
echo ========================================
echo 1. Wait 5-10 minutes for the application to start
echo 2. Open your browser and go to: %APP_URL%
echo 3. Download trading signals: %APP_URL%/MT4_Signals.csv
echo 4. SSH into server: ssh -i %KEY_PAIR_NAME%.pem ec2-user@%INSTANCE_IP%
echo.
echo ========================================
echo   Free Tier Usage:
echo ========================================
echo ✅ EC2 t2.micro: 750 hours/month (FREE)
echo ✅ CloudWatch Logs: 5GB/month (FREE)
echo ✅ Data Transfer: 15GB/month (FREE)
echo 💰 Estimated cost after free tier: $5-15/month
echo.

REM Create monitoring script
echo Creating monitoring script...
echo @echo off > monitor-genx.bat
echo echo Checking GenX FX status... >> monitor-genx.bat
echo curl -s %APP_URL%/health >> monitor-genx.bat
echo echo. >> monitor-genx.bat
echo echo Application URL: %APP_URL% >> monitor-genx.bat
echo echo SSH Command: ssh -i %KEY_PAIR_NAME%.pem ec2-user@%INSTANCE_IP% >> monitor-genx.bat
echo pause >> monitor-genx.bat

echo ✅ Created monitor-genx.bat for easy monitoring

echo.
echo ========================================
echo   🚀 GenX FX is now live on AWS! 🚀
echo ========================================
echo.
pause