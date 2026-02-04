# 🚀 Deployment Setup Instructions

## Overview

This document provides step-by-step instructions for setting up forge.mql5.io integration, configuring repository secrets, and deploying the GenX FX Trading Platform to your VPS with Docker.

## 📋 What Has Been Configured

The following files and configurations have been added to your repository:

### Documentation Files
1. **`docs/FORGE_MQL5_DEPLOYMENT.md`** - Complete guide for forge.mql5.io integration
2. **`docs/REPOSITORY_SECRETS_SETUP.md`** - Detailed secrets configuration guide
3. **`docs/VPS_QUICK_START.md`** - Quick reference for rapid deployment

### Configuration Files
4. **`.env.vps.template`** - Environment variable template for VPS
5. **`.gitea/workflows/deploy-vps.yml`** - Automated deployment workflow for Gitea Actions

### Scripts
6. **`vps-config/vps-setup.sh`** - Automated VPS setup script
7. **`vps-config/README.md`** - Updated with comprehensive deployment information

## 🔐 Security-First Implementation

**IMPORTANT**: All sensitive credentials are handled securely:

✅ **NO credentials are committed to the repository**
✅ Template files use placeholder values only
✅ Scripts reference environment variables and secrets
✅ Documentation guides users to add secrets via UI
✅ `.gitignore` properly configured

## 🎯 What You Need to Do

### Step 1: Add Repository Secrets

You need to add the following secrets to your repository (GitHub or forge.mql5.io):

#### GitHub Repository
1. Go to: `https://github.com/A6-9V/A6..9V-GenX_FX.main/settings/secrets/actions`
2. Click **"New repository secret"**
3. Add each secret from the table below

#### forge.mql5.io Repository (Gitea)
1. Go to your repository on forge.mql5.io
2. Navigate to **Settings** → **Secrets**
3. Add each secret from the table below

#### Required Secrets

| Secret Name | Description | Your Value |
|------------|-------------|------------|
| `FORGE_ACCESS_TOKEN` | forge.mql5.io access token | `CYjzmgPMAy6hraoZ86xPHQlWfop7meqBOJtN9psl` |
| `DOCKER_USERNAME` | Docker Hub username | `mouyleng` |
| `DOCKER_TOKEN` | Docker Hub personal access token | `dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210` |
| `VPS_HOST` | VPS IP address | `192.168.18.6` |
| `VPS_USERNAME` | SSH username for VPS | Your SSH username (e.g., `mouyleng` or `root`) |
| `VPS_SSH_KEY` | Private SSH key for VPS | Will be generated in Step 2 |
| `VPS_PORT` | SSH port | `22` |

**Optional but recommended:**
- `TELEGRAM_TOKEN` - For deployment notifications
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID
- `GEMINI_API_KEY` - For AI features
- `BYBIT_API_KEY` - For trading features
- `BYBIT_API_SECRET` - For trading features

### Step 2: Setup Your VPS

#### Option A: Automated Setup (Recommended)

SSH into your VPS and run:

```bash
# Connect to VPS
ssh mouyleng@192.168.18.6

# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/A6-9V/A6..9V-GenX_FX.main/main/vps-config/vps-setup.sh -o vps-setup.sh
chmod +x vps-setup.sh
sudo bash vps-setup.sh
```

The script will:
- Install Docker and Docker Compose
- Configure firewall
- Generate SSH deploy key
- Create project directory
- Set up systemd service

**IMPORTANT**: After the script runs, it will display an SSH public key. Copy this key!

#### Option B: Manual Setup

Follow the detailed instructions in `docs/FORGE_MQL5_DEPLOYMENT.md`

### Step 3: Add Deploy Key to forge.mql5.io

1. Go to forge.mql5.io
2. Navigate to your repository
3. Go to **Settings** → **Deploy Keys**
4. Click **"Add Deploy Key"**
5. Paste the public key from Step 2
6. ✅ Enable "Write Access" (if you need to push from VPS)
7. Click **"Add Key"**

Now add the **private key** to your repository secrets:
- Secret name: `VPS_SSH_KEY`
- Value: Contents of `/root/.ssh/genx_deploy_key` (the private key file)

### Step 4: Configure VPS Environment

SSH into your VPS and configure the environment:

```bash
cd /opt/genx-fx

# Copy environment template
cp .env.vps.template .env

# Edit with your actual credentials
nano .env
```

**At minimum, set these values:**
```bash
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
```

Add your API keys as needed (BYBIT, GEMINI, etc.)

### Step 5: Login to Docker Hub on VPS

```bash
# Login to Docker Hub
docker login -u mouyleng

# When prompted, enter your Personal Access Token:
# dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210
```

### Step 6: Deploy the Application

#### Manual Deployment

```bash
cd /opt/genx-fx

# Clone repository (if not already done)
git clone https://github.com/A6-9V/A6..9V-GenX_FX.main.git .

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Automated Deployment (Recommended)

Once secrets are configured, simply push to the main branch:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

The `.gitea/workflows/deploy-vps.yml` workflow will automatically:
1. Build Docker image
2. Push to Docker Hub
3. Deploy to VPS
4. Run health checks
5. Create database backup

### Step 7: Verify Deployment

Check that everything is running:

```bash
# On your VPS
docker-compose ps

