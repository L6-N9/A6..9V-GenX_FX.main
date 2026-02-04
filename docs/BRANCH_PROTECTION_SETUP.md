# 🛡️ Branch Protection Setup Guide

## 🎯 **Objective**
Set `feature/fxcm-integration-with-spreadsheet` as the main branch and configure comprehensive branch protection rules.

---

## 📋 **Step 1: Change Default Branch**

### **Manual Steps (Required)**
Since the GitHub PAT doesn't have sufficient permissions, you need to do this manually:

1. **Go to Repository Settings**:
   ```
   https://github.com/Mouy-leng/GenX_FX/settings/branches
   ```

2. **Change Default Branch**:
   - Click "Switch to another branch" button
   - Select `feature/fxcm-integration-with-spreadsheet`
   - Click "Update"
   - Confirm the change

3. **Verify the Change**:
   ```bash
   git remote show origin
   # Should show: HEAD branch: feature/fxcm-integration-with-spreadsheet
   ```

---

## 🛡️ **Step 2: Configure Branch Protection Rules**

### **2.1 Enable Branch Protection**
1. Go to: `https://github.com/Mouy-leng/GenX_FX/settings/branches`
2. Click "Add rule" or "Add branch protection rule"
3. In "Branch name pattern", enter: `feature/fxcm-integration-with-spreadsheet`

### **2.2 Configure Protection Settings**

#### **✅ Required Settings**
- [x] **Require a pull request before merging**
  - [x] Require approvals: **2 reviewers**
  - [x] Dismiss stale PR approvals when new commits are pushed
  - [x] Require review from code owners
  - [x] Require review from users who have write access

- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - [x] Status checks that are required:
    - `Docker Build`
    - `Security Scan`
    - `Code Quality Check`

- [x] **Require conversation resolution before merging**
- [x] **Require signed commits**
- [x] **Require linear history**
- [x] **Include administrators**

#### **✅ Optional but Recommended**
- [x] **Restrict pushes that create files larger than 100 MB**
- [x] **Require deployments to succeed before merging**
- [x] **Lock branch**

---

## 🔧 **Step 3: Create GitHub Actions for Status Checks**

### **3.1 Security Scan Workflow**
Create `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan

on:
  pull_request:
    branches: [ feature/fxcm-integration-with-spreadsheet ]
  push:
    branches: [ feature/fxcm-integration-with-spreadsheet ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Bandit Security Scan
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json || true
      
      - name: Run Safety Check
        run: |
          pip install safety
          safety check --json --output safety-report.json || true
      
      - name: Upload Security Reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
```

### **3.2 Code Quality Check**
Create `.github/workflows/code-quality.yml`:

```yaml
name: Code Quality Check

on:
  pull_request:
    branches: [ feature/fxcm-integration-with-spreadsheet ]
  push:
    branches: [ feature/fxcm-integration-with-spreadsheet ]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install flake8 black isort mypy
      
      - name: Run Flake8
        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Run Black Check
        run: black --check --diff .
      
      - name: Run isort Check
        run: isort --check-only --diff .
      
      - name: Run MyPy
        run: mypy . --ignore-missing-imports
```

### **3.3 Docker Build Check**
Update `.github/workflows/docker-image.yml`:

```yaml
name: Docker Build & Security Check

on:
  pull_request:
    branches: [ feature/fxcm-integration-with-spreadsheet ]
  push:
    branches: [ feature/fxcm-integration-with-spreadsheet ]

jobs:
  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.production
          push: false
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'keamouyleng/genx-fx:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## 👥 **Step 4: Set Up Code Owners**

Create `.github/CODEOWNERS`:

```markdown
# Global code owners
* @Mouy-leng

# Python files
*.py @Mouy-leng

# Configuration files
*.yml *.yaml *.json *.toml @Mouy-leng

# Documentation
*.md @Mouy-leng

# Docker files
Dockerfile* docker-compose* @Mouy-leng

# GitHub workflows
.github/workflows/ @Mouy-leng

# AWS and deployment
aws/ deploy/ @Mouy-leng

# Expert Advisors
expert-advisors/ @Mouy-leng

# Core modules
core/ @Mouy-leng
```

---

## 🔐 **Step 5: Configure Repository Settings**

### **5.1 General Settings**
Go to: `https://github.com/Mouy-leng/GenX_FX/settings`

