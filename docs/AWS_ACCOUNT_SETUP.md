# 🚀 AWS Account Setup Guide

## Step 1: Create AWS Account
1. Go to: https://aws.amazon.com/free/
2. Click "Create a Free Account"
3. Enter email and account name
4. Verify email
5. Add payment method (required but won't be charged in free tier)
6. Verify phone number
7. Choose "Basic Support - Free"

## Step 2: Get Access Keys
1. Login to AWS Console
2. Click your name (top right) → "Security credentials"
3. Scroll to "Access keys" → "Create access key"
4. Choose "Command Line Interface (CLI)"
5. Download CSV file with keys
6. **SAVE THESE KEYS SECURELY**

## Step 3: Install AWS CLI
```bash
# Windows
https://awscli.amazonaws.com/AWSCLIV2.msi

# After install, configure:
aws configure
# Enter:
# AWS Access Key ID: [from CSV]
# AWS Secret Access Key: [from CSV]  
# Default region: us-east-1
# Default output format: json
```

## Step 4: Test Setup
```bash
aws sts get-caller-identity
# Should show your account info
```