#!/bin/bash

# Quick AWS Deployment Script for AMP System
# This script helps you deploy your AMP system to AWS quickly

set -e

echo "🚀 Quick AWS Deployment for AMP System"
echo "======================================"

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

# Check if AWS credentials are configured
check_credentials() {
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS credentials are configured!"
        aws sts get-caller-identity
        return 0
    else
        return 1
    fi
}

# Setup credentials manually
setup_credentials_manual() {
    print_status "Setting up AWS credentials manually..."
    
    echo ""
    echo "📋 Follow these steps to get your AWS credentials:"
    echo "=================================================="
    echo ""
    echo "1. 🌐 Open AWS Console:"
    echo "   https://console.aws.amazon.com"
    echo ""
    echo "2. 🔑 Login with:"
    echo "   (Use your AWS account credentials)"
    echo ""
    echo "3. 👤 Click on 'keamouyleng' (top right corner)"
    echo ""
    echo "4. 🔐 Click 'Security credentials'"
    echo ""
    echo "5. 🔑 Scroll to 'Access keys' and click 'Create access key'"
    echo ""
    echo "6. ✅ Choose 'Command Line Interface (CLI)'"
    echo ""
    echo "7. 📋 Copy your Access Key ID and Secret Access Key"
    echo ""
    
    read -p "Press Enter when you have your credentials ready..."
    
    echo ""
    echo "🔧 Now let's configure your credentials:"
    echo "========================================"
    
    # Create credentials file
    mkdir -p ~/.aws
    
    echo "Enter your AWS Access Key ID:"
    read -p "Access Key ID: " ACCESS_KEY_ID
    
    echo "Enter your AWS Secret Access Key:"
    read -s -p "Secret Access Key: " SECRET_ACCESS_KEY
    echo ""
    
    # Save credentials
    cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $ACCESS_KEY_ID
aws_secret_access_key = $SECRET_ACCESS_KEY
EOF

    cat > ~/.aws/config << EOF
[default]
region = us-east-1
output = json
EOF

    print_success "Credentials saved!"
    
    # Test credentials
    if check_credentials; then
        print_success "Credentials are working!"
        return 0
    else
        print_error "Credentials test failed. Please check your credentials."
        return 1
    fi
}

# Deploy to AWS
deploy_to_aws() {
    print_status "Starting AWS deployment..."
    
    if ! check_credentials; then
        print_error "AWS credentials not configured."
        setup_credentials_manual
    fi
    
    print_status "Deploying AMP system to AWS..."
    
    # Run the deployment script
    cd aws/
    ./amp-deploy.sh
}

# Show deployment info
show_info() {
    echo ""
    echo "🎯 What will be deployed:"
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
    echo "🔗 After deployment, you'll get:"
    echo "   - AMP API: http://<PUBLIC_IP>:8000/health"
    echo "   - Grafana: http://<PUBLIC_IP>:3000"
    echo "   - SSH Access: ssh -i amp-trading-key.pem ec2-user@<PUBLIC_IP>"
    echo ""
}

# Main function
main() {
    print_status "Checking current setup..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install it first."
        exit 1
    fi
    
    print_success "AWS CLI is installed: $(aws --version)"
    
    # Check SSH key
    if [ -f "amp-trading-key" ]; then
        print_success "SSH key found"
    else
        print_warning "SSH key not found. Generating..."
        ssh-keygen -t rsa -b 4096 -f amp-trading-key -N ""
        print_success "SSH key generated"
    fi
    
    show_info
    
    # Check credentials
    if check_credentials; then
        print_success "AWS credentials are configured!"
        echo ""
        echo "🚀 Ready to deploy!"
        read -p "Press Enter to start deployment..."
        deploy_to_aws
    else
        print_warning "AWS credentials need to be configured"
        setup_credentials_manual
        if check_credentials; then
            echo ""
            echo "🚀 Ready to deploy!"
            read -p "Press Enter to start deployment..."
            deploy_to_aws
        fi
    fi
}

# Handle arguments
case "${1:-}" in
    "deploy")
        deploy_to_aws
        ;;
    "setup")
        setup_credentials_manual
        ;;
    "check")
        check_credentials
        ;;
    "help"|"-h"|"--help")
        echo "Quick AWS Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Setup and deploy"
        echo "  deploy     Deploy to AWS"
        echo "  setup      Setup AWS credentials"
        echo "  check      Check AWS credentials"
        echo "  help       Show this help"
        ;;
    *)
        main
        ;;
esac