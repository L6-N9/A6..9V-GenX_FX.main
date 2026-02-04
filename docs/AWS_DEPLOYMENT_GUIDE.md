# 🚀 AMP System AWS Deployment Guide

## ✅ **AWS Free Tier Optimized Deployment**

This guide will help you deploy your AMP CLI system to AWS using the free tier, minimizing costs while providing a production-ready infrastructure.

---

## 📋 **Prerequisites**

### **Required Tools**
- [x] **AWS Account**: Free tier eligible
- [x] **AWS CLI**: Installed and configured
- [x] **Terraform** (Optional): For infrastructure as code
- [x] **SSH Key Pair**: For EC2 access

### **AWS Free Tier Limits**
- **EC2**: 750 hours/month of t2.micro
- **S3**: 5GB storage
- **DynamoDB**: 25GB storage, 25 WCU/RCU
- **CloudWatch**: 5GB data ingestion
- **Data Transfer**: 15GB outbound

---

## 🚀 **Deployment Options**

### **Option 1: Automated Script Deployment**
```bash
# Run the automated deployment script
cd aws/
chmod +x amp-deploy.sh
./amp-deploy.sh
```

### **Option 2: Terraform Infrastructure as Code**
```bash
# Deploy using Terraform
cd aws/terraform/
terraform init
terraform plan
terraform apply
```

### **Option 3: Manual AWS Console Deployment**
Follow the step-by-step manual deployment process.

---

## 🔧 **Option 1: Automated Script Deployment**

### **Step 1: Prepare AWS Credentials**
```bash
# Install AWS CLI if not installed
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (us-east-1 for free tier)
```

### **Step 2: Run Deployment Script**
```bash
# Navigate to AWS directory
cd aws/

# Make script executable
chmod +x amp-deploy.sh

# Run deployment
./amp-deploy.sh
```

### **Step 3: Choose Deployment Method**
The script will prompt you to choose:
1. **EC2 Instance** (t2.micro - free tier eligible)
2. **ECS Fargate** (free tier eligible)

**Recommendation**: Choose **EC2 Instance** for simplicity and full control.

---

## 🏗️ **Option 2: Terraform Deployment**

### **Step 1: Install Terraform**
```bash
# Download Terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs)"
sudo apt-get update && sudo apt-get install terraform
```

### **Step 2: Generate SSH Key Pair**
```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f amp-trading-key -N ""
# This creates amp-trading-key (private) and amp-trading-key.pub (public)
```

### **Step 3: Deploy Infrastructure**
```bash
# Navigate to Terraform directory
cd aws/terraform/

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

### **Step 4: Access Your System**
After successful deployment, Terraform will output:
- **Public IP**: Your EC2 instance IP
- **Access URLs**: AMP API and Grafana dashboard
- **SSH Command**: To connect to your instance

---

## 📊 **What Gets Deployed**

### **AWS Resources Created**
- ✅ **EC2 Instance**: t2.micro (free tier eligible)
- ✅ **VPC & Networking**: Custom VPC with public subnet
- ✅ **Security Group**: Firewall rules for AMP system
- ✅ **S3 Bucket**: Data storage (free tier: 5GB)
- ✅ **DynamoDB Table**: NoSQL database (free tier: 25GB)
- ✅ **CloudWatch Logs**: Centralized logging
- ✅ **Key Pair**: SSH access to EC2

### **AMP System Components**
- ✅ **AMP CLI**: Complete trading system
- ✅ **Redis**: Caching and job queue
- ✅ **PostgreSQL**: Relational database
- ✅ **Grafana**: Monitoring dashboard
- ✅ **Docker Compose**: Container orchestration

---

## 🔗 **Access Your Deployed System**

### **Access URLs**
- **AMP API Health**: `http://<PUBLIC_IP>:8000/health`
- **Grafana Dashboard**: `http://<PUBLIC_IP>:3000`
- **Grafana Credentials**: `admin` / `amp_admin`

### **SSH Access**
```bash
# Connect to your EC2 instance
ssh -i amp-trading-key.pem ec2-user@<PUBLIC_IP>
```

### **AMP CLI Commands**
```bash
# Check system status
docker exec -it amp-trading-system amp status

# View authentication status
docker exec -it amp-trading-system amp auth --status

# Start scheduler
docker exec -it amp-trading-system amp schedule --start

# Monitor dashboard
docker exec -it amp-trading-system amp monitor --dashboard

# View logs
docker logs amp-trading-system
```

---

## 🔐 **Security Configuration**

### **Security Group Rules**
- **SSH (Port 22)**: Secure shell access
- **AMP API (Port 8000)**: Trading system API
- **Grafana (Port 3000)**: Monitoring dashboard
- **All Outbound**: Internet access for updates

