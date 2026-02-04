#!/bin/bash

# GitHub Token AWS Deployment Setup Script
# This script sets up the environment for GitHub token-based AWS deployment

set -e

echo "🚀 GitHub Token AWS Deployment Setup"
echo "===================================="

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

# GitHub token MUST be provided via environment variable.
#   export GITHUB_TOKEN=...
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install GitHub CLI
install_github_cli() {
    print_status "Installing GitHub CLI..."
    
    if command_exists gh; then
        print_success "GitHub CLI is already installed: $(gh --version | head -n1)"
        return 0
    fi
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Ubuntu/Debian
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt-get update
            sudo apt-get install gh -y
        elif command_exists yum; then
            # CentOS/RHEL
            sudo yum install gh -y
        elif command_exists dnf; then
            # Fedora
            sudo dnf install gh -y
        else
            print_error "Unsupported Linux distribution"
            return 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install gh
        else
            print_error "Homebrew not found. Please install Homebrew first."
            return 1
        fi
    else
        print_error "Unsupported operating system"
        return 1
    fi
    
    if command_exists gh; then
        print_success "GitHub CLI installed successfully: $(gh --version | head -n1)"
        return 0
    else
        print_error "Failed to install GitHub CLI"
        return 1
    fi
}

# Function to install AWS CLI
install_aws_cli() {
    print_status "Installing AWS CLI..."
    
    if command_exists aws; then
        print_success "AWS CLI is already installed: $(aws --version)"
        return 0
    fi
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    else
        print_error "Unsupported operating system"
        return 1
    fi
    
    if command_exists aws; then
        print_success "AWS CLI installed successfully: $(aws --version)"
        return 0
    else
        print_error "Failed to install AWS CLI"
        return 1
    fi
}

# Function to install Docker
install_docker() {
    print_status "Installing Docker..."
    
    if command_exists docker; then
        print_success "Docker is already installed: $(docker --version)"
        return 0
    fi
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io
            sudo usermod -aG docker $USER
        elif command_exists yum; then
            # CentOS/RHEL
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
        else
            print_error "Unsupported Linux distribution"
            return 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install --cask docker
        else
            print_error "Homebrew not found. Please install Homebrew first."
            return 1
        fi
    else
        print_error "Unsupported operating system"
        return 1
    fi
    
    if command_exists docker; then
        print_success "Docker installed successfully: $(docker --version)"
        return 0
    else
        print_error "Failed to install Docker"
        return 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if command_exists pip3; then
        pip3 install boto3 docker requests
        print_success "Python dependencies installed successfully"
        return 0
    elif command_exists pip; then
        pip install boto3 docker requests
        print_success "Python dependencies installed successfully"
        return 0
    else
        print_error "pip not found. Please install Python and pip first."
        return 1
    fi
}

# Function to setup GitHub authentication
setup_github_auth() {
    print_status "Setting up GitHub authentication..."
    
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "GITHUB_TOKEN is not set. Export GITHUB_TOKEN before running."
        return 1
    fi

    # Set GitHub token as environment variable
    export GITHUB_TOKEN
    
    # Test GitHub authentication
    if gh auth status &> /dev/null; then
        print_success "GitHub authentication successful"
        gh auth status
        return 0
    else
        print_warning "GitHub CLI not authenticated, setting up..."
        echo "$GITHUB_TOKEN" | gh auth login --with-token
        if gh auth status &> /dev/null; then
            print_success "GitHub authentication configured successfully"
            return 0
        else
            print_error "Failed to configure GitHub authentication"
            return 1
        fi
    fi
}

