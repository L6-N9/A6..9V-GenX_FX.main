# 🔐 Complete GitHub Secrets & Variables Setup Guide

## 🎯 **Repository: Mouy-leng/GenX_FX**

Your GitHub token doesn't have admin permissions for repository secrets, so you'll need to set them up manually through the GitHub web interface.

## 📋 **Complete List of Required Secrets & Variables**

### 🔐 **Repository Secrets** (Settings → Secrets and variables → Actions → Secrets)

#### **✅ Already Available**
```
AMP_TOKEN = [your AMP session token]
```

#### **🔑 Critical Secrets (Must Configure)**

**Docker Hub Secrets:**
```
DOCKER_USERNAME = keamouyleng
DOCKER_PASSWORD = [Get from https://hub.docker.com/settings/security]
```

**AWS Secrets:**
```
AWS_ACCESS_KEY_ID = [Get from AWS Console]
AWS_SECRET_ACCESS_KEY = [Get from AWS Console]
```

**Database Secrets (Auto-generated):**
```
POSTGRES_PASSWORD = [Use: openssl rand -base64 32]
REDIS_PASSWORD = [Use: openssl rand -base64 32]
```

**GenX (GitHub Packages / GHCR) Container Digests:**
```
GENX_GHCR_IMAGE = ghcr.io/mouy-leng/genx
GENX_CONTAINER_DIGEST_MAIN = sha256:cbdd7132acf1cc3000d1965ac9ac0f7c8e425f0f2ac5e0080764e87279233f21
GENX_CONTAINER_DIGEST_2 = sha256:3d8a19989bb281c070cc8b478317f904741a52e9ac18a4c3e9d15965715c9372
GENX_CONTAINER_DIGEST_3 = sha256:c253aa7ab5d40949ff74f6aa00925087b212168efe8b7c4b60976c599ed11a76
```

#### **⚠️ Optional Secrets**

**Trading Platform (FXCM):**
```
FXCM_API_KEY = [Get from FXCM demo account]
FXCM_SECRET_KEY = [Get from FXCM demo account]
```

**AI/ML APIs:**
```
GEMINI_API_KEY = [Get from Google AI Studio]
OPENAI_API_KEY = [Get from OpenAI platform]
```

### 📊 **Repository Variables** (Settings → Secrets and variables → Actions → Variables)

```
AMP_ENV = production
DOCKER_IMAGE = keamouyleng/genx-fx
AWS_REGION = us-east-1
EC2_INSTANCE_TYPE = t2.micro
```

## 🚀 **Step-by-Step Manual Setup**

### **Step 1: Access GitHub Repository Settings**

1. Go to: **https://github.com/Mouy-leng/GenX_FX**
2. Click **"Settings"** tab
3. Click **"Secrets and variables"** → **"Actions"**

### **Step 2: Add Repository Secrets**

Click **"New repository secret"** for each secret:

#### **Docker Hub Secrets**
```
Name: DOCKER_USERNAME
Value: keamouyleng
```

```
Name: DOCKER_PASSWORD
Value: [Your Docker Hub Access Token]
```
**Get token from**: https://hub.docker.com/settings/security

#### **AWS Secrets**
```
Name: AWS_ACCESS_KEY_ID
Value: [Your AWS Access Key ID]
```

```
Name: AWS_SECRET_ACCESS_KEY
Value: [Your AWS Secret Access Key]
```
**Get from**: https://console.aws.amazon.com → IAM → Security credentials → Create access key

#### **AMP Token (Already Provided)**
```
Name: AMP_TOKEN
Value: [your AMP session token]
```

#### **Database Secrets (Generate Secure Passwords)**
```
Name: POSTGRES_PASSWORD
Value: [Generate with: openssl rand -base64 32]
```

```
Name: REDIS_PASSWORD
Value: [Generate with: openssl rand -base64 32]
```

#### **Optional: Trading Platform**
```
Name: FXCM_API_KEY
Value: [Your FXCM API Key]
```

