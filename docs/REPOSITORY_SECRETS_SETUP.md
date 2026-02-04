# 🔐 Repository Secrets Configuration Guide

This document lists all the secrets that need to be configured in your repository settings for automated deployment and CI/CD workflows.

## 🚨 SECURITY WARNING

**NEVER commit these values directly to your repository!**
- All secrets must be added via repository settings UI
- Use environment variables in code
- Add sensitive files to `.gitignore`
- Rotate credentials regularly (every 90 days)

## 📋 Required Secrets List

### 1. forge.mql5.io Integration

#### `FORGE_ACCESS_TOKEN`
- **Description**: Personal access token for forge.mql5.io API access
- **How to get**: forge.mql5.io → Settings → Applications → Generate Token
- **Permissions needed**: `repo`, `write:packages`
- **Example format**: `CYjzmgPMAy6hraoZ86xPHQlWfop7meqBOJtN9psl`

### 2. Docker Hub Credentials

#### `DOCKER_USERNAME`
- **Description**: Docker Hub username
- **Value**: `mouyleng`
- **Type**: Plain text

#### `DOCKER_TOKEN`
- **Description**: Docker Hub personal access token (NOT password)
- **How to get**: Docker Hub → Account Settings → Security → New Access Token
- **Permissions needed**: Read, Write, Delete
- **Example format**: `dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210`

### 3. VPS Deployment Configuration

#### `VPS_HOST`
- **Description**: IP address or hostname of your VPS
- **Example**: `192.168.18.6`
- **Type**: Plain text

#### `VPS_USERNAME`
- **Description**: SSH username for VPS access
- **Example**: `root` or `ubuntu`
- **Type**: Plain text

#### `VPS_SSH_KEY`
- **Description**: Private SSH key for VPS authentication
- **How to get**: Generate with `ssh-keygen -t ed25519 -C "deployment@vps"`
- **Format**: Complete private key including headers
- **Example**:
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
...
-----END OPENSSH PRIVATE KEY-----
```

#### `VPS_PORT`
- **Description**: SSH port for VPS (default is 22)
- **Value**: `22`
- **Type**: Plain text

### 4. Database Credentials

#### `DB_PASSWORD`
- **Description**: PostgreSQL database password
- **How to generate**: Use strong random password
- **Example**: `openssl rand -base64 32`
- **Type**: Plain text (alphanumeric + special chars)

#### `REDIS_PASSWORD`
- **Description**: Redis cache password
- **How to generate**: Use strong random password
- **Example**: `openssl rand -base64 32`
- **Type**: Plain text (alphanumeric + special chars)

#### `DATABASE_URL`
- **Description**: Full PostgreSQL connection string
- **Format**: `postgresql://user:password@host:port/database`
- **Example**: `postgresql://genx_user:${DB_PASSWORD}@postgres:5432/genx_trading`

#### `MONGODB_PASSWORD`
- **Description**: MongoDB password (if using MongoDB)
- **How to generate**: Use strong random password
- **Type**: Plain text

### 5. Trading Platform API Keys

#### `BYBIT_API_KEY`
- **Description**: Bybit exchange API key
- **How to get**: Bybit → Account → API Management → Create New API
- **Permissions needed**: Trading, Account read
- **Type**: Plain text

#### `BYBIT_API_SECRET`
- **Description**: Bybit exchange API secret
- **How to get**: Provided when creating API key
- **Type**: Plain text (keep secure!)

#### `FXCM_API_KEY`
- **Description**: FXCM trading platform API key
- **How to get**: FXCM → Demo Account → API Credentials
- **Type**: Plain text

#### `FXCM_API_TOKEN`
- **Description**: FXCM API token
- **How to get**: FXCM API dashboard
- **Type**: Plain text

#### `FXCM_SECRET_KEY`
- **Description**: FXCM API secret
- **Type**: Plain text

### 6. AI/ML API Keys

#### `GEMINI_API_KEY`
- **Description**: Google Gemini AI API key
- **How to get**: https://makersuite.google.com/app/apikey
- **Type**: Plain text

#### `OPENAI_API_KEY`
- **Description**: OpenAI API key
- **How to get**: https://platform.openai.com/api-keys
- **Format**: Starts with `sk-`
- **Type**: Plain text

### 7. Messaging & Notifications

#### `DISCORD_TOKEN`
- **Description**: Discord bot token
- **How to get**: Discord Developer Portal → New Application → Bot
- **Type**: Plain text

#### `TELEGRAM_TOKEN`
- **Description**: Telegram bot token
- **How to get**: Talk to @BotFather on Telegram
- **Format**: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Type**: Plain text

#### `WHATSAPP_GROUP_URL`
- **Description**: WhatsApp group invite URL
- **Example**: `https://chat.whatsapp.com/DYemXrBnMD63K55bjUMKYF`
- **Type**: Plain text

### 8. Core Application

#### `SECRET_KEY`
- **Description**: Application secret key for encryption
- **How to generate**: `openssl rand -hex 32`
- **Type**: Plain text (64 hexadecimal characters)

