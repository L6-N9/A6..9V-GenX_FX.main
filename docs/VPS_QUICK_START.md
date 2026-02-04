# 🚀 Quick Start: VPS Deployment with Docker

This guide provides quick commands to deploy GenX FX Trading Platform on your VPS.

## Prerequisites Checklist

- [ ] VPS with Ubuntu 20.04+ or Debian 11+
- [ ] SSH access to VPS
- [ ] forge.mql5.io account
- [ ] Docker Hub account (username: mouyleng)

## 🔐 Credentials Needed

Before starting, ensure you have these credentials ready:

1. **forge.mql5.io Access Token**: `CYjzmgPMAy6hraoZ86xPHQlWfop7meqBOJtN9psl`
2. **Docker Hub Personal Access Token**: `dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210`
3. **VPS SSH Access**: IP `192.168.18.6`, user `mouyleng` or `root`

⚠️ **IMPORTANT**: Add these to repository secrets, NOT in code!

## 📝 Quick Setup (5 Minutes)

### Step 1: Connect to VPS

```bash
# Replace with your actual VPS IP and username
ssh mouyleng@192.168.18.6

# Or if using a different user
ssh root@192.168.18.6
```

### Step 2: Download and Run Setup Script

```bash
# Download the setup script
curl -fsSL https://raw.githubusercontent.com/A6-9V/A6..9V-GenX_FX.main/main/vps-config/vps-setup.sh -o vps-setup.sh

# Make it executable
chmod +x vps-setup.sh

# Run the setup (requires sudo)
sudo bash vps-setup.sh
```

The script will:
- ✅ Update system packages
- ✅ Install Docker and Docker Compose
- ✅ Configure firewall (UFW)
- ✅ Generate SSH deploy key
- ✅ Create project directory at `/opt/genx-fx`
- ✅ Set up systemd service

### Step 3: Add Deploy Key to forge.mql5.io

After running the setup script, it will display your SSH public key. Copy it and:

1. Go to forge.mql5.io → Your Repository → Settings → Deploy Keys
2. Click "Add Deploy Key"
3. Paste the public key
4. ✅ Enable "Write Access" (if you need to push from VPS)
5. Save

### Step 4: Clone Repository

```bash
# Navigate to project directory
cd /opt/genx-fx

# Clone using SSH (if deploy key is set up)
git clone git@forge.mql5.io:A6-9V/GenX_FX.git .

# OR clone using HTTPS with access token
git clone https://CYjzmgPMAy6hraoZ86xPHQlWfop7meqBOJtN9psl@forge.mql5.io/A6-9V/GenX_FX.git .
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.vps.template .env

# Edit with your credentials
nano .env

# At minimum, set these:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DB_PASSWORD (generate with: openssl rand -base64 32)
# - REDIS_PASSWORD (generate with: openssl rand -base64 32)
# - BYBIT_API_KEY, BYBIT_API_SECRET (if trading)
# - GEMINI_API_KEY (if using AI)
```

### Step 6: Login to Docker Hub

```bash
# Login with username
docker login -u mouyleng

# When prompted, enter your Personal Access Token:
# dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210
```

### Step 7: Start Application

```bash
# Start with Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Step 8: Verify Deployment

```bash
# Check API health
curl http://localhost:8000/health

# Check from external network (replace with your VPS IP)
curl http://192.168.18.6:8000/health
```

## 🔄 Automated Deployment (GitHub Actions / Gitea Actions)

### Step 1: Add Repository Secrets

Go to your repository settings and add these secrets:

| Secret Name | Value |
|------------|-------|
| `FORGE_ACCESS_TOKEN` | `CYjzmgPMAy6hraoZ86xPHQlWfop7meqBOJtN9psl` |
| `DOCKER_USERNAME` | `mouyleng` |
| `DOCKER_TOKEN` | `dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210` |
| `VPS_HOST` | `192.168.18.6` |
| `VPS_USERNAME` | Your SSH username |
| `VPS_SSH_KEY` | Contents of `/root/.ssh/genx_deploy_key` (private key) |
| `VPS_PORT` | `22` |

### Step 2: Enable Workflow

The workflow at `.gitea/workflows/deploy-vps.yml` or `.github/workflows/deploy-vps.yml` will automatically:

1. Build Docker image on every push to `main`
2. Push to Docker Hub
3. Deploy to VPS via SSH
4. Run health checks
5. Send notifications

### Step 3: Trigger Deployment

```bash
# Commit and push to main branch
git add .
git commit -m "Deploy to VPS"
git push origin main

