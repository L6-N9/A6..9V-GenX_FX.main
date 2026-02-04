#!/bin/bash

# Automated GitHub Secrets and Variables Setup
# Using provided credentials and tokens

set -e

echo "🔐 Automated GitHub Secrets Setup for AMP System"
echo "================================================"

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

# Check GitHub authentication
check_gh_auth() {
    if gh auth status &> /dev/null; then
        print_success "GitHub CLI is authenticated"
        return 0
    else
        print_error "GitHub CLI not authenticated"
        return 1
    fi
}

# Setup AMP Token (provide via environment variable)
setup_amp_secret() {
    print_status "Setting up AMP Token secret..."
    
    if [ -z "${AMP_TOKEN:-}" ]; then
        print_error "AMP_TOKEN is not set. Export AMP_TOKEN before running."
        return 1
    fi

    gh secret set AMP_TOKEN --body "$AMP_TOKEN"
    print_success "AMP Token secret configured (from environment)"
}

# Setup GenX container digests (GitHub Packages / GHCR)
setup_genx_container_digests() {
    print_status "Setting up GenX container digest secrets..."

    gh secret set GENX_GHCR_IMAGE --body "ghcr.io/mouy-leng/genx"
    gh secret set GENX_CONTAINER_DIGEST_MAIN --body "sha256:cbdd7132acf1cc3000d1965ac9ac0f7c8e425f0f2ac5e0080764e87279233f21"
    gh secret set GENX_CONTAINER_DIGEST_2 --body "sha256:3d8a19989bb281c070cc8b478317f904741a52e9ac18a4c3e9d15965715c9372"
    gh secret set GENX_CONTAINER_DIGEST_3 --body "sha256:c253aa7ab5d40949ff74f6aa00925087b212168efe8b7c4b60976c599ed11a76"

    print_success "GenX container digest secrets configured"
}

# Setup Docker Hub secrets (using provided username)
setup_docker_secrets() {
    print_status "Setting up Docker Hub secrets..."
    
    DOCKER_USERNAME="keamouyleng"
    
    # Set username
    gh secret set DOCKER_USERNAME --body "$DOCKER_USERNAME"
    print_success "Docker Hub username configured"
    
    print_warning "Docker Hub password needs to be set manually"
    echo "Please get your Docker Hub access token from: https://hub.docker.com/settings/security"
    echo "Then run: gh secret set DOCKER_PASSWORD --body 'YOUR_TOKEN'"
}

# Setup database secrets (auto-generated)
setup_database_secrets() {
    print_status "Setting up database secrets..."
    
    # Generate secure passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    
    gh secret set POSTGRES_PASSWORD --body "$POSTGRES_PASSWORD"
    gh secret set REDIS_PASSWORD --body "$REDIS_PASSWORD"
    
    print_success "Database secrets configured"
    print_warning "Generated passwords saved to GitHub secrets"
}

# Setup GitHub variables
setup_github_variables() {
    print_status "Setting up GitHub variables..."
    
    # Set repository variables
    gh variable set AMP_ENV --body "production"
    gh variable set DOCKER_IMAGE --body "keamouyleng/genx-fx"
    gh variable set AWS_REGION --body "us-east-1"
    gh variable set EC2_INSTANCE_TYPE --body "t2.micro"
    
    print_success "GitHub variables configured"
}

# Show current secrets
show_current_secrets() {
    print_status "Current GitHub secrets:"
    gh secret list
    echo ""
    
    print_status "Current GitHub variables:"
    gh variable list
    echo ""
}

# Create setup instructions
create_setup_instructions() {
    cat > MANUAL_SECRETS_SETUP.md << 'EOF'
# Manual Secrets Setup Instructions

## 🔐 Still Need to Configure

### Docker Hub Password
```bash
gh secret set DOCKER_PASSWORD --body "YOUR_DOCKER_HUB_ACCESS_TOKEN"
```
Get token from: https://hub.docker.com/settings/security

### AWS Credentials
```bash
gh secret set AWS_ACCESS_KEY_ID --body "YOUR_AWS_ACCESS_KEY_ID"
gh secret set AWS_SECRET_ACCESS_KEY --body "YOUR_AWS_SECRET_ACCESS_KEY"
```
Get from: https://console.aws.amazon.com → Security credentials

### Optional: Trading Platform (FXCM)
```bash
gh secret set FXCM_API_KEY --body "YOUR_FXCM_API_KEY"
gh secret set FXCM_SECRET_KEY --body "YOUR_FXCM_SECRET_KEY"
```
Get from: https://www.fxcm.com/markets/forex-trading-demo/

### Optional: AI APIs
```bash
gh secret set GEMINI_API_KEY --body "YOUR_GEMINI_API_KEY"
gh secret set OPENAI_API_KEY --body "YOUR_OPENAI_API_KEY"
```
Get from: 
- Gemini: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

## ✅ Already Configured
- AMP_TOKEN
- DOCKER_USERNAME
- POSTGRES_PASSWORD
- REDIS_PASSWORD
- AMP_ENV
- DOCKER_IMAGE
- AWS_REGION
- EC2_INSTANCE_TYPE

## 🚀 Quick Commands
```bash
# Check current secrets
gh secret list
gh variable list

# Test GitHub Actions
gh workflow list
gh workflow run docker-image.yml
```
EOF

    print_success "Setup instructions created: MANUAL_SECRETS_SETUP.md"
}

# Main function
main() {
    print_status "Starting automated GitHub secrets setup..."
    
    # Check GitHub CLI authentication
    if ! check_gh_auth; then
        print_error "Please authenticate with GitHub first"
        exit 1
    fi
    
    echo ""
    echo "🎯 Setting up secrets for repository: Mouy-leng/GenX_FX"
    echo ""
    
    # Setup all available secrets
    setup_amp_secret
    setup_genx_container_digests
    setup_docker_secrets
    setup_database_secrets
    setup_github_variables
    
    # Show current configuration
    show_current_secrets
    
    # Create setup instructions
    create_setup_instructions
    
    echo ""
    print_success "Automated GitHub secrets setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Configure Docker Hub password (see MANUAL_SECRETS_SETUP.md)"
    echo "2. Configure AWS credentials (see MANUAL_SECRETS_SETUP.md)"
    echo "3. Test GitHub Actions workflow"
    echo "4. Deploy to AWS using: ./aws/amp-deploy.sh"
    echo ""
}

# Run main function
main "$@"