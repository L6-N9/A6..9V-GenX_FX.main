#!/bin/bash

# AMP System AWS Deployment Script
# Optimized for AWS Free Tier
# Deploys AMP CLI system to AWS with minimal cost

set -e

echo "🚀 Deploying AMP System to AWS (Free Tier Optimized)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check AWS CLI installation
check_aws_cli() {
    print_status "Checking AWS CLI installation..."
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        print_status "Installation guide: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    print_success "AWS CLI is installed"
}

# Configure AWS credentials
configure_aws() {
    print_status "Configuring AWS credentials..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_warning "AWS credentials not configured. Please configure them:"
        aws configure
    else
        print_success "AWS credentials are configured"
        aws sts get-caller-identity
    fi
}

# Create AWS resources for AMP system
create_aws_resources() {
    print_status "Creating AWS resources for AMP system..."
    
    # Set variables
    PROJECT_NAME="amp-trading-system"
    REGION="us-east-1"  # Free tier region
    S3_BUCKET="${PROJECT_NAME}-$(date +%s)"
    DYNAMODB_TABLE="${PROJECT_NAME}-data"
    CLOUDWATCH_LOG_GROUP="/aws/amp-system"
    
    # Create S3 bucket
    print_status "Creating S3 bucket: $S3_BUCKET"
    aws s3 mb s3://$S3_BUCKET --region $REGION
    
    # Create DynamoDB table (free tier: 25GB storage, 25 WCU/RCU)
    print_status "Creating DynamoDB table: $DYNAMODB_TABLE"
    aws dynamodb create-table \
        --table-name $DYNAMODB_TABLE \
        --attribute-definitions AttributeName=id,AttributeType=S \
        --key-schema AttributeName=id,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region $REGION
    
    # Create CloudWatch log group
    print_status "Creating CloudWatch log group: $CLOUDWATCH_LOG_GROUP"
    aws logs create-log-group --log-group-name $CLOUDWATCH_LOG_GROUP --region $REGION
    
    # Save configuration
    cat > aws_config.json << EOF
{
    "project_name": "$PROJECT_NAME",
    "region": "$REGION",
    "s3_bucket": "$S3_BUCKET",
    "dynamodb_table": "$DYNAMODB_TABLE",
    "cloudwatch_log_group": "$CLOUDWATCH_LOG_GROUP"
}
EOF
    
    print_success "AWS resources created successfully"
}

# Create EC2 instance (t2.micro - free tier eligible)
create_ec2_instance() {
    print_status "Creating EC2 instance (t2.micro - free tier)..."
    
    # Get latest Amazon Linux 2 AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" \
        --query "reverse(sort_by(Images, &CreationDate))[:1].ImageId" \
        --output text \
        --region us-east-1)
    
    print_status "Using AMI: $AMI_ID"
    
    # Create key pair
    KEY_NAME="amp-trading-key"
    print_status "Creating key pair: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > $KEY_NAME.pem
    
    chmod 400 $KEY_NAME.pem
    print_success "Key pair created: $KEY_NAME.pem"
    
    # Create security group
    SG_NAME="amp-trading-sg"
    print_status "Creating security group: $SG_NAME"
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security group for AMP trading system" \
        --query 'GroupId' --output text --region us-east-1)
    
    # Add security group rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region us-east-1
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region us-east-1
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 3000 \
        --cidr 0.0.0.0/0 \
        --region us-east-1
    
    print_success "Security group created: $SG_ID"
    
    # Create user data script
    create_user_data_script
    
    # Create EC2 instance
    print_status "Creating EC2 instance (t2.micro)..."
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type t2.micro \
        --key-name $KEY_NAME \
        --security-group-ids $SG_ID \
        --user-data file://aws/user_data.sh \
        --query 'Instances[0].InstanceId' --output text \
        --region us-east-1)
    
    print_success "EC2 instance created: $INSTANCE_ID"
    
    # Wait for instance to be running
    print_status "Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region us-east-1
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' --output text \
        --region us-east-1)
    
    print_success "Instance is running at: $PUBLIC_IP"
    
    # Save instance info
    cat > instance_info.json << EOF
{
    "instance_id": "$INSTANCE_ID",
    "public_ip": "$PUBLIC_IP",
    "security_group_id": "$SG_ID",
    "key_name": "$KEY_NAME"
}
EOF
    
    print_success "Instance information saved to instance_info.json"
}

