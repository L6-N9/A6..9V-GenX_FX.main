# VPS Configuration & Deployment Setup

This directory contains configuration files and scripts for setting up the GenX FX Trading Platform on a VPS, including Docker deployment and Gitea Actions runner setup.

## 📁 Files in This Directory

- **`vps-setup.sh`** - Main VPS setup script (installs Docker, configures firewall, etc.)
- **`setup_runner.sh`** - Gitea Actions runner setup for Linux
- **`setup_runner.ps1`** - Gitea Actions runner setup for Windows
- **`runner_config.yaml`** - Gitea runner configuration file

## 🚀 Quick Start: VPS Deployment

### Complete VPS Setup (Recommended)

Run the main setup script to configure everything:

```bash
# Download the setup script
curl -fsSL https://raw.githubusercontent.com/A6-9V/A6..9V-GenX_FX.main/main/vps-config/vps-setup.sh -o vps-setup.sh

# Make it executable
chmod +x vps-setup.sh

# Run with sudo
sudo bash vps-setup.sh
```

This script will:
- ✅ Update system packages
- ✅ Install Docker and Docker Compose
- ✅ Configure UFW firewall (ports 22, 80, 443, 8000)
- ✅ Generate SSH deploy key for forge.mql5.io
- ✅ Create project directory at `/opt/genx-fx`
- ✅ Set up systemd service for auto-start
- ✅ Configure log rotation

### What You Need

**Before running the setup:**
- VPS with Ubuntu 20.04+ or Debian 11+
- Root or sudo access
- Network connectivity

**Credentials to have ready:**
- forge.mql5.io access token: `CYjzmgPMAy6hraoZ86xPHQlWfop7meqBOJtN9psl`
- Docker Hub username: `mouyleng`
- Docker Hub token: `dckr_pat_FMob4Pqlvj-kZ1UeeLTkHAmZ210`
- VPS IP: `192.168.18.6`

⚠️ **SECURITY**: Add these to repository secrets, NOT in code!

## 🔧 Gitea Runner Setup (for CI/CD)

The runner connects to **forge.mql5.io** to execute Actions (CI/CD workflows).

### 🔑 Registration Token

Before running the setup scripts, ensure you have your Gitea runner registration token. You can find it in your repository settings on `forge.mql5.io`.

### 🐧 Linux (Ubuntu/Debian)

1. Copy `setup_runner.sh` and `runner_config.yaml` to your VPS.
2. Make the script executable: `chmod +x setup_runner.sh`
3. Run the script: `./setup_runner.sh`
4. Enter your registration token when prompted.
5. Follow the instructions in the script output to enable the systemd service.

### 🪟 Windows

1. Copy `setup_runner.ps1` and `runner_config.yaml` to your VPS.
2. Open PowerShell as Administrator.
3. Run the script: `.\setup_runner.ps1`
4. Enter your registration token when prompted.
5. To start the runner: `.\act_runner.exe daemon --config config.yaml`

## 🌐 Network Configuration

Your VPS should have these network settings:

```
SSID:          LengA6-9V
Protocol:      Wi-Fi 4 (802.11n)
Security:      WPA2-Personal
IPv4:          192.168.18.6
Gateway:       192.168.18.1
DNS Servers:   8.8.8.8, 1.1.1.1
IPv6 DNS:      2001:4860:4860::8888, 2606:4700:4700::1111
MAC Address:   78:20:51:54:60:5C
```

### Firewall Ports

The setup script configures these ports:

| Port | Protocol | Service | Status |
|------|----------|---------|--------|
| 22   | TCP      | SSH     | ALLOW  |
| 80   | TCP      | HTTP    | ALLOW  |
| 443  | TCP      | HTTPS   | ALLOW  |
| 8000 | TCP      | GenX API| ALLOW  |

Check status: `sudo ufw status`

## 📝 Configuration Files

### runner_config.yaml

The base configuration for Gitea Actions runner. Customize labels, capacity, or other settings before running setup scripts.

### SSH Deploy Key

After running `vps-setup.sh`, you'll get an SSH public key to add to forge.mql5.io:

1. Copy the displayed public key
2. Go to forge.mql5.io → Repository → Settings → Deploy Keys
3. Add the key with "Write Access" enabled

## 📁 Dropbox Sync (Optional)

If you are using Dropbox for configuration sync (e.g., at `C:\Users\USER\Dropbox\vps-config`), you can keep these files there to have them available across all your machines.

## 🛠️ Maintenance

### Update Gitea Runner

Download a newer version from [official releases](https://gitea.com/gitea/act_runner/releases) and replace the existing binary.

### Update Docker

```bash
sudo apt update
sudo apt upgrade docker-ce docker-ce-cli containerd.io
```

### View Service Logs

```bash
# GenX service logs
sudo journalctl -u genx-fx -f

# Docker logs
docker-compose -f /opt/genx-fx/docker-compose.production.yml logs -f
```

## 📚 Additional Documentation

For more detailed information, see:

- **VPS Quick Start**: [../docs/VPS_QUICK_START.md](../docs/VPS_QUICK_START.md)
- **forge.mql5.io Deployment**: [../docs/FORGE_MQL5_DEPLOYMENT.md](../docs/FORGE_MQL5_DEPLOYMENT.md)
- **Repository Secrets**: [../docs/REPOSITORY_SECRETS_SETUP.md](../docs/REPOSITORY_SECRETS_SETUP.md)
- **Docker Deployment**: [../docs/DOCKER_DEPLOYMENT_GUIDE.md](../docs/DOCKER_DEPLOYMENT_GUIDE.md)

## 🆘 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review documentation in `/docs`
- Open an issue on forge.mql5.io or GitHub

---

**Last Updated**: 2026-02-02
