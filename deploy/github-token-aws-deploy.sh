#!/bin/bash

# GitHub Token AWS Deployment Script
# Uses GitHub CLI with token authentication for AWS deployment

set -e

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

# GitHub token (provide via environment variable or --token)
GITHUB_TOKEN=${GITHUB_TOKEN:-""}

# Default values
ENVIRONMENT=${ENVIRONMENT:-"production"}
AWS_REGION=${AWS_REGION:-"us-east-1"}
BRANCH=${BRANCH:-"main"}

# Function to authenticate with GitHub
authenticate_github() {
    print_status "Authenticating with GitHub using token..."
    
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "GITHUB_TOKEN is not set. Export GITHUB_TOKEN or pass --token."
        exit 1
    fi

    # Set GitHub token for CLI
    export GITHUB_TOKEN
    
    # Test GitHub authentication
    if gh auth status &> /dev/null; then
        print_success "GitHub authentication successful"
        gh auth status
    else
        print_warning "GitHub CLI not authenticated, setting up..."
        echo "$GITHUB_TOKEN" | gh auth login --with-token
        print_success "GitHub authentication configured"
    fi
}

# Function to check AWS credentials
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS credentials are configured"
        aws sts get-caller-identity
        return 0
    else
        print_error "AWS credentials not configured"
        return 1
    fi
}

# Function to setup AWS credentials using GitHub secrets
setup_aws_from_github() {
    print_status "Setting up AWS credentials from GitHub secrets..."
    
    # Get AWS credentials from GitHub secrets (if available)
    if gh secret list &> /dev/null; then
        print_status "Checking for AWS secrets in repository..."
        
        # Try to get AWS credentials from GitHub secrets
        AWS_ACCESS_KEY_ID=$(gh secret view AWS_ACCESS_KEY_ID --repo . 2>/dev/null || echo "")
        AWS_SECRET_ACCESS_KEY=$(gh secret view AWS_SECRET_ACCESS_KEY --repo . 2>/dev/null || echo "")
        
        if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
            print_success "Found AWS credentials in GitHub secrets"
            
            # Configure AWS CLI
            aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
            aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
            aws configure set region "$AWS_REGION"
            aws configure set output json
            
            return 0
        fi
    fi
    
    print_warning "AWS credentials not found in GitHub secrets"
    return 1
}

# Function to create GitHub deployment
create_github_deployment() {
    local environment=$1
    local ref=$2
    
    print_status "Creating GitHub deployment for $environment..."
    
    # Create deployment
    DEPLOYMENT_ID=$(gh api repos/:owner/:repo/deployments \
        --method POST \
        --field environment="$environment" \
        --field ref="$ref" \
        --field description="Deployment to AWS $environment" \
        --field auto_merge=false \
        --jq '.id')
    
    print_success "Created deployment with ID: $DEPLOYMENT_ID"
    echo "$DEPLOYMENT_ID"
}

# Function to update deployment status
update_deployment_status() {
    local deployment_id=$1
    local state=$2
    local description=$3
    local url=${4:-""}
    
    print_status "Updating deployment status to: $state"
    
    if [ -n "$url" ]; then
        gh api repos/:owner/:repo/deployments/$deployment_id/statuses \
            --method POST \
            --field state="$state" \
            --field description="$description" \
            --field environment_url="$url"
    else
        gh api repos/:owner/:repo/deployments/$deployment_id/statuses \
            --method POST \
            --field state="$state" \
            --field description="$description"
    fi
}

# Function to build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    # Get ECR registry
    ECR_REGISTRY=$(aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com" 2>/dev/null && echo "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com" || echo "")
    
    if [ -z "$ECR_REGISTRY" ]; then
        print_error "Failed to get ECR registry"
        return 1
    fi
    
    # Build and push images
    IMAGE_TAG=$(git rev-parse --short HEAD)
    
    # Main API image
    print_status "Building main API image..."
    docker build -f Dockerfile.production -t "$ECR_REGISTRY/genx-api:$IMAGE_TAG" .
    docker tag "$ECR_REGISTRY/genx-api:$IMAGE_TAG" "$ECR_REGISTRY/genx-api:latest"
    docker push "$ECR_REGISTRY/genx-api:$IMAGE_TAG"
    docker push "$ECR_REGISTRY/genx-api:latest"
    
    # Discord bot image
    if [ -f "Dockerfile.discord" ]; then
        print_status "Building Discord bot image..."
        docker build -f Dockerfile.discord -t "$ECR_REGISTRY/genx-discord-bot:$IMAGE_TAG" .
        docker tag "$ECR_REGISTRY/genx-discord-bot:$IMAGE_TAG" "$ECR_REGISTRY/genx-discord-bot:latest"
        docker push "$ECR_REGISTRY/genx-discord-bot:$IMAGE_TAG"
        docker push "$ECR_REGISTRY/genx-discord-bot:latest"
    fi
    
    # Telegram bot image
    if [ -f "Dockerfile.telegram" ]; then
        print_status "Building Telegram bot image..."
        docker build -f Dockerfile.telegram -t "$ECR_REGISTRY/genx-telegram-bot:$IMAGE_TAG" .
        docker tag "$ECR_REGISTRY/genx-telegram-bot:$IMAGE_TAG" "$ECR_REGISTRY/genx-telegram-bot:latest"
        docker push "$ECR_REGISTRY/genx-telegram-bot:$IMAGE_TAG"
        docker push "$ECR_REGISTRY/genx-telegram-bot:latest"
    fi
    
    print_success "All images built and pushed successfully"
}