**Repository Features**:
- [x] **Issues**: Enabled
- [x] **Pull requests**: Enabled
- [x] **Wikis**: Disabled (use README instead)
- [x] **Discussions**: Enabled
- [x] **Sponsorships**: Enabled
- [x] **Merge button**: Enabled
- [x] **Squash merging**: Enabled
- [x] **Rebase merging**: Enabled
- [x] **Auto-delete head branches**: Enabled

### **5.2 Security Settings**
Go to: `https://github.com/Mouy-leng/GenX_FX/settings/security`

**Security Features**:
- [x] **Dependency graph**: Enabled
- [x] **Dependabot alerts**: Enabled
- [x] **Dependabot security updates**: Enabled
- [x] **Code scanning**: Enabled
- [x] **Secret scanning**: Enabled

---

## 🚀 **Step 6: Automated Scripts**

### **6.1 Branch Protection Setup Script**
Create `setup_branch_protection.sh`:

```bash
#!/bin/bash

# Setup Branch Protection Rules
# This script provides commands to set up branch protection

echo "🔧 Setting up branch protection for GenX FX..."

# Check current branch
echo "📋 Current branch: $(git branch --show-current)"

# Check remote default branch
echo "🌐 Remote default branch:"
git remote show origin | grep "HEAD branch"

echo ""
echo "✅ Manual steps required:"
echo "1. Go to: https://github.com/Mouy-leng/GenX_FX/settings/branches"
echo "2. Change default branch to: feature/fxcm-integration-with-spreadsheet"
echo "3. Add branch protection rule"
echo "4. Configure all protection settings as shown above"
echo ""
echo "📚 See BRANCH_PROTECTION_SETUP.md for detailed instructions"
```

### **6.2 Verification Script**
Create `verify_branch_protection.sh`:

```bash
#!/bin/bash

# Verify Branch Protection Setup
echo "🔍 Verifying branch protection setup..."

# Check if we're on the protected branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "feature/fxcm-integration-with-spreadsheet" ]; then
    echo "✅ Currently on protected branch: $CURRENT_BRANCH"
else
    echo "⚠️  Not on protected branch. Current: $CURRENT_BRANCH"
fi

# Check remote default
echo "🌐 Remote default branch:"
git remote show origin | grep "HEAD branch"

# Check if branch exists
if git ls-remote --heads origin feature/fxcm-integration-with-spreadsheet | grep -q .; then
    echo "✅ Protected branch exists on remote"
else
    echo "❌ Protected branch not found on remote"
fi

echo ""
echo "🔗 Check protection status at:"
echo "https://github.com/Mouy-leng/GenX_FX/settings/branches"
```

---

## 📊 **Step 7: Protection Status Dashboard**

### **7.1 Protection Checklist**
- [ ] Default branch changed to `feature/fxcm-integration-with-spreadsheet`
- [ ] Branch protection rule created
- [ ] Required PR reviews (2 reviewers)
- [ ] Required status checks enabled
- [ ] Required signed commits
- [ ] Required linear history
- [ ] Code owners configured
- [ ] Security workflows added
- [ ] Code quality workflows added
- [ ] Docker build workflows updated

### **7.2 Monitoring**
- **Branch Status**: Check at `/settings/branches`
- **Security Alerts**: Monitor at `/security`
- **Dependabot**: Check at `/security/dependabot`
- **Code Scanning**: Monitor at `/security/code-scanning`

---

## 🎯 **Expected Results**

### **After Setup**
1. **Protected Branch**: `feature/fxcm-integration-with-spreadsheet` becomes main
2. **No Direct Pushes**: All changes must go through PRs
3. **Required Reviews**: 2 approvals needed for merging
4. **Automated Checks**: Security, quality, and build checks run automatically
5. **Signed Commits**: All commits must be signed
6. **Linear History**: Clean, linear commit history

### **Workflow**
1. Create feature branch from main
2. Make changes and commit
3. Create pull request
4. Automated checks run
5. Code review required
6. Merge only after all checks pass

---

## 🚨 **Important Notes**

1. **Admin Override**: Administrators can still bypass protection (use sparingly)
2. **Emergency Fixes**: Use admin override only for critical security fixes
3. **Documentation**: Keep all changes documented
4. **Testing**: Test all workflows before enforcing protection

---

**Status**: ⏳ **Ready for Manual Setup**  
**Next Action**: Follow the manual steps above to configure branch protection