### **Best Practices**
- ✅ **Non-root User**: Docker containers run as non-root
- ✅ **Health Checks**: Automatic health monitoring
- ✅ **Logging**: Centralized CloudWatch logs
- ✅ **Backup**: S3 bucket for data storage
- ✅ **Monitoring**: Automated system monitoring

---

## 💰 **Cost Optimization**

### **Free Tier Usage**
- **EC2 t2.micro**: 750 hours/month (31 days)
- **S3 Storage**: 5GB free storage
- **DynamoDB**: 25GB storage, 25 WCU/RCU
- **CloudWatch**: 5GB data ingestion
- **Data Transfer**: 15GB outbound

### **Cost Monitoring**
```bash
# Check AWS billing
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost
```

### **Cost Optimization Tips**
1. **Stop Instance**: When not in use
2. **Monitor Usage**: Check AWS Cost Explorer
3. **Set Alerts**: CloudWatch billing alarms
4. **Use Spot Instances**: For non-critical workloads

---

## 🔧 **Management Commands**

### **Instance Management**
```bash
# Stop instance (save costs)
aws ec2 stop-instances --instance-ids <INSTANCE_ID>

# Start instance
aws ec2 start-instances --instance-ids <INSTANCE_ID>

# Terminate instance (permanent)
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>
```

### **System Management**
```bash
# SSH into instance
ssh -i amp-trading-key.pem ec2-user@<PUBLIC_IP>

# Check system status
/opt/amp-system/monitor.sh

# View health check
/opt/amp-system/health_check.sh

# Restart AMP system
sudo systemctl restart amp-system.service
```

### **Docker Management**
```bash
# View running containers
docker ps

# View logs
docker logs amp-trading-system

# Restart containers
docker-compose restart

# Update system
docker-compose pull
docker-compose up -d
```

---

## 📈 **Monitoring & Alerts**

### **CloudWatch Monitoring**
- **CPU Utilization**: Monitor EC2 performance
- **Memory Usage**: Track system resources
- **Disk Usage**: Monitor storage
- **Network**: Track data transfer

### **AMP System Monitoring**
- **Health Checks**: Every 5 minutes
- **Daily Reports**: System status reports
- **Log Monitoring**: Centralized logging
- **Performance Metrics**: Real-time dashboards

### **Set Up Alerts**
```bash
# Create CloudWatch alarm for high CPU
aws cloudwatch put-metric-alarm \
    --alarm-name "AMP-HighCPU" \
    --alarm-description "High CPU usage on AMP system" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Instance Won't Start**:
   ```bash
   # Check instance status
   aws ec2 describe-instances --instance-ids <INSTANCE_ID>
   
   # Check system logs
   ssh -i amp-trading-key.pem ec2-user@<PUBLIC_IP> 'sudo journalctl -u amp-system.service'
   ```

2. **Docker Issues**:
   ```bash
   # Check Docker status
   sudo systemctl status docker
   
   # Restart Docker
   sudo systemctl restart docker
   ```

3. **AMP System Issues**:
   ```bash
   # Check container status
   docker ps -a
   
   # View container logs
   docker logs amp-trading-system
   
   # Restart AMP system
   docker-compose restart amp-system
   ```

4. **Network Issues**:
   ```bash
   # Check security group
   aws ec2 describe-security-groups --group-ids <SG_ID>
   
   # Test connectivity
   curl -f http://localhost:8000/health
   ```

### **Support Commands**
```bash
# Full system status
/opt/amp-system/monitor.sh

# Health check
/opt/amp-system/health_check.sh

# View all logs
sudo journalctl -u amp-system.service -f

# Check disk space
df -h

# Check memory usage
free -h
```

---

## 🎯 **Next Steps After Deployment**

1. **Configure API Keys**: Update environment variables
2. **Test Trading**: Run test trades
3. **Set Up Monitoring**: Configure alerts
4. **Backup Strategy**: Implement data backup
5. **Scale Up**: Add more instances as needed

---

## 📞 **Support & Resources**

### **AWS Resources**
- **AWS Console**: https://console.aws.amazon.com
- **AWS CLI Documentation**: https://docs.aws.amazon.com/cli
- **Terraform Documentation**: https://www.terraform.io/docs

### **AMP System Resources**
- **GitHub Repository**: https://github.com/Mouy-leng/GenX_FX
- **Docker Hub**: https://hub.docker.com/r/keamouyleng/genx-fx
- **Documentation**: See project README

---

**🎉 Your AMP system is now deployed to AWS and ready for production trading!**

**Next Action**: Configure your API keys and start trading.