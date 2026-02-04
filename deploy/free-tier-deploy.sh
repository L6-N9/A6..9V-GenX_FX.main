#!/bin/bash

# GenX FX AWS Free Tier Deployment Script
# Optimized for AWS Free Tier usage

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="genx-fx"
AWS_REGION="us-east-1"
ENVIRONMENT="production"
STACK_NAME="${ENVIRONMENT}-${PROJECT_NAME}-free-tier"

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if key pair exists
    if [ -z "$KEY_PAIR_NAME" ]; then
        print_error "Please set KEY_PAIR_NAME environment variable or pass --key-pair parameter"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create EC2 key pair if it doesn't exist
create_key_pair() {
    print_status "Checking EC2 key pair: $KEY_PAIR_NAME"
    
    if ! aws ec2 describe-key-pairs --key-names "$KEY_PAIR_NAME" --region "$AWS_REGION" &> /dev/null; then
        print_status "Creating new key pair: $KEY_PAIR_NAME"
        aws ec2 create-key-pair --key-name "$KEY_PAIR_NAME" --region "$AWS_REGION" --query 'KeyMaterial' --output text > "${KEY_PAIR_NAME}.pem"
        chmod 400 "${KEY_PAIR_NAME}.pem"
        print_success "Key pair created and saved as ${KEY_PAIR_NAME}.pem"
    else
        print_warning "Key pair $KEY_PAIR_NAME already exists"
    fi
}

# Function to deploy CloudFormation stack
deploy_stack() {
    print_status "Deploying CloudFormation stack: $STACK_NAME"
    
    aws cloudformation deploy \
        --template-file deploy/aws-free-tier-deploy.yml \
        --stack-name "$STACK_NAME" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
            KeyPairName="$KEY_PAIR_NAME" \
        --capabilities CAPABILITY_IAM \
        --region "$AWS_REGION"
    
    print_success "CloudFormation stack deployed successfully"
}

# Function to get stack outputs
get_stack_outputs() {
    print_status "Getting deployment information..."
    
    local instance_ip=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`InstancePublicIP`].OutputValue' \
        --output text)
    
    local app_url=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
        --output text)
    
    local ssh_command=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`SSHCommand`].OutputValue' \
        --output text)
    
    print_success "Deployment completed successfully!"
    echo ""
    echo "=== GenX FX Deployment Information ==="
    echo "Instance IP: $instance_ip"
    echo "Application URL: $app_url"
    echo "SSH Command: $ssh_command"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Wait 5-10 minutes for the application to start"
    echo "2. Access your trading platform at: $app_url"
    echo "3. SSH into the server: $ssh_command"
    echo "4. Check logs: docker logs genx-fx"
    echo ""
    echo "=== Free Tier Usage ==="
    echo "✅ EC2 t2.micro: 750 hours/month (FREE)"
    echo "✅ CloudWatch Logs: 5GB/month (FREE)"
    echo "✅ Data Transfer: 15GB/month (FREE)"
    echo ""
}

# Function to monitor deployment
monitor_deployment() {
    print_status "Monitoring deployment status..."
    
    local instance_id=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
        --output text)
    
    if [ -n "$instance_id" ]; then
        print_status "Waiting for instance to be running..."
        aws ec2 wait instance-running --instance-ids "$instance_id" --region "$AWS_REGION"
        print_success "Instance is running"
    fi
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up basic monitoring..."
    
    # Create CloudWatch alarm for high CPU usage
    aws cloudwatch put-metric-alarm \
        --alarm-name "${STACK_NAME}-high-cpu" \
        --alarm-description "High CPU usage on GenX FX instance" \
        --metric-name CPUUtilization \
        --namespace AWS/EC2 \
        --statistic Average \
        --period 300 \
        --threshold 80 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2 \
        --region "$AWS_REGION" \
        --dimensions Name=InstanceId,Value=$(aws cloudformation describe-stack-resources --stack-name "$STACK_NAME" --region "$AWS_REGION" --query 'StackResources[?ResourceType==`AWS::EC2::Instance`].PhysicalResourceId' --output text)
    
    print_success "Basic monitoring configured"
}

# Function to create simple backup script
create_backup_script() {
    print_status "Creating backup script..."
    
    cat > backup-genx.sh << 'EOF'
#!/bin/bash
# Simple backup script for GenX FX data

BACKUP_DIR="/home/ec2-user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup application data
docker exec genx-fx tar czf - /app/data /app/logs 2>/dev/null | cat > "$BACKUP_DIR/genx-data-$DATE.tar.gz"

# Keep only last 7 backups
find $BACKUP_DIR -name "genx-data-*.tar.gz" -mtime +7 -delete

echo "Backup completed: genx-data-$DATE.tar.gz"
EOF
    
    chmod +x backup-genx.sh
    print_success "Backup script created: backup-genx.sh"
}

# Function to show cost optimization tips
show_cost_tips() {
    print_warning "AWS Free Tier Cost Optimization Tips:"
    echo ""
    echo "1. Monitor your usage in AWS Billing Dashboard"
    echo "2. Set up billing alerts for $1, $5, $10"
    echo "3. Stop the instance when not trading: aws ec2 stop-instances --instance-ids <instance-id>"
    echo "4. Use CloudWatch to monitor resource usage"
    echo "5. Clean up unused resources regularly"
    echo ""
    echo "Estimated monthly cost (after free tier): $5-15/month"
}

# Main deployment function
main() {
    print_status "Starting GenX FX AWS Free Tier Deployment"
    echo ""
    
    check_prerequisites
    create_key_pair
    deploy_stack
    monitor_deployment
    setup_monitoring
    get_stack_outputs
    create_backup_script
    show_cost_tips
    
    print_success "GenX FX deployment completed successfully!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            STACK_NAME="${ENVIRONMENT}-${PROJECT_NAME}-free-tier"
            shift 2
            ;;
        --key-pair)
            KEY_PAIR_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --region REGION     AWS region (default: us-east-1)"
            echo "  --environment ENV   Environment name (default: production)"
            echo "  --key-pair NAME     EC2 key pair name (required)"
            echo "  --help              Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --key-pair my-genx-key --region us-east-1"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set default key pair name if not provided
if [ -z "$KEY_PAIR_NAME" ]; then
    KEY_PAIR_NAME="genx-fx-key"
fi

# Run main function
main