# Function to setup AWS credentials
setup_aws_credentials() {
    print_status "Setting up AWS credentials..."
    
    if aws sts get-caller-identity &> /dev/null; then
        print_success "AWS credentials are already configured"
        aws sts get-caller-identity
        return 0
    fi
    
    print_warning "AWS credentials not configured"
    echo ""
    echo "📋 To configure AWS credentials, you need:"
    echo "1. AWS Access Key ID"
    echo "2. AWS Secret Access Key"
    echo "3. Default region (us-east-1 for free tier)"
    echo ""
    echo "🔗 Get your credentials from: https://console.aws.amazon.com/iam/home#/security_credentials"
    echo ""
    
    read -p "Do you want to configure AWS credentials now? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Enter your AWS Access Key ID:"
        read -p "Access Key ID: " AWS_ACCESS_KEY_ID
        
        echo "Enter your AWS Secret Access Key:"
        read -s -p "Secret Access Key: " AWS_SECRET_ACCESS_KEY
        echo
        
        # Configure AWS CLI
        aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
        aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
        aws configure set region "us-east-1"
        aws configure set output json
        
        if aws sts get-caller-identity &> /dev/null; then
            print_success "AWS credentials configured successfully"
            aws sts get-caller-identity
            return 0
        else
            print_error "Failed to configure AWS credentials"
            return 1
        fi
    else
        print_warning "AWS credentials setup skipped"
        return 1
    fi
}

# Function to create deployment scripts
create_deployment_scripts() {
    print_status "Creating deployment scripts..."
    
    # Make scripts executable
    if [ -f "deploy/github-token-aws-deploy.sh" ]; then
        chmod +x deploy/github-token-aws-deploy.sh
        print_success "GitHub token AWS deployment script is ready"
    fi
    
    if [ -f "deploy/github_aws_deploy.py" ]; then
        chmod +x deploy/github_aws_deploy.py
        print_success "Python GitHub AWS deployment script is ready"
    fi
    
    # Create a simple deployment script
    cat > deploy-with-github-token.sh << 'EOF'
#!/bin/bash

# Simple deployment script using GitHub token
set -e

echo "🚀 Deploying with GitHub Token to AWS"
echo "====================================="

# Set GitHub token
: "${GITHUB_TOKEN:?Set GITHUB_TOKEN in your environment before running.}"
export GITHUB_TOKEN

# Default values
ENVIRONMENT=${1:-"production"}
REGION=${2:-"us-east-1"}

echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"

# Check if Python script exists and run it
if [ -f "deploy/github_aws_deploy.py" ]; then
    echo "Running Python deployment script..."
    python3 deploy/github_aws_deploy.py \
        --environment "$ENVIRONMENT" \
        --region "$REGION" \
        --token "$GITHUB_TOKEN"
elif [ -f "deploy/github-token-aws-deploy.sh" ]; then
    echo "Running Bash deployment script..."
    ./deploy/github-token-aws-deploy.sh \
        --environment "$ENVIRONMENT" \
        --region "$REGION" \
        --token "$GITHUB_TOKEN"
else
    echo "No deployment script found"
    exit 1
fi
EOF

    chmod +x deploy-with-github-token.sh
    print_success "Simple deployment script created: deploy-with-github-token.sh"
}

# Function to setup GitHub secrets (if possible)
setup_github_secrets() {
    print_status "Setting up GitHub repository secrets..."
    
    if gh auth status &> /dev/null; then
        print_status "Checking if we can access repository secrets..."
        
        # Note: GitHub CLI doesn't allow setting secrets directly from command line
        # This would need to be done through the GitHub web interface
        print_warning "GitHub secrets must be set manually through the web interface"
        echo ""
        echo "🔗 Set up secrets at: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
        echo ""
        echo "Required secrets:"
        echo "- AWS_ACCESS_KEY_ID: Your AWS access key"
        echo "- AWS_SECRET_ACCESS_KEY: Your AWS secret key"
        echo "- AWS_ROLE_ARN: Your AWS role ARN (if using IAM roles)"
        echo "- SLACK_WEBHOOK_URL: Your Slack webhook URL (optional)"
        echo ""
    else
        print_warning "GitHub CLI not authenticated, skipping secrets setup"
    fi
}

