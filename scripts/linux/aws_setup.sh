#!/bin/bash

# GenX_FX AWS CLI Setup Script
# This script sets up AWS CLI and configures it for the GenX_FX trading system

set -e

echo "🚀 Setting up AWS CLI for GenX_FX Trading System..."

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

# Check if AWS CLI is installed
check_aws_cli() {
    if command -v aws &> /dev/null; then
        print_success "AWS CLI is already installed"
        aws --version
        return 0
    else
        print_warning "AWS CLI not found. Installing..."
        return 1
    fi
}

# Install AWS CLI based on OS
install_aws_cli() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        print_status "Installing AWS CLI on Linux..."
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_status "Installing AWS CLI on macOS..."
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        print_status "Installing AWS CLI on Windows..."
        print_warning "Please download and install AWS CLI from: https://awscli.amazonaws.com/AWSCLIV2.msi"
        return 1
    else
        print_error "Unsupported OS: $OSTYPE"
        return 1
    fi
}

# Configure AWS CLI
configure_aws() {
    print_status "Configuring AWS CLI..."
    
    # Check if already configured
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS CLI is already configured"
        aws sts get-caller-identity
        return 0
    fi
    
    print_status "Please provide your AWS credentials:"
    echo "You can get these from the AWS Console > IAM > Users > Your User > Security credentials"
    echo ""
    
    read -p "Enter AWS Access Key ID: " aws_access_key_id
    read -s -p "Enter AWS Secret Access Key: " aws_secret_access_key
    echo ""
    read -p "Enter AWS Region (e.g., us-east-1): " aws_region
    
    # Configure AWS CLI
    aws configure set aws_access_key_id "$aws_access_key_id"
    aws configure set aws_secret_access_key "$aws_secret_access_key"
    aws configure set default.region "$aws_region"
    aws configure set default.output json
    
    print_success "AWS CLI configured successfully!"
}

# Create AWS resources for GenX_FX
create_aws_resources() {
    print_status "Creating AWS resources for GenX_FX..."
    
    # Create S3 bucket for data storage
    bucket_name="genx-fx-trading-data-$(date +%s)"
    print_status "Creating S3 bucket: $bucket_name"
    aws s3 mb s3://$bucket_name --region $(aws configure get default.region)
    
    # Create DynamoDB table for trading signals
    table_name="genx-fx-trading-signals"
    print_status "Creating DynamoDB table: $table_name"
    aws dynamodb create-table \
        --table-name $table_name \
        --attribute-definitions AttributeName=signal_id,AttributeType=S AttributeName=timestamp,AttributeType=S \
        --key-schema AttributeName=signal_id,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --region $(aws configure get default.region)
    
    # Create CloudWatch log group
    log_group_name="/aws/genx-fx/trading-logs"
    print_status "Creating CloudWatch log group: $log_group_name"
    aws logs create-log-group --log-group-name $log_group_name --region $(aws configure get default.region)
    
    # Save configuration
    cat > aws_config.json << EOF
{
    "s3_bucket": "$bucket_name",
    "dynamodb_table": "$table_name",
    "cloudwatch_log_group": "$log_group_name",
    "region": "$(aws configure get default.region)"
}
EOF
    
    print_success "AWS resources created successfully!"
    print_status "Configuration saved to aws_config.json"
}

# Create IAM role for EC2 instances
create_iam_role() {
    print_status "Creating IAM role for GenX_FX EC2 instances..."
    
    role_name="GenXFXEC2Role"
    policy_name="GenXFXEC2Policy"
    
    # Create trust policy
    cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
    
    # Create IAM role
    aws iam create-role --role-name $role_name --assume-role-policy-document file://trust-policy.json
    
    # Create policy document
    cat > policy-document.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::genx-fx-trading-data-*",
                "arn:aws:s3:::genx-fx-trading-data-*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/genx-fx-trading-signals"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/genx-fx/*"
        }
    ]
}
EOF
    
    # Create policy
    aws iam create-policy --policy-name $policy_name --policy-document file://policy-document.json
    
    # Attach policy to role
    aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/$policy_name
    
    # Create instance profile
    aws iam create-instance-profile --instance-profile-name $role_name
    aws iam add-role-to-instance-profile --instance-profile-name $role_name --role-name $role_name
    
    # Cleanup
    rm -f trust-policy.json policy-document.json
    
    print_success "IAM role created successfully!"
}

# Main execution
main() {
    print_status "Starting AWS CLI setup for GenX_FX..."
    
    # Check and install AWS CLI
    if ! check_aws_cli; then
        install_aws_cli
    fi
    
    # Configure AWS CLI
    configure_aws
    
    # Create AWS resources
    create_aws_resources
    
    # Create IAM role
    create_iam_role
    
    print_success "AWS CLI setup completed successfully!"
    print_status "Next steps:"
    echo "1. Review aws_config.json for your AWS resource configuration"
    echo "2. Use the provided AWS integration scripts in the aws/ directory"
    echo "3. Deploy your GenX_FX trading system to AWS"
}

# Run main function
main "$@" 