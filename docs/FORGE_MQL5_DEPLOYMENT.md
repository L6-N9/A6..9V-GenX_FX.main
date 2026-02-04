# 🚀 forge.mql5.io Deployment Guide

This guide provides step-by-step instructions for setting up deployment keys, configuring Gitea runners, and deploying the GenX FX Trading Platform via forge.mql5.io.

## 📋 Prerequisites

Before you begin, ensure you have:
- Access to forge.mql5.io
- VPS with Docker installed
- SSH access to your VPS
- Network connection (WiFi/Ethernet configured)

## 🔐 Part 1: Setting Up Deploy Keys on forge.mql5.io

### Step 1: Generate SSH Deploy Key

On your VPS or local machine, generate a new SSH key pair:

```bash
# Generate a new SSH key for deployment
ssh-keygen -t ed25519 -C "genx-deploy@forge.mql5.io" -f ~/.ssh/forge_deploy_key

# Display the public key
cat ~/.ssh/forge_deploy_key.pub
```

### Step 2: Add Deploy Key to forge.mql5.io Repository

1. Log in to forge.mql5.io
2. Navigate to your repository
3. Go to **Settings** → **Deploy Keys**
4. Click **Add Deploy Key**
5. Fill in the form:
   - **Title**: `GenX VPS Deployment Key`
   - **Key**: Paste the contents of `forge_deploy_key.pub`
   - **Write Access**: ✅ Enable if you need to push from VPS
6. Click **Add Key**

### Step 3: Configure Access Token

If you need API access, create a personal access token:

1. Go to **Settings** → **Applications** → **Personal Access Tokens**
2. Click **Generate New Token**
3. Fill in the form:
   - **Name**: `GenX Deployment Token`
   - **Scopes**: Select `repo`, `write:packages`
