# 🚀 Quick AWS Free Tier Deployment

Deploy GenX FX to AWS in **5 minutes** using the free tier!

## ⚡ One-Click Deployment (Windows)

1. **Install AWS CLI** (if not installed):
   ```powershell
   # Download and install from: https://aws.amazon.com/cli/
   ```

2. **Configure AWS credentials**:
   ```bash
   aws configure
   # Enter your AWS Access Key ID and Secret Access Key
   ```

3. **Run deployment**:
   ```bash
   # Double-click this file:
   deploy-to-aws.bat
   ```

## 🐧 Linux/Mac Deployment

```bash
# 1. Configure AWS
aws configure

# 2. Run deployment
./deploy/free-tier-deploy.sh --key-pair genx-fx-key

# 3. Access your app
# URL will be shown after deployment
```

## 📊 What You Get

- ✅ **EC2 t2.micro** (FREE for 12 months)
- ✅ **Public IP** for web access
- ✅ **24/7 trading signals**
- ✅ **Web dashboard** at `http://YOUR_IP:8000`
- ✅ **CSV downloads** at `http://YOUR_IP:8000/MT4_Signals.csv`

## 💰 Cost Breakdown

**Free Tier (12 months):**
- EC2 t2.micro: 750 hours/month (FREE)
- Storage: 30GB (FREE)
- Data transfer: 15GB/month (FREE)

**After Free Tier:**
- ~$12-15/month total

## 🔧 Quick Commands

```bash
# Check status
curl http://YOUR_IP:8000/health

# Download signals
curl http://YOUR_IP:8000/MT4_Signals.csv

# SSH into server
ssh -i genx-fx-key.pem ec2-user@YOUR_IP

# View logs
docker logs genx-fx

# Restart app
docker restart genx-fx
```

## 🎯 Next Steps

1. Wait 5-10 minutes for deployment
2. Open `http://YOUR_IP:8000` in browser
3. Download signals for your EA
4. Start trading! 🚀