# Function to test the setup
test_setup() {
    print_status "Testing the setup..."
    
    # Test GitHub CLI
    if command_exists gh; then
        if gh auth status &> /dev/null; then
            print_success "✅ GitHub CLI is working"
        else
            print_error "❌ GitHub CLI authentication failed"
        fi
    else
        print_error "❌ GitHub CLI not found"
    fi
    
    # Test AWS CLI
    if command_exists aws; then
        if aws sts get-caller-identity &> /dev/null; then
            print_success "✅ AWS CLI is working"
        else
            print_warning "⚠️  AWS CLI found but not configured"
        fi
    else
        print_error "❌ AWS CLI not found"
    fi
    
    # Test Docker
    if command_exists docker; then
        if docker --version &> /dev/null; then
            print_success "✅ Docker is working"
        else
            print_error "❌ Docker not working properly"
        fi
    else
        print_error "❌ Docker not found"
    fi
    
    # Test Python dependencies
    if python3 -c "import boto3, docker, requests" 2>/dev/null; then
        print_success "✅ Python dependencies are installed"
    else
        print_error "❌ Python dependencies are missing"
    fi
}

# Function to show next steps
show_next_steps() {
    print_success "Setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "=============="
    echo ""
    echo "1. 🔑 Configure AWS Credentials (if not done):"
    echo "   aws configure"
    echo ""
    echo "2. 🚀 Deploy using GitHub token:"
    echo "   ./deploy-with-github-token.sh"
    echo "   # or"
    echo "   python3 deploy/github_aws_deploy.py --environment production"
    echo "   # or"
    echo "   ./deploy/github-token-aws-deploy.sh --environment production"
    echo ""
    echo "3. 🔄 Manual deployment options:"
    echo "   - Use GitHub Actions: .github/workflows/github-token-aws-deploy.yml"
    echo "   - Use existing scripts: deploy/aws-deploy.sh"
    echo "   - Use quick deployment: quick_aws_deploy.sh"
    echo ""
    echo "4. 📊 Monitor deployment:"
    echo "   - GitHub: Check deployment status in repository"
    echo "   - AWS: Check CloudFormation stacks"
    echo "   - Application: Health check endpoint"
    echo ""
    echo "🔗 Useful Commands:"
    echo "=================="
    echo "gh auth status                    # Check GitHub authentication"
    echo "aws sts get-caller-identity      # Check AWS credentials"
    echo "docker --version                  # Check Docker installation"
    echo "python3 -c 'import boto3, docker, requests'  # Check Python deps"
    echo ""
}

# Main function
main() {
    print_status "Starting GitHub Token AWS Deployment Setup"
    
    # Step 1: Install required tools
    install_github_cli
    install_aws_cli
    install_docker
    install_python_deps
    
    # Step 2: Setup authentication
    setup_github_auth
    setup_aws_credentials
    
    # Step 3: Create deployment scripts
    create_deployment_scripts
    
    # Step 4: Setup GitHub secrets (informational)
    setup_github_secrets
    
    # Step 5: Test the setup
    test_setup
    
    # Step 6: Show next steps
    show_next_steps
}

# Handle script arguments
case "${1:-}" in
    "test")
        test_setup
        ;;
    "github")
        install_github_cli
        setup_github_auth
        ;;
    "aws")
        install_aws_cli
        setup_aws_credentials
        ;;
    "docker")
        install_docker
        ;;
    "python")
        install_python_deps
        ;;
    "help"|"-h"|"--help")
        echo "GitHub Token AWS Deployment Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Complete setup"
        echo "  test       Test current setup"
        echo "  github     Install and setup GitHub CLI only"
        echo "  aws        Install and setup AWS CLI only"
        echo "  docker     Install Docker only"
        echo "  python     Install Python dependencies only"
        echo "  help       Show this help message"
        ;;
    *)
        main
        ;;
esac