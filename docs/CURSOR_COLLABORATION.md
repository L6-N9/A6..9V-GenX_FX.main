# 🤖 Cursor Agent Collaboration Guide

## 🎯 Current Status
✅ **Git Commit Complete**: All AWS deployment files committed  
🔄 **Next Task**: Deploy GenX FX to AWS free tier

## 📋 For Cursor Agent

### Files Ready for Deployment:
- `deploy/aws-free-tier-deploy.yml` - CloudFormation template
- `deploy/free-tier-deploy.sh` - Deployment script  
- `cursor-agent-instructions.md` - Step-by-step guide
- `aws-deploy-commands.txt` - Exact commands

### Required from User:
```bash
# User needs to provide:
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
```

### Deployment Commands:
```bash
# 1. Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 2. Configure AWS (needs user input)
aws configure

# 3. Deploy
aws cloudformation deploy \
  --template-file deploy/aws-free-tier-deploy.yml \
  --stack-name production-genx-fx-free-tier \
  --parameter-overrides Environment=production KeyPairName=genx-fx-key \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# 4. Get result
aws cloudformation describe-stacks \
  --stack-name production-genx-fx-free-tier \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

## 🔄 Collaboration Workflow

### My Role (Amazon Q):
- ✅ Created deployment infrastructure
- ✅ Optimized for AWS free tier
- ✅ Created VPS integration guides
- ✅ Git commit completed

### Cursor Agent Role:
- 🔄 Execute AWS CLI installation
- 🔄 Run deployment commands
- 🔄 Monitor deployment status
- 🔄 Report deployment results

### User Role:
- 🔄 Provide AWS credentials
- 🔄 Approve deployment steps
- 🔄 Test final system

## 📊 Expected Results
After successful deployment:
- **Instance IP**: `54.xxx.xxx.xxx`
- **App URL**: `http://54.xxx.xxx.xxx:8000`
- **Signals**: `http://54.xxx.xxx.xxx:8000/MT4_Signals.csv`
- **SSH**: `ssh -i genx-fx-key.pem ec2-user@54.xxx.xxx.xxx`

## 🚨 Next Steps for Cursor
1. Wait for user's AWS credentials
2. Execute `aws-cli-setup.sh`
3. Run deployment commands from `aws-deploy-commands.txt`
4. Report success/failure with instance details