4. Click **Generate Token**
5. **IMPORTANT**: Copy and save the token immediately (you won't see it again)

## 🐳 Part 2: Docker Hub Configuration

### Step 1: Create Docker Hub Personal Access Token

1. Log in to [Docker Hub](https://hub.docker.com/)
2. Go to **Account Settings** → **Security** → **New Access Token**
3. Fill in the form:
   - **Description**: `GenX VPS Deployment`
   - **Access permissions**: `Read, Write, Delete`
4. Click **Generate**
5. **IMPORTANT**: Copy and save the token immediately

### Step 2: Login to Docker Hub on VPS

SSH into your VPS and login:

```bash
# Login to Docker Hub
docker login -u mouyleng

# When prompted, enter your Personal Access Token (not your password)
# Token: dckr_pat_[YOUR_TOKEN_HERE]
```

To automate this (for CI/CD), you can use:

```bash
echo "YOUR_DOCKER_TOKEN" | docker login -u mouyleng --password-stdin
```

## 🔑 Part 3: Add Secrets to Repository

### Option A: GitHub Repository Secrets

If using GitHub:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of the following secrets:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `FORGE_ACCESS_TOKEN` | forge.mql5.io access token | `CYjzmgPMAy6hraoZ86xPHQlWfop7meqBOJtN9psl` |
| `DOCKER_USERNAME` | Docker Hub username | `mouyleng` |
| `DOCKER_TOKEN` | Docker Hub personal access token | `dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210` |
| `VPS_HOST` | VPS IP address | `192.168.18.6` |
| `VPS_SSH_KEY` | Private SSH key for VPS | Contents of `~/.ssh/forge_deploy_key` |
| `VPS_USERNAME` | SSH username for VPS | `root` or your username |
| `VPS_PORT` | SSH port | `22` |

### Option B: Gitea (forge.mql5.io) Repository Secrets

If using Gitea:

1. Go to your repository on forge.mql5.io
2. Navigate to **Settings** → **Secrets**
3. Add each secret listed above

## 🌐 Part 4: Network Configuration

### WiFi/Network Setup

Based on your network configuration:

**Network Details:**
- **SSID**: LengA6-9V
- **Protocol**: Wi-Fi 4 (802.11n)
- **Security**: WPA2-Personal
- **IPv4 Address**: 192.168.18.6
- **Gateway**: 192.168.18.1
- **DNS Servers**: 8.8.8.8, 1.1.1.1
- **MAC Address**: 78:20:51:54:60:5C

### Firewall Configuration

Ensure the following ports are open on your VPS:

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow API port
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

## 🚀 Part 5: VPS Deployment with Docker

### Step 1: Clone Repository on VPS

```bash
# SSH into your VPS
ssh -i ~/.ssh/forge_deploy_key [username]@192.168.18.6

# Clone the repository using deploy key
git clone git@forge.mql5.io:A6-9V/GenX_FX.git /opt/genx-fx
cd /opt/genx-fx
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment file with your credentials
nano .env
```

Required environment variables:
```bash
# Core settings
SECRET_KEY=your-secure-random-key-here
LOG_LEVEL=INFO
NODE_ENV=production
PORT=8000

# Database
DATABASE_URL=postgresql://genx_user:your_db_password@postgres:5432/genx_trading
REDIS_URL=redis://:your_redis_password@redis:6379

# API Keys (from forge.mql5.io repository)
BYBIT_API_KEY=${BYBIT_API_KEY}
BYBIT_API_SECRET=${BYBIT_API_SECRET}
GEMINI_API_KEY=${GEMINI_API_KEY}

# Messaging
DISCORD_TOKEN=${DISCORD_TOKEN}
TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
```

### Step 3: Build and Run with Docker

```bash
# Login to Docker Hub
docker login -u mouyleng

# Build and start services
docker-compose -f docker-compose.production.yml up -d --build

# Check running containers
docker ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Step 4: Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Check service status
docker-compose -f docker-compose.production.yml ps
```

## 🔄 Part 6: Automated Deployment Workflow

Create a deployment workflow file for Gitea Actions or GitHub Actions:

**File**: `.gitea/workflows/deploy.yml` or `.github/workflows/deploy-vps.yml`

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USERNAME }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: ${{ secrets.VPS_PORT }}
          script: |
            cd /opt/genx-fx
            git pull origin main
            echo "${{ secrets.DOCKER_TOKEN }}" | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
            docker-compose -f docker-compose.production.yml pull
            docker-compose -f docker-compose.production.yml up -d --build
            docker system prune -af
```

## 📝 Part 7: Maintenance Commands

### Update Deployment

```bash
# SSH into VPS
ssh [username]@192.168.18.6

# Navigate to project directory
cd /opt/genx-fx

# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker-compose -f docker-compose.production.yml up -d --build
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f api
```

### Stop Services

```bash
docker-compose -f docker-compose.production.yml down
```

### Backup Data

```bash
# Backup database
docker exec genx-postgres pg_dump -U genx_user genx_trading > backup_$(date +%Y%m%d).sql

# Backup volumes
docker run --rm -v genx-postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d).tar.gz /data
```

## 🔒 Security Best Practices

1. **Never commit secrets to repository**
   - Always use `.env` files (added to `.gitignore`)
   - Use repository secrets for CI/CD

2. **Rotate credentials regularly**
   - Update access tokens every 90 days
   - Generate new deploy keys after team changes

3. **Use SSH keys instead of passwords**
   - Disable password authentication on VPS
   - Use ed25519 keys for better security

4. **Keep software updated**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y

   # Update Docker images
   docker-compose pull
   ```

5. **Monitor access logs**
   ```bash
   # Check SSH login attempts
   sudo tail -f /var/log/auth.log

   # Check Docker logs
   docker-compose logs --tail=100
   ```

## 🆘 Troubleshooting

### Deploy Key Permission Denied

If you get "Permission denied (publickey)" error:

```bash
# Verify SSH key is added
ssh-add ~/.ssh/forge_deploy_key

# Test connection
ssh -T git@forge.mql5.io
```

### Docker Login Fails

If Docker login fails:

```bash
# Remove existing credentials
rm ~/.docker/config.json

# Login again with correct token
docker login -u mouyleng
```

### Container Won't Start

```bash
# Check logs
docker-compose logs [service-name]

# Check resource usage
docker stats

# Verify environment variables
docker-compose config
```

### Network Issues

```bash
# Check VPS network
ip addr show

# Test DNS
dig @8.8.8.8 google.com

# Check firewall rules
sudo ufw status
```

## 📞 Support

For issues or questions:
- Check documentation: `/docs` folder
- Review logs: `docker-compose logs`
- Open an issue on forge.mql5.io

---

**Last Updated**: 2026-02-02
**Version**: 1.0.0
