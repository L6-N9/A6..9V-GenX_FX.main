# Instructions for Cursor Agent

## AWS CLI Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure (need user's AWS keys)
aws configure
```

## Deployment Steps
```bash
# 1. Test connection
aws sts get-caller-identity

# 2. Create key pair
aws ec2 create-key-pair --key-name genx-fx-key --region us-east-1 --query 'KeyMaterial' --output text > genx-fx-key.pem

# 3. Deploy CloudFormation
aws cloudformation deploy \
  --template-file deploy/aws-free-tier-deploy.yml \
  --stack-name production-genx-fx-free-tier \
  --parameter-overrides Environment=production KeyPairName=genx-fx-key \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# 4. Get instance IP
aws cloudformation describe-stacks \
  --stack-name production-genx-fx-free-tier \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`InstancePublicIP`].OutputValue' \
  --output text
```

## Files Needed
- `deploy/aws-free-tier-deploy.yml` ✅ Created
- AWS credentials from user
- Region: us-east-1