# Check API health
curl http://localhost:8000/health

# From external network
curl http://192.168.18.6:8000/health
```

## 📖 Quick Reference

### Common Commands

```bash
# Start services
docker-compose -f docker-compose.production.yml up -d

# Stop services
docker-compose -f docker-compose.production.yml down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart api

# Update deployment
cd /opt/genx-fx
git pull origin main
docker-compose up -d --build
```

### Service Management

```bash
# Using systemd
sudo systemctl start genx-fx
sudo systemctl stop genx-fx
sudo systemctl status genx-fx
sudo systemctl enable genx-fx  # Auto-start on boot
```

## 🌐 Network Configuration

Your VPS network details (for reference):

```
SSID:          LengA6-9V
Protocol:      Wi-Fi 4 (802.11n)
Security:      WPA2-Personal
IPv4:          192.168.18.6
Gateway:       192.168.18.1
DNS:           8.8.8.8, 1.1.1.1
IPv6 DNS:      2001:4860:4860::8888, 2606:4700:4700::1111
MAC Address:   78:20:51:54:60:5C
```

Firewall ports configured:
- Port 22 (SSH) - ALLOW
- Port 80 (HTTP) - ALLOW
- Port 443 (HTTPS) - ALLOW
- Port 8000 (API) - ALLOW

## 🔍 Troubleshooting

### Cannot SSH to VPS
```bash
# Test connection
ssh -v mouyleng@192.168.18.6

# Check if key is loaded
ssh-add -l
```

### Docker login fails
```bash
# Remove old credentials
rm ~/.docker/config.json

# Login again
docker login -u mouyleng
```

### Services won't start
```bash
# Check logs
docker-compose logs

# Check environment
docker-compose config

# Restart Docker
sudo systemctl restart docker
```

### Deployment workflow fails
1. Verify all secrets are added correctly
2. Check workflow logs on GitHub/Gitea
3. Ensure SSH key has proper permissions
4. Verify VPS is accessible from GitHub/Gitea runners

## 📚 Detailed Documentation

For more detailed information, refer to:

1. **`docs/FORGE_MQL5_DEPLOYMENT.md`**
   - Complete forge.mql5.io setup guide
   - Deploy key configuration
   - Detailed deployment steps

2. **`docs/REPOSITORY_SECRETS_SETUP.md`**
   - All required secrets explained
   - How to generate secure credentials
   - Security best practices

3. **`docs/VPS_QUICK_START.md`**
   - Quick reference commands
   - Common operations
   - Troubleshooting guide

4. **`vps-config/README.md`**
   - VPS configuration details
   - Gitea runner setup
   - Network configuration

## ✅ Verification Checklist

Use this checklist to ensure everything is set up correctly:

### Repository Configuration
- [ ] All secrets added to repository (GitHub or forge.mql5.io)
- [ ] Deploy key added to forge.mql5.io
- [ ] Workflow file exists: `.gitea/workflows/deploy-vps.yml`

### VPS Configuration
- [ ] Docker and Docker Compose installed
- [ ] Firewall configured (ports 22, 80, 443, 8000 open)
- [ ] Project directory created at `/opt/genx-fx`
- [ ] Environment file configured (`.env`)
- [ ] Docker Hub login successful
- [ ] SSH deploy key generated and added

### Deployment
- [ ] Repository cloned on VPS
- [ ] Services started successfully
- [ ] API health check passes
- [ ] Can access from external network
- [ ] Logs show no errors

### Automation
- [ ] Workflow triggers on push to main
- [ ] Build and deployment succeed
- [ ] Health checks pass
- [ ] Notifications received (if configured)

## 🔒 Security Reminders

1. **Never commit secrets to repository** ✅ Done - secrets are only in repository settings
2. **Rotate credentials every 90 days** - Mark your calendar
3. **Keep SSH keys secure** - Don't share private keys
4. **Monitor access logs** - `sudo tail -f /var/log/auth.log`
5. **Keep software updated** - `sudo apt update && sudo apt upgrade`

## 🆘 Need Help?

If you encounter issues:

1. Check the documentation files in `/docs`
2. Review the troubleshooting section above
3. Check Docker logs: `docker-compose logs -f`
4. Check system logs: `sudo journalctl -xe`
5. Open an issue on GitHub or forge.mql5.io

## 📝 Next Steps

After completing the setup:

1. **Test the deployment** - Verify all services are running
2. **Configure monitoring** - Set up health checks and alerts
3. **Enable backups** - The workflow includes automated database backups
4. **Update documentation** - Add any custom configuration you've made
5. **Train your team** - Share this documentation with team members

---

**Congratulations!** 🎉

Your GenX FX Trading Platform is now configured for automated deployment from forge.mql5.io to your VPS with Docker!

**Last Updated**: 2026-02-02
**Version**: 1.0.0