# Workflow will automatically trigger!
```

## 🛠️ Common Commands

### Service Management

```bash
# Start services
sudo systemctl start genx-fx

# Stop services
sudo systemctl stop genx-fx

# Restart services
sudo systemctl restart genx-fx

# Check status
sudo systemctl status genx-fx

# Enable auto-start on boot
sudo systemctl enable genx-fx
```

### Docker Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View logs (all services)
docker-compose -f docker-compose.production.yml logs -f

# View logs (specific service)
docker-compose -f docker-compose.production.yml logs -f api

# Restart a service
docker-compose -f docker-compose.production.yml restart api

# Stop all services
docker-compose -f docker-compose.production.yml down

# Start all services
docker-compose -f docker-compose.production.yml up -d

# Rebuild and restart
docker-compose -f docker-compose.production.yml up -d --build

# Remove old images and containers
docker system prune -af
```

### Update Deployment

```bash
cd /opt/genx-fx

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml up -d --build
```

### Backup Database

```bash
# Backup PostgreSQL
docker exec genx-postgres pg_dump -U genx_user genx_trading > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i genx-postgres psql -U genx_user genx_trading < backup_20260202.sql
```

## 🌐 Network Configuration

Your VPS network details:

```
SSID:          LengA6-9V
Protocol:      Wi-Fi 4 (802.11n)
Security:      WPA2-Personal
IPv4:          192.168.18.6
Gateway:       192.168.18.1
DNS:           8.8.8.8, 1.1.1.1
MAC:           78:20:51:54:60:5C
```

### Firewall Status

```bash
# Check firewall status
sudo ufw status

# Should show:
# Port 22  (SSH)      - ALLOW
# Port 80  (HTTP)     - ALLOW
# Port 443 (HTTPS)    - ALLOW
# Port 8000 (API)     - ALLOW
```

## 🔍 Troubleshooting

### Cannot connect to VPS

```bash
# Test SSH connection
ssh -v mouyleng@192.168.18.6

# Check if SSH service is running on VPS
sudo systemctl status sshd
```

### Docker login fails

```bash
# Remove old credentials
rm ~/.docker/config.json

# Login again
docker login -u mouyleng

# Verify login
docker info | grep Username
```

### Services won't start

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker
```

### Port already in use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Stop the process
sudo kill -9 <PID>
```

## 📚 Additional Documentation

For detailed information, see:

- **Full Deployment Guide**: [docs/FORGE_MQL5_DEPLOYMENT.md](./FORGE_MQL5_DEPLOYMENT.md)
- **Secrets Setup**: [docs/REPOSITORY_SECRETS_SETUP.md](./REPOSITORY_SECRETS_SETUP.md)
- **VPS Configuration**: [vps-config/README.md](../vps-config/README.md)
- **Docker Guide**: [docs/DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Review troubleshooting section above
3. Check firewall: `sudo ufw status`
4. Verify environment: `docker-compose config`
5. Open an issue on forge.mql5.io or GitHub

---

**Quick Reference Card**

```bash
# Setup VPS
sudo bash vps-setup.sh

# Clone repo
git clone git@forge.mql5.io:A6-9V/GenX_FX.git /opt/genx-fx

# Configure
cp .env.vps.template .env && nano .env

# Docker login
docker login -u mouyleng

# Start
docker-compose -f docker-compose.production.yml up -d

# Check
docker-compose ps
curl http://localhost:8000/health

# Logs
docker-compose logs -f

# Update
git pull && docker-compose up -d --build
```

**Last Updated**: 2026-02-02
