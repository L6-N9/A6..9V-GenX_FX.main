#!/bin/bash

# AMP System AWS Deployment Setup Script
# This script helps configure AWS credentials and deploy the AMP system

set -e

echo "🚀 AMP System AWS Deployment Setup"
echo "=================================="

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

# Check if AWS credentials are configured
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

# Setup AWS credentials
setup_aws_credentials() {
    print_status "Setting up AWS credentials..."
    
    echo ""
    echo "To configure AWS credentials, you need:"
    echo "1. AWS Access Key ID"
    echo "2. AWS Secret Access Key"
    echo "3. Default region (us-east-1 for free tier)"
    echo ""
    
    # Create AWS credentials file
    mkdir -p ~/.aws
    
    cat > ~/.aws/credentials << 'EOF'
# AWS Credentials
# Replace these with your actual AWS credentials
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID_HERE
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY_HERE
EOF

    cat > ~/.aws/config << 'EOF'
# AWS Configuration
[default]
region = us-east-1
output = json
EOF

    print_warning "Please edit ~/.aws/credentials with your actual AWS credentials"
    print_status "You can get your credentials from: https://console.aws.amazon.com/iam/home#/security_credentials"
    
    echo ""
    echo "After updating credentials, run:"
    echo "  aws sts get-caller-identity"
    echo "  ./aws/amp-deploy.sh"
}

# Deploy to AWS
deploy_to_aws() {
    print_status "Starting AWS deployment..."
    
    if ! check_aws_credentials; then
        print_error "AWS credentials not configured. Please configure them first."
        setup_aws_credentials
        exit 1
    fi
    
    # Run the deployment script
    cd aws/
    ./amp-deploy.sh
}

# Show deployment information
show_deployment_info() {
    print_success "Setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "=============="
    echo ""
    echo "1. 🔑 Configure AWS Credentials:"
    echo "   - Edit ~/.aws/credentials with your actual credentials"
    echo "   - Get credentials from: https://console.aws.amazon.com/iam/home#/security_credentials"
    echo ""
    echo "2. ✅ Verify Credentials:"
    echo "   aws sts get-caller-identity"
    echo ""
    echo "3. 🚀 Deploy to AWS:"
    echo "   ./aws/amp-deploy.sh"
    echo ""
    echo "4. 📊 Monitor Deployment:"
    echo "   python3 aws_deploy_status.py"
    echo ""
    echo "💰 Free Tier Information:"
    echo "   - EC2: 750 hours/month of t2.micro"
    echo "   - S3: 5GB storage"
    echo "   - DynamoDB: 25GB storage, 25 WCU/RCU"
    echo "   - CloudWatch: 5GB data ingestion"
    echo ""
    echo "🔗 Resources:"
    echo "   - AWS Console: https://console.aws.amazon.com"
    echo "   - IAM Credentials: https://console.aws.amazon.com/iam/home#/security_credentials"
    echo "   - Cost Explorer: https://console.aws.amazon.com/cost-reports"
}

# Main function
main() {
    print_status "Checking current setup..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    print_success "AWS CLI is installed: $(aws --version)"
    
    # Check if SSH key exists
    if [ -f "amp-trading-key" ]; then
        print_success "SSH key pair found"
    else
        print_warning "SSH key pair not found. Generating..."
        ssh-keygen -t rsa -b 4096 -f amp-trading-key -N ""
        print_success "SSH key pair generated"
    fi
    
    # Check AWS credentials
    if check_aws_credentials; then
        print_success "AWS credentials are configured"
        echo ""
        echo "🎯 Ready to deploy!"
        echo "Run: ./aws/amp-deploy.sh"
    else
        print_warning "AWS credentials need to be configured"
        setup_aws_credentials
    fi
    
    show_deployment_info
}

# Handle script arguments
case "${1:-}" in
    "deploy")
        deploy_to_aws
        ;;
    "setup")
        setup_aws_credentials
        ;;
    "check")
        check_aws_credentials
        ;;
    "help"|"-h"|"--help")
        echo "AMP System AWS Deployment Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Setup AWS deployment"
        echo "  deploy     Deploy to AWS (requires credentials)"
        echo "  setup      Setup AWS credentials"
        echo "  check      Check AWS credentials"
        echo "  help       Show this help message"
        ;;
    *)
        main
        ;;
esac