#### `AMP_TOKEN`
- **Description**: AMP system authentication token
- **Type**: Plain text

### 9. Network Configuration (For Documentation Only)

**⚠️ Note: These should NOT be stored as secrets, just for your reference:**

- **SSID**: LengA6-9V
- **WiFi Protocol**: Wi-Fi 4 (802.11n)
- **Security**: WPA2-Personal
- **IPv4 Address**: 192.168.18.6
- **Gateway**: 192.168.18.1
- **DNS Servers**: 8.8.8.8, 1.1.1.1
- **IPv6 DNS**: 2001:4860:4860::8888, 2606:4700:4700::1111
- **MAC Address**: 78:20:51:54:60:5C

## 📝 How to Add Secrets

### GitHub

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the name and value
5. Click **Add secret**

### Gitea (forge.mql5.io)

1. Go to your repository on forge.mql5.io
2. Click **Settings** → **Secrets**
3. Click **Add Secret**
4. Enter the name and value
5. Click **Add**

### Command Line (GitHub CLI)

```bash
# Install GitHub CLI
# https://cli.github.com/

# Login
gh auth login

# Add a secret
gh secret set DOCKER_TOKEN --body "dckr_pat_your_token_here"

# Add multiple secrets from a file
gh secret set --env-file .env.secrets
```

## 🔄 Environment Variables vs Secrets

### Use Repository Secrets for:
- API keys and tokens
- Passwords
- SSH keys
- Any sensitive data that should never be in version control

### Use Environment Variables (in `.env` file) for:
- Application configuration
- Non-sensitive settings
- Local development settings

**Important**: Add `.env` to `.gitignore`!

## 🧪 Testing Secrets Configuration

Create a test workflow to verify secrets are correctly configured:

```yaml
name: Test Secrets
on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check Docker credentials
        run: |
          if [ -z "${{ secrets.DOCKER_USERNAME }}" ]; then
            echo "❌ DOCKER_USERNAME not set"
            exit 1
          fi
          if [ -z "${{ secrets.DOCKER_TOKEN }}" ]; then
            echo "❌ DOCKER_TOKEN not set"
            exit 1
          fi
          echo "✅ Docker credentials configured"

      - name: Check VPS configuration
        run: |
          if [ -z "${{ secrets.VPS_HOST }}" ]; then
            echo "❌ VPS_HOST not set"
            exit 1
          fi
          echo "✅ VPS configuration present"

      - name: Check API keys
        run: |
          if [ -z "${{ secrets.GEMINI_API_KEY }}" ]; then
            echo "⚠️ GEMINI_API_KEY not set (optional)"
          fi
          echo "✅ Secrets check complete"
```

## 🔐 Security Best Practices

### 1. Credential Rotation Schedule

| Secret Type | Rotation Frequency | Priority |
|------------|-------------------|----------|
| API Keys | Every 90 days | High |
| SSH Keys | Every 180 days | High |
| Database Passwords | Every 90 days | Critical |
| Bot Tokens | Every 180 days | Medium |

### 2. Access Control

- Limit who can view/edit repository secrets
- Use separate tokens for different environments (dev/staging/prod)
- Enable 2FA on all service accounts

### 3. Monitoring

```bash
# Check for exposed secrets in git history
git log -p | grep -i "api_key\|secret\|password\|token"

# Use tools like git-secrets or truffleHog
pip install truffleHog
truffleHog --regex --entropy=True .
```

### 4. Emergency Response

If a secret is compromised:

1. **Immediately revoke the compromised credential**
2. **Generate new credentials**
3. **Update repository secrets**
4. **Review access logs for unauthorized usage**
5. **Document the incident**

## ✅ Secrets Checklist

Use this checklist to ensure all secrets are properly configured:

```markdown
### Deployment Essentials
- [ ] FORGE_ACCESS_TOKEN
- [ ] DOCKER_USERNAME
- [ ] DOCKER_TOKEN
- [ ] VPS_HOST
- [ ] VPS_USERNAME
- [ ] VPS_SSH_KEY
- [ ] VPS_PORT

### Database
- [ ] DB_PASSWORD
- [ ] REDIS_PASSWORD
- [ ] DATABASE_URL

### Trading APIs (Optional)
- [ ] BYBIT_API_KEY
- [ ] BYBIT_API_SECRET
- [ ] FXCM_API_KEY
- [ ] FXCM_API_TOKEN

### AI/ML (Optional)
- [ ] GEMINI_API_KEY
- [ ] OPENAI_API_KEY

### Notifications (Optional)
- [ ] DISCORD_TOKEN
- [ ] TELEGRAM_TOKEN

### Core Application
- [ ] SECRET_KEY
- [ ] AMP_TOKEN
```

## 📚 Additional Resources

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Gitea Secrets Management](https://docs.gitea.io/en-us/actions-secrets/)
- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [SSH Key Management Best Practices](https://www.ssh.com/academy/ssh/key-management)

---

**Last Updated**: 2026-02-02
**Version**: 1.0.0
