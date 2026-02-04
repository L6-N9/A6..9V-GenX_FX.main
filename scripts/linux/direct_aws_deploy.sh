#!/bin/bash

# Direct AWS Deployment Script for AMP System
# Uses provided AMP token and streamlined process

set -e

echo "🚀 Direct AWS Deployment for AMP System"
echo "======================================="

# AMP Token (provide via environment variable)
: "${AMP_TOKEN:?Set AMP_TOKEN in your environment before running.}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check AWS CLI
check_aws_cli() {
    if command -v aws &> /dev/null; then
        print_success "AWS CLI is installed: $(aws --version)"
        return 0
    else
        print_error "AWS CLI not found"
        return 1
    fi
}

# Check AWS credentials
check_aws_credentials() {
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS credentials are configured"
        aws sts get-caller-identity
        return 0
    else
        print_warning "AWS credentials not configured"
        return 1
    fi
}

# Setup AWS credentials template
setup_aws_template() {
    print_status "Setting up AWS credentials template..."
    
    mkdir -p ~/.aws
    
    cat > ~/.aws/credentials << 'EOF'
# AWS Credentials Template
# Replace these with your actual AWS credentials from console
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID_HERE
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY_HERE
EOF

    cat > ~/.aws/config << 'EOF'
[default]
region = us-east-1
output = json
EOF

    print_success "AWS credentials template created"
    print_warning "Please edit ~/.aws/credentials with your actual credentials"
}

# Create deployment package
create_deployment_package() {
    print_status "Creating deployment package..."
    
    # Update environment file with AMP token
    cat > .env << EOF
# AMP System Environment Configuration
AMP_TOKEN=$AMP_TOKEN

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
EOF

    print_success "Environment file created with AMP token"
}

# Show deployment instructions
show_deployment_instructions() {
    echo ""
    echo "📋 AWS Deployment Instructions"
    echo "============================="
    echo ""
    echo "1. 🔑 Get AWS Credentials:"
    echo "   - Go to: https://console.aws.amazon.com"
    echo "   - In IAM, create an access key for your deployment user"
    echo "   - Create access key for CLI"
    echo ""
    echo "2. ⚙️ Configure Credentials:"
    echo "   nano ~/.aws/credentials"
    echo "   # Replace with your actual credentials"
    echo ""
    echo "3. ✅ Test Credentials:"
    echo "   aws sts get-caller-identity"
    echo ""
    echo "4. 🚀 Deploy to AWS:"
    echo "   ./aws/amp-deploy.sh"
    echo ""
    echo "5. 📊 Monitor Deployment:"
    echo "   python3 aws_deploy_status.py"
    echo ""
}

# Show what will be deployed
show_deployment_info() {
    echo ""
    echo "🎯 What Will Be Deployed:"
    echo "========================"
    echo "✅ EC2 Instance (t2.micro - free tier)"
    echo "✅ VPC & Security Groups"
    echo "✅ S3 Bucket (5GB free storage)"
    echo "✅ DynamoDB Table (25GB free)"
    echo "✅ CloudWatch Logs"
    echo "✅ AMP Trading System (Docker)"
    echo "✅ Grafana Dashboard"
    echo "✅ PostgreSQL Database"
    echo "✅ Redis Cache"
    echo ""
    echo "💰 Cost: $0 for first 12 months (AWS Free Tier)"
    echo ""
    echo "🔗 After deployment:"
    echo "   - AMP API: http://<PUBLIC_IP>:8000/health"
    echo "   - Grafana: http://<PUBLIC_IP>:3000"
    echo "   - SSH: ssh -i amp-trading-key.pem ec2-user@<PUBLIC_IP>"
    echo ""
}

# Main function
main() {
    print_status "Setting up direct AWS deployment..."
    
    # Check AWS CLI
    if ! check_aws_cli; then
        print_error "Please install AWS CLI first"
        exit 1
    fi
    
    # Check SSH key
    if [ ! -f "amp-trading-key" ]; then
        print_warning "SSH key not found. Generating..."
        ssh-keygen -t rsa -b 4096 -f amp-trading-key -N ""
        print_success "SSH key generated"
    else
        print_success "SSH key found"
    fi
    
    # Setup AWS credentials template
    setup_aws_template
    
    # Create deployment package
    create_deployment_package
    
    # Check if credentials are configured
    if check_aws_credentials; then
        print_success "AWS credentials are ready!"
        echo ""
        echo "🚀 Ready to deploy! Run:"
        echo "   ./aws/amp-deploy.sh"
    else
        print_warning "AWS credentials need to be configured"
        show_deployment_instructions
    fi
    
    show_deployment_info
    
    echo ""
    echo "🎉 Setup complete! Follow the instructions above to deploy."
    echo ""
    echo "📞 Quick Commands:"
    echo "   aws sts get-caller-identity  # Test credentials"
    echo "   ./aws/amp-deploy.sh          # Deploy to AWS"
    echo "   python3 aws_deploy_status.py # Check status"
}

# Run main function
main "$@"