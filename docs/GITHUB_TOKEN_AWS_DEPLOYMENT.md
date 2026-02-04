# GitHub Token AWS Deployment Guide

This guide provides multiple solutions for deploying your application to AWS using a GitHub token for authentication and deployment management.

## 🚀 Quick Start

### Option 1: One-Click Setup and Deploy
```bash
# Run the complete setup
./setup_github_token_aws.sh

# Deploy to AWS
./deploy-with-github-token.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
./setup_github_token_aws.sh github
./setup_github_token_aws.sh aws
./setup_github_token_aws.sh docker
./setup_github_token_aws.sh python

# Deploy using Python script
python3 deploy/github_aws_deploy.py --environment production --region us-east-1
```

## 📋 Prerequisites

- GitHub Personal Access Token (already provided)
- AWS Account with appropriate permissions
- Linux/macOS system (scripts are designed for Unix-like systems)

## 🔧 Solutions Overview

### 1. GitHub Actions Workflow
**File**: `.github/workflows/github-token-aws-deploy.yml`

**Features**:
- Automated deployment on push to main branch
- Security scanning with CodeQL and Bandit
- Docker image building and pushing to ECR
- CloudFormation deployment
- Health checks and monitoring
- Slack notifications
- Deployment status tracking

**Usage**:
```bash
# Push to main branch to trigger deployment
git push origin main

# Or manually trigger from GitHub Actions tab
```

### 2. GitHub CLI Bash Script
**File**: `deploy/github-token-aws-deploy.sh`

**Features**:
- GitHub CLI integration
- Docker image building and ECR pushing
- AWS CloudFormation deployment
- Health checks
- Deployment status updates
- Comprehensive error handling

**Usage**:
```bash
# Deploy to production
./deploy/github-token-aws-deploy.sh --environment production --region us-east-1

# Deploy to staging
./deploy/github-token-aws-deploy.sh -e staging -r us-west-2
```

### 3. Python Deployment Script
**File**: `deploy/github_aws_deploy.py`

**Features**:
- GitHub API integration
- AWS SDK (boto3) integration
- Docker SDK integration
- Comprehensive error handling
- Health checks
- Deployment status tracking

**Usage**:
```bash
# Deploy to production
python3 deploy/github_aws_deploy.py --environment production --region us-east-1

# Deploy with custom token
python3 deploy/github_aws_deploy.py -e staging -r us-west-2 -t your_token_here
```

### 4. Setup Script
**File**: `setup_github_token_aws.sh`

**Features**:
- Automatic installation of required tools
- GitHub CLI setup and authentication
- AWS CLI setup and configuration
- Docker installation
- Python dependencies installation
- Environment testing

**Usage**:
```bash
# Complete setup
./setup_github_token_aws.sh

# Install specific components
./setup_github_token_aws.sh github    # GitHub CLI only
./setup_github_token_aws.sh aws       # AWS CLI only
./setup_github_token_aws.sh docker    # Docker only
./setup_github_token_aws.sh python    # Python deps only
./setup_github_token_aws.sh test      # Test current setup
```

## 🔑 Authentication Setup

### GitHub Token Configuration
The GitHub token is already configured in all scripts:
```bash
GITHUB_TOKEN="YOUR_GITHUB_TOKEN_HERE"
```

### AWS Credentials Setup
You have several options for AWS credentials:

#### Option 1: AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your region (us-east-1)
# Enter your output format (json)
```

#### Option 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option 3: GitHub Secrets (for GitHub Actions)
Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ROLE_ARN` (if using IAM roles)
- `SLACK_WEBHOOK_URL` (optional)

## 🚀 Deployment Process

### Step-by-Step Deployment Flow

1. **Authentication Check**
   - Verify GitHub token
   - Verify AWS credentials
   - Test Docker installation

2. **GitHub Deployment Creation**
   - Create deployment record in GitHub
   - Set initial status to "in_progress"

3. **Docker Image Building**
   - Build application Docker images
   - Push to Amazon ECR
   - Tag with commit SHA and latest

