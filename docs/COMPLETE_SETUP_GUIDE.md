# 🚀 Complete GenX FX Setup Guide

## 🎯 Two-Account Strategy

### **Account 1: AWS (Signal Generation)**
- **Purpose**: Generate trading signals 24/7
- **Cost**: FREE (12 months), then ~$12/month
- **Setup**: 10 minutes

### **Account 2: VPS (MT4/5 Trading)**
- **Purpose**: Run MT4/5 + EA for actual trading
- **Cost**: $2.50-4/month
- **Setup**: 15 minutes

---

## 📋 **Step 1: AWS Account Setup**

### Create AWS Account
1. Go to: https://aws.amazon.com/free/
2. Click "Create a Free Account"
3. Enter email: `your-email@gmail.com`
4. Account name: `GenX-Trading`
5. Verify email and phone
6. Add credit card (won't be charged in free tier)

### Get AWS Keys
1. Login → Click your name → "Security credentials"
2. "Access keys" → "Create access key"
3. Choose "CLI" → Download CSV
4. **Save keys securely**

### Install & Configure AWS CLI
```bash
# Download: https://awscli.amazonaws.com/AWSCLIV2.msi
# After install:
aws configure
# Enter your keys from CSV
```

### Deploy GenX FX to AWS
```bash
# Double-click this file:
deploy-to-aws.bat

# Or command line:
./deploy/free-tier-deploy.sh --key-pair genx-fx-key
```

**Result**: Your signal generator at `http://YOUR_AWS_IP:8000`

---

## 🖥️ **Step 2: VPS Account Setup**

### Choose VPS Provider
**Recommended: Vultr**
- Cost: $2.50/month
- Sign up: https://www.vultr.com/
- Use promo code for free credit

### Create VPS
1. Choose "Windows Server 2019"
2. Plan: "Regular Performance" - $6/month (1GB RAM)
3. Location: Close to your broker
4. Deploy server

### Connect to VPS
1. Get IP and password from Vultr dashboard
2. Windows: Remote Desktop Connection
3. Connect to VPS IP with Administrator account

### Install MT4/5 on VPS
1. Download MT4 from your broker (Exness, FXCM, etc.)
2. Install on VPS
3. Login with your trading account
4. Copy `GenX_VPS_EA.mq4` to `MQL4/Experts/`

### Configure EA
1. Drag EA to chart
2. Set parameters:
   - `SignalURL`: `http://YOUR_AWS_IP:8000/MT4_Signals.csv`
   - `LotSize`: `0.01`
   - `MaxRisk`: `2.0`
3. Enable "Allow WebRequest" for your AWS URL
4. Click OK

---

## ⚡ **Quick Setup Commands**

### AWS Deployment
```bash
# 1. Configure AWS
aws configure

# 2. Deploy (Windows)
deploy-to-aws.bat

# 3. Get your signal URL
# Will be shown after deployment
```

### VPS Setup
```bash
# 1. Remote Desktop to VPS
mstsc /v:YOUR_VPS_IP

# 2. Download MT4 from broker
# 3. Install GenX_VPS_EA.mq4
# 4. Set SignalURL to your AWS IP
```

---

## 📊 **Testing Your Setup**

### Test AWS Signals
```bash
# Check if signals are generating
curl http://YOUR_AWS_IP:8000/MT4_Signals.csv

# Should return CSV with trading signals
```

### Test VPS EA
1. Check MT4 "Experts" tab for EA logs
2. Should see: "GenX VPS EA Started - Connecting to AWS Signals"
3. Every 5 minutes: "Signals updated from AWS"

---

## 💰 **Cost Breakdown**

### AWS (Signal Generation)
- **Free Tier**: 12 months FREE
- **After**: ~$12/month
- **Features**: 24/7 signal generation, web dashboard

### VPS (Trading)
- **Vultr**: $2.50-6/month
- **DigitalOcean**: $4/month
- **Features**: Windows, MT4/5, 24/7 trading

### **Total Cost**: $6.50-18/month for complete system

---

## 🔧 **Troubleshooting**

### AWS Issues
```bash
# Check deployment status
aws cloudformation describe-stacks --stack-name production-genx-fx-free-tier

# Check application logs
ssh -i genx-fx-key.pem ec2-user@YOUR_AWS_IP
docker logs genx-fx
```

### VPS Issues
1. **EA not connecting**: Check WebRequest permissions
2. **No trades**: Verify signal URL and confidence levels
3. **Connection lost**: Restart VPS or check internet

---

## 🎉 **Success Checklist**

- ✅ AWS account created and configured
- ✅ GenX FX deployed to AWS (signals generating)
- ✅ VPS created with Windows Server
- ✅ MT4/5 installed on VPS
- ✅ GenX_VPS_EA.mq4 running and connected
- ✅ EA receiving signals from AWS
- ✅ Test trades executed successfully

**🚀 Your complete GenX FX system is now live!**