```
Name: FXCM_SECRET_KEY
Value: [Your FXCM Secret Key]
```

#### **Optional: AI APIs**
```
Name: GEMINI_API_KEY
Value: [Your Google Gemini API Key]
```

```
Name: OPENAI_API_KEY
Value: [Your OpenAI API Key]
```

### **Step 3: Add Repository Variables**

Click **"Variables"** tab, then **"New repository variable"** for each:

```
Name: AMP_ENV
Value: production
```

```
Name: DOCKER_IMAGE
Value: keamouyleng/genx-fx
```

```
Name: AWS_REGION
Value: us-east-1
```

```
Name: EC2_INSTANCE_TYPE
Value: t2.micro
```

## 🔑 **How to Get Required Credentials**

### **1. Docker Hub Access Token**
1. Go to: https://hub.docker.com/settings/security
2. Click **"New Access Token"**
3. Name: `amp-trading-system`
4. Copy the generated token

### **2. AWS Credentials**
1. Go to: https://console.aws.amazon.com
2. In IAM, create an access key for your deployment user
3. Copy both keys into GitHub Secrets

### **3. Generate Database Passwords**
Run these commands to generate secure passwords:
```bash
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -base64 32  # For REDIS_PASSWORD
```

### **4. Optional: FXCM API Credentials**
1. Go to: https://www.fxcm.com/markets/forex-trading-demo/
2. Create a demo account
3. Get API credentials from dashboard

### **5. Optional: AI API Keys**
- **Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/api-keys

## ✅ **Verification Commands**

After setting up all secrets, verify with:

```bash
# Check GitHub Actions workflows
gh workflow list

# Trigger a test build
gh workflow run docker-image.yml

# Check deployment status
python3 aws_deploy_status.py
```

## 🎯 **Priority Order**

### **Critical (Must Have)**
1. ✅ `AMP_TOKEN`
2. 🔑 `DOCKER_USERNAME` + `DOCKER_PASSWORD`
3. 🔑 `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
4. 🔑 `POSTGRES_PASSWORD` + `REDIS_PASSWORD`

### **Important (Should Have)**
5. 📊 All Variables (AMP_ENV, DOCKER_IMAGE, AWS_REGION, EC2_INSTANCE_TYPE)

### **Optional (Nice to Have)**
6. ⚠️ `FXCM_API_KEY` + `FXCM_SECRET_KEY`
7. ⚠️ `GEMINI_API_KEY` + `OPENAI_API_KEY`

## 🚨 **Quick Setup Checklist**

- [ ] **Docker Hub**: Get access token from https://hub.docker.com/settings/security
- [ ] **AWS**: Get credentials from https://console.aws.amazon.com
- [ ] **Database**: Generate passwords with `openssl rand -base64 32`
- [ ] **GitHub**: Add all secrets and variables through web interface
- [ ] **Test**: Run `gh workflow run docker-image.yml`
- [ ] **Deploy**: Run `./aws/amp-deploy.sh`

## 🔗 **Useful Links**

- **Repository**: https://github.com/Mouy-leng/GenX_FX
- **Settings**: https://github.com/Mouy-leng/GenX_FX/settings/secrets/actions
- **Docker Hub**: https://hub.docker.com/settings/security
- **AWS Console**: https://console.aws.amazon.com
- **FXCM Demo**: https://www.fxcm.com/markets/forex-trading-demo/
- **Gemini API**: https://makersuite.google.com/app/apikey
- **OpenAI API**: https://platform.openai.com/api-keys

## 🎉 **Success Indicators**

- ✅ GitHub Actions workflows run successfully
- ✅ Docker images build and push to Docker Hub
- ✅ AWS deployment completes without errors
- ✅ AMP system responds on deployed URL

## 📞 **Need Help?**

If you encounter any issues:
1. Check the GitHub Actions logs for error details
2. Verify all secrets are correctly named and have valid values
3. Ensure your AWS credentials have the necessary permissions
4. Test Docker Hub login with your credentials

**Your AMP token is already configured and ready to use!** 🚀