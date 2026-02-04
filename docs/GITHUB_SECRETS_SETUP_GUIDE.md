# GitHub Secrets & Environment Setup Guide

## Overview

This guide will help you manually set up all GitHub secrets, environment variables, and CI/CD pipeline for the GenX FX trading system.

## Token Permissions Issue

The provided token doesn't have sufficient permissions for automated setup. You need to:

1. **Create a new token** with these permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:repo_hook` (Admin access to repository hooks)

2. **Or update the existing token** to include these scopes

## Manual Setup Steps

### 1. Repository Secrets

Go to: `https://github.com/Mouy-leng/GenX_FX/settings/secrets/actions`

Add these **Repository Secrets**:

#### Core Application Secrets
```
SECRET_KEY = your_secret_key_here
DB_PASSWORD = your_database_password
MONGO_PASSWORD = your_mongodb_password
REDIS_PASSWORD = your_redis_password
GRAFANA_PASSWORD = your_grafana_password
```

#### Trading API Keys
```
BYBIT_API_KEY = your_bybit_api_key
BYBIT_API_SECRET = your_bybit_api_secret
FXCM_API_TOKEN = your_fxcm_api_token
FXCM_API_KEY = your_fxcm_api_key
FXCM_SECRET_KEY = your_fxcm_secret_key
```

#### AI/ML API Keys
```
GEMINI_API_KEY = your_gemini_api_key
OPENAI_API_KEY = your_openai_api_key
```

#### Data & News APIs
```
ALPHA_VANTAGE_API_KEY = your_alpha_vantage_key
NEWS_API_KEY = your_news_api_key
```

#### Messaging & Notifications
```
DISCORD_TOKEN = your_discord_bot_token
TELEGRAM_TOKEN = your_telegram_bot_token
```

#### System Tokens
```
AMP_TOKEN = your_amp_token_here
```

#### Database Configuration
```
POSTGRES_PASSWORD = your_postgres_password
```

### 2. Repository Variables

Go to: `https://github.com/Mouy-leng/GenX_FX/settings/variables/actions`

Add these **Repository Variables**:

#### Application Configuration
```
NODE_ENV = production
LOG_LEVEL = INFO
PORT = 8000
API_PORT = 8000
GRAFANA_PORT = 3000
```

#### AI Configuration
```
GEMINI_MODEL = gemini-1.5-flash
GEMINI_MAX_TOKENS = 2048
GEMINI_RATE_LIMIT_RPM = 30
```

#### Service URLs
```
FXCM_URL = https://api-fxpractice.fxcm.com
```

#### Database Configuration
```
POSTGRES_DB = genx_trading
POSTGRES_USER = genx_user
POSTGRES_HOST = postgres
POSTGRES_PORT = 5432
REDIS_HOST = redis
REDIS_PORT = 6379
MONGODB_URL = mongodb://mongo:27017/genx_trading
```

### 3. Environment Setup

#### Create Environments

Go to: `https://github.com/Mouy-leng/GenX_FX/settings/environments`

Create these environments:
1. **development**
2. **staging** 
3. **production**

#### Environment-Specific Secrets

For each environment, add these secrets:

**Production Environment:**
```
DATABASE_URL = postgresql://genx_user:${DB_PASSWORD}@postgres:5432/genx_trading
REDIS_URL = redis://:${REDIS_PASSWORD}@redis:6379
```

**Staging Environment:**
```
DATABASE_URL = postgresql://genx_user:${DB_PASSWORD}@postgres-staging:5432/genx_trading_staging
REDIS_URL = redis://:${REDIS_PASSWORD}@redis-staging:6379
```

### 4. Automated Setup Script

If you get a token with proper permissions, run:

```bash
# Set the token as environment variable
set GITHUB_TOKEN=your_new_token_with_permissions

# Run the automated setup
python github-secrets-manager.py
```

## CI/CD Pipeline Features

The updated pipeline includes:

### Security & Quality
- **Trivy Security Scanning** - Vulnerability detection
- **Multi-Python Testing** - Python 3.11, 3.12, 3.13
- **Code Coverage** - Codecov integration
- **Comprehensive Linting** - Black, Flake8, isort, Bandit, Safety

### Build & Deploy
- **Docker Build** - Multi-stage builds with caching
- **Environment Deployments** - Staging and Production
- **Manual Deployment** - Workflow dispatch for manual deploys
- **Health Checks** - Post-deployment verification

### Workflows Created
1. **ci-cd.yml** - Main CI/CD pipeline
2. **manual-deploy.yml** - Manual deployment workflow

## Testing the Setup

### 1. Test Repository Access
```bash
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/repos/Mouy-leng/GenX_FX
```

### 2. Test Secrets Access
```bash
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/repos/Mouy-leng/GenX_FX/actions/secrets
```

### 3. Trigger Workflow
- Push to `main` or `develop` branch
- Or use "Actions" tab to manually trigger workflows

## Security Best Practices

### Token Security
- **Never commit tokens** to repository
- **Use environment variables** for local development
- **Rotate tokens regularly** (every 90 days)
- **Use fine-grained tokens** when possible

### Secret Management
- **Use different keys** for staging/production
- **Implement secret rotation** for critical APIs
- **Monitor secret usage** in Actions logs
- **Use environment protection rules** for production

### Access Control
- **Limit repository access** to necessary team members
- **Use branch protection rules** for main/develop
- **Require reviews** for production deployments
- **Enable audit logging** for security events

## Troubleshooting

### Common Issues

1. **403 Forbidden Errors**
   - Check token permissions
   - Verify repository access
   - Ensure token hasn't expired

2. **Environment Not Found**
   - Create environments manually first
   - Check environment names match exactly
   - Verify environment protection rules

3. **Secret Encryption Errors**
   - Ensure PyNaCl is installed: `pip install pynacl`
   - Check public key retrieval
   - Verify secret value format

4. **Workflow Failures**
   - Check required secrets are set
   - Verify environment variables
   - Review workflow logs in Actions tab

### Getting Help

1. **GitHub Documentation**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
2. **Repository Issues**: Create an issue in the GenX_FX repository
3. **Actions Logs**: Check the Actions tab for detailed error messages

## Next Steps

1. **Set up all secrets** using the lists above
2. **Test the CI/CD pipeline** by pushing code
3. **Configure deployment targets** (AWS, GCP, etc.)
4. **Set up monitoring** and alerting
5. **Document your deployment process**

---

**Security Note**: This guide contains placeholder values. Replace all `your_*_here` values with actual credentials. Never share actual API keys or tokens.