# Create user data script for EC2
create_user_data_script() {
    print_status "Creating user data script..."
    
    cat > aws/user_data.sh << 'EOF'
#!/bin/bash

# Update system
yum update -y

# Install required packages
yum install -y python3 python3-pip git docker

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create application directory
mkdir -p /opt/amp-system
cd /opt/amp-system

# Create environment file
cat > .env << 'ENVEOF'
# AMP System Environment Configuration
AMP_TOKEN=

# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET=amp-trading-system-data
DYNAMODB_TABLE=amp-trading-system-data

# System Configuration
AMP_ENV=production
LOG_LEVEL=INFO
DEBUG=false

# Port Configuration
API_PORT=8000
GRAFANA_PORT=3000
ENVEOF

# Create docker-compose file
cat > docker-compose.yml << 'COMPOSEEOF'
version: '3.8'

services:
  amp-system:
    image: keamouyleng/genx-fx:latest
    container_name: amp-trading-system
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./reports:/app/reports
      - ./.env:/app/.env:ro
    environment:
      - PYTHONPATH=/app
      - AMP_ENV=production
      - AWS_REGION=us-east-1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: amp-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    container_name: amp-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: amp_trading
      POSTGRES_USER: amp_user
      POSTGRES_PASSWORD: amp_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  grafana:
    image: grafana/grafana:latest
    container_name: amp-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=amp_admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  redis_data:
  postgres_data:
  grafana_data:
COMPOSEEOF

# Create necessary directories
mkdir -p logs data reports

# Pull and start containers
docker-compose up -d

# Wait for containers to start
sleep 30

# Authenticate AMP system
set -a
source /opt/amp-system/.env
set +a
if [ -n "${AMP_TOKEN:-}" ]; then
  docker exec -it amp-trading-system amp auth --token "$AMP_TOKEN" || true
fi

# Start scheduler
docker exec -it amp-trading-system amp schedule --start || true

# Create startup script
cat > /opt/amp-system/start_amp.sh << 'STARTEOF'
#!/bin/bash
cd /opt/amp-system
docker-compose up -d
sleep 10
docker exec -it amp-trading-system amp schedule --start || true
echo "AMP system started successfully!"
STARTEOF

chmod +x /opt/amp-system/start_amp.sh

# Create systemd service
cat > /etc/systemd/system/amp-system.service << 'SERVICEEOF'
[Unit]
Description=AMP Trading System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/amp-system
ExecStart=/opt/amp-system/start_amp.sh
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Enable and start service
systemctl enable amp-system.service
systemctl start amp-system.service

echo "AMP system deployment completed!"
EOF
    
    print_success "User data script created"
}

# Deploy to ECS Fargate (alternative - free tier eligible)
deploy_to_ecs() {
    print_status "Deploying to ECS Fargate (free tier eligible)..."
    
    # Create ECS cluster
    aws ecs create-cluster --cluster-name amp-trading-cluster --region us-east-1
    
    # Create task definition
    cat > task-definition.json << EOF
{
    "family": "amp-trading-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "256",
    "memory": "512",
    "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "amp-trading-container",
            "image": "keamouyleng/genx-fx:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "AWS_REGION",
                    "value": "us-east-1"
                },
                {
                    "name": "AMP_ENV",
                    "value": "production"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/aws/amp-system",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF
    
    # Register task definition
    aws ecs register-task-definition --cli-input-json file://task-definition.json --region us-east-1
    
    print_success "ECS deployment configuration created"
}

# Show deployment information
show_deployment_info() {
    print_success "AMP System AWS Deployment Complete!"
    echo ""
    echo "📊 Deployment Information:"
    echo "=========================="
    
    if [ -f "instance_info.json" ]; then
        INSTANCE_IP=$(jq -r '.public_ip' instance_info.json)
        INSTANCE_ID=$(jq -r '.instance_id' instance_info.json)
        KEY_NAME=$(jq -r '.key_name' instance_info.json)
        
        echo "🌐 Public IP: $INSTANCE_IP"
        echo "🆔 Instance ID: $INSTANCE_ID"
        echo "🔑 Key File: $KEY_NAME.pem"
        echo ""
        echo "🔗 Access URLs:"
        echo "   - AMP API: http://$INSTANCE_IP:8000/health"
        echo "   - Grafana: http://$INSTANCE_IP:3000"
        echo "   - SSH: ssh -i $KEY_NAME.pem ec2-user@$INSTANCE_IP"
        echo ""
        echo "⚡ AMP CLI Commands:"
        echo "   - Status: ssh -i $KEY_NAME.pem ec2-user@$INSTANCE_IP 'docker exec -it amp-trading-system amp status'"
        echo "   - Monitor: ssh -i $KEY_NAME.pem ec2-user@$INSTANCE_IP 'docker exec -it amp-trading-system amp monitor --dashboard'"
        echo "   - Logs: ssh -i $KEY_NAME.pem ec2-user@$INSTANCE_IP 'docker logs amp-trading-system'"
    fi
    
    if [ -f "aws_config.json" ]; then
        S3_BUCKET=$(jq -r '.s3_bucket' aws_config.json)
        DYNAMODB_TABLE=$(jq -r '.dynamodb_table' aws_config.json)
        CLOUDWATCH_LOG_GROUP=$(jq -r '.cloudwatch_log_group' aws_config.json)
        
        echo ""
        echo "📦 AWS Resources:"
        echo "   - S3 Bucket: $S3_BUCKET"
        echo "   - DynamoDB Table: $DYNAMODB_TABLE"
        echo "   - CloudWatch Logs: $CLOUDWATCH_LOG_GROUP"
    fi
    
    echo ""
    echo "💰 Free Tier Information:"
    echo "   - EC2: 750 hours/month of t2.micro"
    echo "   - S3: 5GB storage"
    echo "   - DynamoDB: 25GB storage, 25 WCU/RCU"
    echo "   - CloudWatch: 5GB data ingestion"
    echo ""
    echo "🔧 Management Commands:"
    echo "   - Stop instance: aws ec2 stop-instances --instance-ids $INSTANCE_ID"
    echo "   - Start instance: aws ec2 start-instances --instance-ids $INSTANCE_ID"
    echo "   - Terminate instance: aws ec2 terminate-instances --instance-ids $INSTANCE_ID"
}

# Main deployment function
main() {
    print_status "Starting AMP System AWS deployment (Free Tier Optimized)..."
    
    # Check prerequisites
    check_aws_cli
    configure_aws
    
    # Create AWS resources
    create_aws_resources
    
    # Choose deployment method
    echo ""
    echo "Choose deployment method:"
    echo "1. EC2 Instance (t2.micro - free tier eligible)"
    echo "2. ECS Fargate (free tier eligible)"
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            create_ec2_instance
            ;;
        2)
            deploy_to_ecs
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    # Show deployment information
    show_deployment_info
    
    print_success "AMP System deployed to AWS successfully!"
}

# Run main function
main "$@"