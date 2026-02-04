#!/bin/bash

# Verify Branch Protection Setup
echo "🔍 Verifying branch protection setup..."
echo "========================================"

# Check if we're on the protected branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "feature/fxcm-integration-with-spreadsheet" ]; then
    echo "✅ Currently on protected branch: $CURRENT_BRANCH"
else
    echo "⚠️  Not on protected branch. Current: $CURRENT_BRANCH"
fi

# Check remote default
echo ""
echo "🌐 Remote default branch:"
git remote show origin | grep "HEAD branch"

# Check if branch exists
echo ""
echo "🔍 Checking branch existence:"
if git ls-remote --heads origin feature/fxcm-integration-with-spreadsheet | grep -q .; then
    echo "✅ Protected branch exists on remote"
else
    echo "❌ Protected branch not found on remote"
fi

# Check if workflows exist
echo ""
echo "🔧 Checking GitHub Actions workflows:"
if [ -f ".github/workflows/security-scan.yml" ]; then
    echo "✅ Security scan workflow exists"
else
    echo "❌ Security scan workflow missing"
fi

if [ -f ".github/workflows/code-quality.yml" ]; then
    echo "✅ Code quality workflow exists"
else
    echo "❌ Code quality workflow missing"
fi

if [ -f ".github/workflows/docker-image.yml" ]; then
    echo "✅ Docker build workflow exists"
else
    echo "❌ Docker build workflow missing"
fi

# Check if CODEOWNERS exists
echo ""
echo "👥 Checking CODEOWNERS:"
if [ -f ".github/CODEOWNERS" ]; then
    echo "✅ CODEOWNERS file exists"
else
    echo "❌ CODEOWNERS file missing"
fi

echo ""
echo "🔗 Check protection status at:"
echo "https://github.com/Mouy-leng/GenX_FX/settings/branches"
echo ""
echo "📊 Protection Checklist:"
echo "- [ ] Default branch changed to feature/fxcm-integration-with-spreadsheet"
echo "- [ ] Branch protection rule created"
echo "- [ ] Required PR reviews (2 reviewers)"
echo "- [ ] Required status checks enabled"
echo "- [ ] Required signed commits"
echo "- [ ] Required linear history"
echo "- [ ] Code owners configured"
echo "- [ ] Security workflows added"
echo "- [ ] Code quality workflows added"
echo "- [ ] Docker build workflows updated"