# AWS Deployment Guide for GenX Trading Platform

This guide provides step-by-step instructions for deploying the GenX Trading Platform to AWS using ECS, RDS, ElastiCache, and other AWS services.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Infrastructure Overview](#aws-infrastructure-overview)
3. [Setup Instructions](#setup-instructions)
4. [Deployment Process](#deployment-process)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- AWS CLI v2.x
- Docker Desktop
- Git
- Python 3.9+
- jq (for JSON parsing)

### AWS Account Requirements
- Active AWS account with billing enabled
- IAM user with appropriate permissions
- Access to the following AWS services:
  - ECS (Elastic Container Service)
  - ECR (Elastic Container Registry)
  - RDS (Relational Database Service)
  - ElastiCache
  - CloudFormation
  - IAM
  - VPC
  - EC2
  - Application Load Balancer
  - CloudWatch
  - Systems Manager Parameter Store
  - Secrets Manager

### Required AWS Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:*",
                "ecr:*",
                "rds:*",
                "elasticache:*",
                "cloudformation:*",
                "iam:*",
                "ec2:*",
                "elasticloadbalancing:*",
                "logs:*",
                "ssm:*",
                "secretsmanager:*",
                "acm:*",
                "route53:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## AWS Infrastructure Overview

The deployment creates the following AWS resources:

### Networking
- **VPC**: Custom VPC with public subnets across 2 availability zones
- **Internet Gateway**: For internet connectivity
- **Route Tables**: For routing traffic
- **Security Groups**: For controlling access to resources

### Compute
- **ECS Cluster**: Fargate cluster for running containers
- **ECS Services**: For API, Discord bot, and Telegram bot
- **Application Load Balancer**: For distributing traffic

### Storage & Databases
- **RDS PostgreSQL**: Primary database
- **ElastiCache Redis**: Caching layer
- **ECR Repositories**: For Docker images

### Security & Management
- **IAM Roles**: For ECS task execution and permissions
- **Secrets Manager**: For storing sensitive data
- **Parameter Store**: For environment variables
- **CloudWatch Logs**: For application logging

## Setup Instructions

### 1. Install and Configure AWS CLI

```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

### 2. Clone and Prepare the Repository

```bash
# Clone the repository
git clone https://github.com/Mouy-leng/GenX_FX.git
cd GenX_FX

# Switch to the AWS deployment branch
git checkout aws-deployment-clean

# Make the deployment script executable
chmod +x deploy/aws-deploy.sh
```

### 3. Set Up GitHub Secrets

Add the following secrets to your GitHub repository:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `SLACK_WEBHOOK_URL`: (Optional) Slack webhook for notifications

### 4. Configure Environment Variables

Create a `.env` file for local development:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the environment variables
nano .env
```

Required environment variables:
For a complete list of environment variables, refer to the `API_KEY_SETUP.md` file in the root of the repository.

## Deployment Process

### Option 1: Automated Deployment via GitHub Actions

1. **Push to the deployment branch**:
   ```bash
   git push origin aws-deployment-clean
   ```

2. **Monitor the deployment**:
   - Go to GitHub Actions tab
   - Watch the "Deploy to AWS" workflow
   - Check for any errors or issues

3. **Get deployment outputs**:
   - The workflow will output the application URL
   - Check the deployment logs for database and Redis endpoints

### Option 2: Manual Deployment

1. **Run the deployment script**:
   ```bash
   ./deploy/aws-deploy.sh --environment production --region us-east-1
   ```

2. **Monitor the deployment**:
   ```bash
   # Check CloudFormation stack status
   aws cloudformation describe-stacks \
     --stack-name production-genx-trading-platform \
     --region us-east-1

   # Check ECS service status
   aws ecs describe-services \
     --cluster production-genx-cluster \
     --services production-genx-service \
     --region us-east-1
   ```

### Option 3: Step-by-Step Manual Deployment

1. **Create ECR repositories**:
   ```bash
   aws ecr create-repository --repository-name genx-api --region us-east-1
   aws ecr create-repository --repository-name genx-discord-bot --region us-east-1
   aws ecr create-repository --repository-name genx-telegram-bot --region us-east-1
   ```

2. **Build and push Docker images**:
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

   # Build and push images
   docker build -f Dockerfile.production -t genx-api .
   docker tag genx-api:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/genx-api:latest
   docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/genx-api:latest
   ```

3. **Deploy CloudFormation stack**:
   ```bash
   aws cloudformation deploy \
     --template-file deploy/aws-deployment.yml \
     --stack-name production-genx-trading-platform \
     --parameter-overrides Environment=production \
     --capabilities CAPABILITY_IAM \
     --region us-east-1
   ```

## Monitoring and Maintenance

### CloudWatch Monitoring

Set up CloudWatch alarms for:
- CPU utilization > 80%
- Memory utilization > 80%
- Application errors
- Database connections
- Load balancer health

### Logging

Application logs are automatically sent to CloudWatch Logs:
- Log group: `/ecs/production-genx`
- Retention: 30 days
- Log level: INFO

### Database Maintenance

- **Backups**: RDS automatically creates daily backups
- **Monitoring**: Use RDS Performance Insights
- **Scaling**: Monitor and adjust instance size as needed

### Container Updates

To update the application:
```bash
# Build new image
docker build -f Dockerfile.production -t genx-api .

# Push to ECR
docker tag genx-api:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/genx-api:latest
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/genx-api:latest

# Force new deployment
aws ecs update-service \
  --cluster production-genx-cluster \
  --service production-genx-service \
  --force-new-deployment \
  --region us-east-1
```

## Troubleshooting

### Common Issues

1. **ECS Service not starting**:
   ```bash
   # Check service events
   aws ecs describe-services \
     --cluster production-genx-cluster \
     --services production-genx-service \
     --region us-east-1

   # Check task logs
   aws logs describe-log-groups --log-group-name-prefix /ecs/production-genx --region us-east-1
   ```

2. **Database connection issues**:
   ```bash
   # Check RDS status
   aws rds describe-db-instances --db-instance-identifier production-genx-db --region us-east-1

   # Check security groups
   aws ec2 describe-security-groups --group-names production-genx-db-sg --region us-east-1
   ```

3. **Load balancer health check failures**:
   ```bash
   # Check target group health
   aws elbv2 describe-target-health \
     --target-group-arn $(aws elbv2 describe-target-groups --names production-genx-tg --region us-east-1 --query 'TargetGroups[0].TargetGroupArn' --output text) \
     --region us-east-1
   ```

### Cost Optimization

1. **Use Spot instances** for non-critical workloads
2. **Enable auto-scaling** based on CPU/memory usage
3. **Use reserved instances** for predictable workloads
4. **Monitor and optimize** database instance size

### Security Best Practices

1. **Use IAM roles** instead of access keys
2. **Enable VPC Flow Logs** for network monitoring
3. **Use AWS Config** for compliance monitoring
4. **Regular security updates** for base images
5. **Enable CloudTrail** for API logging

## Support

For issues and questions:
1. Check the [GitHub Issues](https://github.com/Mouy-leng/GenX_FX/issues)
2. Review AWS CloudWatch logs
3. Check ECS service events
4. Contact the development team

## Cost Estimation

Estimated monthly costs for production deployment:
- ECS Fargate: $50-100/month
- RDS PostgreSQL: $30-60/month
- ElastiCache Redis: $20-40/month
- Application Load Balancer: $20-30/month
- CloudWatch Logs: $10-20/month
- **Total**: $130-250/month

*Costs may vary based on usage and region* 