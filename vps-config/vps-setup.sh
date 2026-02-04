#!/bin/bash

# =============================================================================
# VPS Setup Script for GenX FX Trading Platform
# =============================================================================
# This script sets up a VPS for deploying the GenX FX Trading Platform
# with Docker and configures all necessary components.
#
# Usage: sudo bash vps-setup.sh
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
   exit 1
fi

log_info "Starting VPS setup for GenX FX Trading Platform..."

# =============================================================================
# System Update
# =============================================================================
log_info "Updating system packages..."
apt update && apt upgrade -y

# =============================================================================
# Install Required Packages
# =============================================================================
log_info "Installing required packages..."
apt install -y \
    curl \
    git \
    wget \
    vim \
    htop \
    net-tools \
    ufw \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common

# =============================================================================
# Install Docker
# =============================================================================
if command -v docker &> /dev/null; then
    log_info "Docker is already installed"
    docker --version
else
    log_info "Installing Docker..."

    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Start and enable Docker
    systemctl start docker
    systemctl enable docker

    log_info "Docker installed successfully"
    docker --version
fi

# =============================================================================
# Install Docker Compose (standalone)
# =============================================================================
if command -v docker-compose &> /dev/null; then
    log_info "Docker Compose is already installed"
    docker-compose --version
else
    log_info "Installing Docker Compose..."

    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    log_info "Docker Compose installed successfully"
    docker-compose --version
fi

# =============================================================================
# Configure Firewall
# =============================================================================
log_info "Configuring firewall..."

# Reset UFW to default
ufw --force reset

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (important!)
ufw allow 22/tcp comment 'SSH'

# Allow HTTP/HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Allow API port
ufw allow 8000/tcp comment 'GenX API'

# Enable firewall
ufw --force enable

log_info "Firewall configured successfully"
ufw status

# =============================================================================
# Create Project Directory
# =============================================================================
log_info "Creating project directory..."

PROJECT_DIR="/opt/genx-fx"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

log_info "Project directory created at $PROJECT_DIR"

# =============================================================================
# Setup SSH Deploy Key (if not exists)
# =============================================================================
SSH_DIR="/root/.ssh"
DEPLOY_KEY="$SSH_DIR/genx_deploy_key"

if [ ! -f "$DEPLOY_KEY" ]; then
    log_info "Generating SSH deploy key..."
    mkdir -p $SSH_DIR
    ssh-keygen -t ed25519 -C "genx-deploy@vps" -f $DEPLOY_KEY -N ""

    log_info "SSH Deploy key generated!"
    log_warn "Add this public key to forge.mql5.io:"
    echo "================================================"
    cat "${DEPLOY_KEY}.pub"
    echo "================================================"
else
    log_info "SSH deploy key already exists"
fi

# =============================================================================
# Configure Git
# =============================================================================
log_info "Configuring Git..."

# Set up SSH config for forge.mql5.io
cat > $SSH_DIR/config <<EOF
Host forge.mql5.io
    HostName forge.mql5.io
    User git
    IdentityFile $DEPLOY_KEY
    StrictHostKeyChecking no
EOF

chmod 600 $SSH_DIR/config

# =============================================================================
# Clone Repository (if not exists)
# =============================================================================
if [ ! -d "$PROJECT_DIR/.git" ]; then
    log_info "Repository not found. You need to clone it manually:"
    echo "git clone git@forge.mql5.io:YOUR_USERNAME/GenX_FX.git $PROJECT_DIR"
    log_warn "Or use HTTPS: git clone https://forge.mql5.io/YOUR_USERNAME/GenX_FX.git $PROJECT_DIR"
else
    log_info "Repository already exists, pulling latest changes..."
    git pull
fi

# =============================================================================
# Setup Environment File
# =============================================================================
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_warn "Creating .env file from template..."

    if [ -f "$PROJECT_DIR/.env.vps.template" ]; then
        cp $PROJECT_DIR/.env.vps.template $PROJECT_DIR/.env
        log_warn "Please edit $PROJECT_DIR/.env and add your credentials"
    elif [ -f "$PROJECT_DIR/.env.example" ]; then
        cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env
        log_warn "Please edit $PROJECT_DIR/.env and add your credentials"
    else
        log_error "No environment template found!"
    fi
else
    log_info ".env file already exists"
fi

# =============================================================================
# Docker Login
# =============================================================================
log_info "Configuring Docker Hub access..."
log_warn "To login to Docker Hub, run:"
echo "docker login -u mouyleng"
echo "(Enter your Docker Hub personal access token when prompted)"

# =============================================================================
# Create systemd service (optional)
# =============================================================================
log_info "Creating systemd service..."

cat > /etc/systemd/system/genx-fx.service <<EOF
[Unit]
Description=GenX FX Trading Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

log_info "Systemd service created"
log_warn "To enable and start the service:"
echo "  sudo systemctl enable genx-fx"
echo "  sudo systemctl start genx-fx"

# =============================================================================
# Setup log rotation
# =============================================================================
log_info "Configuring log rotation..."

cat > /etc/logrotate.d/genx-fx <<EOF
$PROJECT_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
EOF

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "================================================"
log_info "VPS Setup Complete!"
echo "================================================"
echo ""
log_info "Next steps:"
echo "  1. Add the SSH public key to forge.mql5.io deploy keys"
echo "  2. Clone the repository (if not done already)"
echo "  3. Edit $PROJECT_DIR/.env with your credentials"
echo "  4. Login to Docker Hub: docker login -u mouyleng"
echo "  5. Start the application:"
echo "     cd $PROJECT_DIR"
echo "     docker-compose -f docker-compose.production.yml up -d"
echo ""
log_info "Service management:"
echo "  - Start: sudo systemctl start genx-fx"
echo "  - Stop: sudo systemctl stop genx-fx"
echo "  - Status: sudo systemctl status genx-fx"
echo "  - Logs: docker-compose -f docker-compose.production.yml logs -f"
echo ""
log_info "System information:"
echo "  - Project directory: $PROJECT_DIR"
echo "  - SSH key: $DEPLOY_KEY"
echo "  - Firewall status: $(ufw status | head -1)"
echo ""
log_warn "Remember to configure repository secrets for automated deployment!"
echo "See docs/REPOSITORY_SECRETS_SETUP.md for details"
echo "================================================"