4. **AWS Infrastructure Deployment**
   - Deploy CloudFormation stack
   - Create/update EC2 instances
   - Configure load balancers
   - Set up security groups

5. **Health Check**
   - Verify application is running
   - Test health endpoint
   - Update deployment status

6. **Monitoring Setup**
   - Configure CloudWatch logs
   - Set up alarms
   - Enable monitoring

## 📊 Monitoring and Management

### GitHub Deployment Status
- View deployment status in GitHub repository
- Check deployment logs and history
- Monitor deployment environments

### AWS Console Monitoring
- CloudFormation stacks
- EC2 instances
- Load balancers
- CloudWatch metrics

### Application Health Checks
```bash
# Check application health
curl http://your-load-balancer-url/health

# Check deployment status
aws cloudformation describe-stacks --stack-name production-genx-trading-platform
```

## 🔧 Configuration Options

### Environment Variables
```bash
# GitHub
GITHUB_TOKEN=your_github_token

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Deployment
ENVIRONMENT=production
AWS_REGION=us-east-1
BRANCH=main
```

### Command Line Options
```bash
# Environment selection
--environment production|staging|development

# AWS region
--region us-east-1|us-west-2|eu-west-1

# Git branch
--branch main|develop|feature-branch

# GitHub token
--token your_github_token
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. GitHub Authentication Failed
```bash
# Check GitHub CLI status
gh auth status

# Re-authenticate
echo "your_token" | gh auth login --with-token
```

#### 2. AWS Credentials Not Found
```bash
# Check AWS credentials
aws sts get-caller-identity

# Configure AWS credentials
aws configure
```

#### 3. Docker Not Running
```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 4. Python Dependencies Missing
```bash
# Install required packages
pip3 install boto3 docker requests

# Or use the setup script
./setup_github_token_aws.sh python
```

### Debug Mode
```bash
# Enable debug output
export DEBUG=1
./deploy/github-token-aws-deploy.sh

# Or for Python script
python3 -u deploy/github_aws_deploy.py --environment production
```

## 📈 Advanced Features

### Multi-Environment Deployment
```bash
# Deploy to staging
./deploy/github-token-aws-deploy.sh --environment staging

# Deploy to production
./deploy/github-token-aws-deploy.sh --environment production
```

### Custom Docker Images
```bash
# Build custom images
docker build -f Dockerfile.production -t your-app:latest .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag your-app:latest your-account.dkr.ecr.us-east-1.amazonaws.com/your-app:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/your-app:latest
```

### Rollback Deployment
```bash
# Rollback to previous version
aws cloudformation rollback-stack --stack-name production-genx-trading-platform

# Or use GitHub deployment rollback
gh api repos/:owner/:repo/deployments --method POST \
  --field environment=production \
  --field ref=previous-commit-sha
```

## 🔒 Security Best Practices

### Token Security
- Store tokens in environment variables
- Use GitHub secrets for sensitive data
- Rotate tokens regularly
- Use least privilege principle

### AWS Security
- Use IAM roles instead of access keys when possible
- Enable CloudTrail logging
- Use VPC and security groups
- Enable encryption at rest and in transit

### Network Security
- Use HTTPS for all communications
- Implement proper firewall rules
- Use private subnets for databases
- Enable WAF for web applications

## 📚 Additional Resources

### Documentation
- [GitHub CLI Documentation](https://cli.github.com/)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Useful Commands
```bash
# Check all tools
./setup_github_token_aws.sh test

# View deployment logs
gh api repos/:owner/:repo/deployments

# Check AWS resources
aws cloudformation list-stacks

# Monitor application
docker logs your-container-name
```

### Support
If you encounter issues:
1. Check the troubleshooting section
2. Review logs and error messages
3. Verify all prerequisites are met
4. Test individual components
5. Check GitHub and AWS documentation

## 🎯 Next Steps

After successful deployment:
1. Set up monitoring and alerting
2. Configure backup strategies
3. Implement CI/CD pipelines
4. Set up staging environments
5. Plan for scaling and optimization

---

**Note**: This guide assumes you have the necessary permissions and access to both GitHub and AWS. Make sure to follow security best practices and comply with your organization's policies.