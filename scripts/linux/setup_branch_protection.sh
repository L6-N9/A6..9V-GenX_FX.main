#!/bin/bash

# Setup Branch Protection Rules
# This script provides commands to set up branch protection

echo "🔧 Setting up branch protection for GenX FX..."
echo "================================================"

# Check current branch
echo "📋 Current branch: $(git branch --show-current)"

# Check remote default branch
echo "🌐 Remote default branch:"
git remote show origin | grep "HEAD branch"

echo ""
echo "✅ Manual steps required:"
echo "================================================"
echo "1. Go to: https://github.com/Mouy-leng/GenX_FX/settings/branches"
echo "2. Change default branch to: feature/fxcm-integration-with-spreadsheet"
echo "3. Add branch protection rule"
echo "4. Configure all protection settings as shown in BRANCH_PROTECTION_SETUP.md"
echo ""
echo "📚 See BRANCH_PROTECTION_SETUP.md for detailed instructions"
echo ""
echo "🔗 Quick Links:"
echo "- Branch Settings: https://github.com/Mouy-leng/GenX_FX/settings/branches"
echo "- Security Settings: https://github.com/Mouy-leng/GenX_FX/settings/security"
echo "- Repository Settings: https://github.com/Mouy-leng/GenX_FX/settings"
echo ""
echo "🎯 Protection Features to Enable:"
echo "- Require pull request reviews (2 reviewers)"
echo "- Require status checks to pass"
echo "- Require signed commits"
echo "- Require linear history"
echo "- Include administrators"
echo "- Restrict pushes that create files larger than 100 MB"