# Function to deploy to AWS
deploy_to_aws() {
    local environment=$1
    
    print_status "Deploying to AWS $environment environment..."
    
    # Run the existing AWS deployment script
    if [ -f "deploy/aws-deploy.sh" ]; then
        chmod +x deploy/aws-deploy.sh
        ./deploy/aws-deploy.sh \
            --region "$AWS_REGION" \
            --environment "$environment"
    else
        print_error "AWS deployment script not found"
        return 1
    fi
}

# Function to get deployment URL
get_deployment_url() {
    local environment=$1
    
    print_status "Getting deployment URL..."
    
    STACK_NAME="$environment-genx-trading-platform"
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$ALB_DNS" ]; then
        print_success "Application URL: http://$ALB_DNS"
        echo "http://$ALB_DNS"
    else
        print_warning "Could not retrieve deployment URL"
        echo ""
    fi
}

# Function to perform health check
health_check() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    print_status "Performing health check on $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url/health" > /dev/null 2>&1; then
            print_success "Health check passed!"
            return 0
        fi
        
        print_status "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    print_error "Health check failed after $max_attempts attempts"
    return 1
}

# Main deployment function
main_deployment() {
    print_status "Starting GitHub Token AWS Deployment"
    print_status "Environment: $ENVIRONMENT"
    print_status "Region: $AWS_REGION"
    print_status "Branch: $BRANCH"
    
    # Step 1: Authenticate with GitHub
    authenticate_github
    
    # Step 2: Setup AWS credentials
    if ! check_aws_credentials; then
        if ! setup_aws_from_github; then
            print_error "Failed to setup AWS credentials"
            exit 1
        fi
    fi
    
    # Step 3: Create GitHub deployment
    DEPLOYMENT_ID=$(create_github_deployment "$ENVIRONMENT" "$BRANCH")
    
    # Step 4: Update deployment status to in_progress
    update_deployment_status "$DEPLOYMENT_ID" "in_progress" "Starting deployment to AWS"
    
    # Step 5: Build and push Docker images
    if build_and_push_images; then
        print_success "Docker images built and pushed successfully"
    else
        update_deployment_status "$DEPLOYMENT_ID" "failure" "Failed to build and push Docker images"
        exit 1
    fi
    
    # Step 6: Deploy to AWS
    if deploy_to_aws "$ENVIRONMENT"; then
        print_success "AWS deployment completed successfully"
    else
        update_deployment_status "$DEPLOYMENT_ID" "failure" "Failed to deploy to AWS"
        exit 1
    fi
    
    # Step 7: Get deployment URL
    DEPLOYMENT_URL=$(get_deployment_url "$ENVIRONMENT")
    
    # Step 8: Perform health check
    if [ -n "$DEPLOYMENT_URL" ]; then
        if health_check "$DEPLOYMENT_URL"; then
            update_deployment_status "$DEPLOYMENT_ID" "success" "Deployment successful and healthy" "$DEPLOYMENT_URL"
            print_success "Deployment completed successfully!"
            print_success "Application URL: $DEPLOYMENT_URL"
        else
            update_deployment_status "$DEPLOYMENT_ID" "failure" "Deployment completed but health check failed" "$DEPLOYMENT_URL"
            print_error "Deployment completed but health check failed"
            exit 1
        fi
    else
        update_deployment_status "$DEPLOYMENT_ID" "success" "Deployment completed" 
        print_success "Deployment completed successfully!"
    fi
}

# Function to show help
show_help() {
    echo "GitHub Token AWS Deployment Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment to deploy to (default: production)"
    echo "  -r, --region REGION      AWS region (default: us-east-1)"
    echo "  -b, --branch BRANCH      Git branch to deploy (default: main)"
    echo "  -t, --token TOKEN        GitHub token (default: uses GITHUB_TOKEN env var)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  GITHUB_TOKEN             GitHub personal access token"
    echo "  AWS_ACCESS_KEY_ID        AWS access key ID"
    echo "  AWS_SECRET_ACCESS_KEY    AWS secret access key"
    echo "  AWS_REGION               AWS region"
    echo ""
    echo "Examples:"
    echo "  $0 --environment staging --region us-west-2"
    echo "  $0 -e production -r us-east-1 -b main"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -t|--token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it first."
    print_status "Installation guide: https://github.com/cli/cli#installation"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    print_status "Installation guide: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Run main deployment
main_deployment