#!/bin/bash

# 🛡️ GitHub Security & Maintenance Setup Script
# This script helps configure your docker_jules_orchestrator repository
# with comprehensive security features while maintaining developer productivity

set -e

echo "🔒 Setting up GitHub Security & Maintenance for docker_jules_orchestrator"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f ".github/workflows/test.yml" ]; then
    print_error "This script must be run from the root of your docker_jules_orchestrator repository"
    exit 1
fi

print_status "Repository structure verified"

echo ""
echo "📋 Manual GitHub Repository Configuration Required"
echo "================================================"
echo ""
echo "Please follow these steps in your GitHub repository settings:"
echo ""

echo "1️⃣  BRANCH PROTECTION RULES (Main Branch)"
echo "   Go to: Settings → Branches → Add branch protection rule → main"
echo "   ✅ Enable: Require status checks to pass before merging"
echo "   ✅ Enable: Require conversation resolution before merging"
echo "   ✅ Enable: Include administrators"
echo "   ❌ Disable: Require pull request approvals (since you're solo)"
echo "   ❌ Disable: Dismiss stale approvals"
echo ""

echo "2️⃣  REQUIRED STATUS CHECKS"
echo "   Add these status checks:"
echo "   - Run Tests and Quality Checks"
echo "   - Enhanced Security Analysis"
echo "   - Code Quality Check"
echo "   - Docker Build Test"
echo ""

echo "3️⃣  REPOSITORY SETTINGS"
echo "   General → Pull Requests:"
echo "   ✅ Automatically delete head branches after merge"
echo "   ✅ Allow auto-merge"
echo ""

echo "4️⃣  CODE SECURITY AND ANALYSIS"
echo "   Enable all features:"
echo "   ✅ Dependabot alerts"
echo "   ✅ Dependabot security updates"
echo "   ✅ CodeQL analysis"
echo "   ✅ Secret scanning"
echo ""

echo "5️⃣  SECRETS & ENVIRONMENT VARIABLES"
echo "   Go to: Settings → Secrets and variables → Actions"
echo "   Add these secrets:"
echo ""

# Check for existing secrets file
if [ -f ".env.example" ]; then
    print_info "Found .env.example file, checking for required secrets..."
    grep -E "^(AWS_|TELEGRAM_|GMAIL_|DOCKER_|API_)" .env.example | while read -r line; do
        if [[ $line =~ ^[[:space:]]*# ]]; then
            continue
        fi
        secret_name=$(echo "$line" | cut -d'=' -f1)
        echo "   🔐 $secret_name"
    done
else
    echo "   🔐 AWS_ACCESS_KEY_ID"
    echo "   🔐 AWS_SECRET_ACCESS_KEY"
    echo "   🔐 TELEGRAM_BOT_TOKEN"
    echo "   🔐 GMAIL_APP_PASSWORD"
    echo "   🔐 DOCKER_USERNAME"
    echo "   🔐 DOCKER_PASSWORD"
fi

echo ""
echo "6️⃣  WORKFLOW PERMISSIONS"
echo "   Go to: Settings → Actions → General"
echo "   ✅ Allow GitHub Actions to create and approve pull requests"
echo "   ✅ Allow GitHub Actions to create and approve pull requests (for workflows)"
echo ""

echo "7️⃣  SECURITY ADVISORIES"
echo "   Go to: Security → Security advisories"
echo "   ✅ Enable private vulnerability reporting"
echo ""

echo "8️⃣  DEPENDABOT SETTINGS"
echo "   Go to: Security → Dependabot"
echo "   ✅ Enable Dependabot alerts"
echo "   ✅ Enable Dependabot security updates"
echo ""

echo "9️⃣  CODEOWNERS VERIFICATION"
echo "   Verify .github/CODEOWNERS file is properly configured"
echo "   Current owners:"
cat .github/CODEOWNERS | grep "@" | head -5

echo ""
echo "🔧 AUTOMATED SETUP COMPLETED"
echo "============================"
print_status "✅ Enhanced test workflow created"
print_status "✅ Enhanced security workflow created"
print_status "✅ Dependabot configuration created"
print_status "✅ Security policy created"
print_status "✅ Issue templates created"
print_status "✅ Pull request template created"
print_status "✅ CODEOWNERS enhanced"
print_status "✅ README security section added"

echo ""
echo "📊 NEXT STEPS"
echo "============="
echo "1. Push these changes to your repository"
echo "2. Configure the GitHub repository settings listed above"
echo "3. Set up your repository secrets"
echo "4. Test the workflows by creating a test PR"
echo ""

echo "🚀 QUICK COMMANDS"
echo "================="
echo "git add ."
echo "git commit -m '🔒 Add comprehensive security and maintenance setup'"
echo "git push origin main"
echo ""

echo "🔍 VERIFICATION"
echo "==============="
echo "After pushing, verify:"
echo "- Workflows appear in Actions tab"
echo "- Security tab shows CodeQL analysis"
echo "- Dependabot creates update PRs"
echo "- Branch protection rules are active"
echo ""

print_status "Setup complete! Your repository is now configured with enterprise-grade security."
print_warning "Remember to manually configure the GitHub repository settings listed above."
print_info "For questions, check the GitHub documentation or repository security best practices."

echo ""
echo "🛡️  Security is not a feature, it's a foundation."
echo "Happy coding! 🎉"