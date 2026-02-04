#!/bin/bash

# GenX FX Trading Platform - Exness MT5 Demo Deployment Script
# Quick deployment for demo account: 279023502

set -euo pipefail

# --- Configuration ---
APP_USER="genx"
APP_DIR="/opt/genx-trading"
REPO_URL="https://github.com/Mouy-leng/GenX-EA_Script.git"

# --- Helper Functions ---

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Error handling
handle_error() {
    log_error "An error occurred on line $1"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Check system requirements
check_system() {
    log_step "Checking system requirements..."
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        log_error "Cannot determine OS"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]] || [[ "$VERSION_ID" != "22.04" ]]; then
        log_warn "This script is tested on Ubuntu 22.04. Current OS: $PRETTY_NAME"
    fi
    
    # Check available memory
    local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $mem_gb -lt 4 ]]; then
        log_error "At least 4GB RAM required. Available: ${mem_gb}GB"
        exit 1
    fi
    
    # Check available disk space
    local disk_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $disk_gb -lt 20 ]]; then
        log_error "At least 20GB free disk space required. Available: ${disk_gb}GB"
        exit 1
    fi
    
    log_info "System requirements check passed"
}

# Generate secure passwords
generate_passwords() {
    log_step "Generating secure passwords..."
    
    DB_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    SECRET_KEY=$(openssl rand -base64 32)
    
    log_info "Passwords generated successfully"
}

# Get VPS IP
get_vps_ip() {
    log_step "Detecting VPS IP..."
    
    VPS_IP=$(curl -s --max-time 10 ifconfig.me || echo "127.0.0.1")
    log_info "VPS IP detected: $VPS_IP"
}

# Update system packages
update_system() {
    log_step "Updating system packages..."
    
    apt-get update
    apt-get upgrade -y
    
    log_info "System packages updated"
}

# Install essential packages
install_packages() {
    log_step "Installing essential packages..."
    
    apt-get install -y \
        git curl wget vim nano htop tree jq ufw fail2ban \
        python3 python3-pip python3-venv \
        postgresql postgresql-contrib \
        redis-server nginx certbot python3-certbot-nginx \
        build-essential libssl-dev libffi-dev python3-dev
    
    log_info "Essential packages installed"
}

    
    log_info "PostgreSQL configured"
}

# Setup Redis
setup_redis() {
    log_step "Setting up Redis..."
    
    systemctl start redis-server
    systemctl enable redis-server
    sed -i 's/# requirepass foobared/requirepass '$REDIS_PASSWORD'/' /etc/redis/redis.conf
    systemctl restart redis-server
    
    log_info "Redis configured"
}

# Create application directory
setup_app_directory() {
    log_step "Setting up application directory..."
    
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    log_info "Application directory created: $APP_DIR"
}

# Clone repository
clone_repository() {
    log_step "Cloning repository..."
    
    git clone $REPO_URL .
    chmod +x deploy/setup-vps.sh
    
    log_info "Repository cloned successfully"
}

# Setup configuration
setup_configuration() {
    log_step "Setting up configuration..."
    
    cp deploy/exness-demo-config.env .env
    
    # Update .env with generated passwords and VPS IP
    sed -i "s/YOUR_SECURE_DB_PASSWORD_HERE/$DB_PASSWORD/g" .env
    sed -i "s/YOUR_REDIS_PASSWORD_HERE/$REDIS_PASSWORD/g" .env
    sed -i "s/YOUR_SECRET_KEY_HERE/$SECRET_KEY/g" .env
    sed -i "s/YOUR_VPS_IP_HERE/$VPS_IP/g" .env
    
    log_info "Configuration updated"
}

# Create directories
create_directories() {
    log_step "Creating necessary directories..."
    
    mkdir -p $APP_DIR/logs
    mkdir -p $APP_DIR/models
    mkdir -p $APP_DIR/backups
    mkdir -p $APP_DIR/credentials
    mkdir -p $APP_DIR/signal_output
    mkdir -p $APP_DIR/data
    
    # Set proper permissions
    chown -R $USER:$USER $APP_DIR
    chmod 600 $APP_DIR/.env
    
    log_info "Directories created with proper permissions"
}

# Setup Python environment
setup_python() {
    log_step "Setting up Python environment..."
    
    python3 -m venv genx_env
    source genx_env/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install additional packages for Exness integration
    pip install requests websocket-client pandas numpy scikit-learn xgboost tensorflow
    
    log_info "Python environment configured"
}

# Create systemd services
create_services() {
    log_step "Creating systemd services..."
    
    # GenX Trading Service
    cat > /etc/systemd/system/genx-trading.service << EOF
[Unit]
Description=GenX FX Trading Platform (Demo)
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/genx_env/bin
ExecStart=$APP_DIR/genx_env/bin/python main.py live
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Monitoring Service
    cat > /etc/systemd/system/genx-monitor.service << EOF
[Unit]
Description=GenX FX Monitoring Service (Demo)
After=genx-trading.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/genx_env/bin
ExecStart=$APP_DIR/genx_env/bin/python scripts/monitor.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    log_info "Systemd services created"
}

# Setup Nginx
setup_nginx() {
    log_step "Setting up Nginx..."
    
    cat > /etc/nginx/sites-available/genx-trading << EOF
server {
    listen 80;
    server_name $VPS_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /demo-status {
        proxy_pass http://127.0.0.1:8000/demo-status;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

    # Enable Nginx site
    ln -sf /etc/nginx/sites-available/genx-trading /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    systemctl restart nginx
    
    log_info "Nginx configured"
}

# Create scripts
create_scripts() {
    log_step "Creating utility scripts..."
    
    # Health check script
    cat > $APP_DIR/scripts/health-check.sh << 'EOF'
#!/bin/bash

# Health check for GenX Trading Platform (Demo)
LOG_FILE="/opt/genx-trading/logs/health-check.log"

echo "$(date): Starting health check for Exness MT5 Demo" >> $LOG_FILE

# Check if services are running
check_service() {
    local service_name=$1
    if systemctl is-active --quiet $service_name; then
        echo "$(date): $service_name is running" >> $LOG_FILE
        return 0
    else
        echo "$(date): $service_name is not running" >> $LOG_FILE
        return 1
    fi
}

# Check database connection
check_database() {
    if pg_isready -h localhost -p 5432 -U genx_user > /dev/null 2>&1; then
        echo "$(date): Database connection OK" >> $LOG_FILE
        return 0
    else
        echo "$(date): Database connection failed" >> $LOG_FILE
        return 1
    fi
}

# Check Redis connection
check_redis() {
    if redis-cli ping > /dev/null 2>&1; then
        echo "$(date): Redis connection OK" >> $LOG_FILE
        return 0
    else
        echo "$(date): Redis connection failed" >> $LOG_FILE
        return 1
    fi
}

# Check API endpoint
check_api() {
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "$(date): API health check OK" >> $LOG_FILE
        return 0
    else
        echo "$(date): API health check failed" >> $LOG_FILE
        return 1
    fi
}

# Check EA connection
check_ea_connection() {
    if netstat -tlnp | grep :9090 > /dev/null 2>&1; then
        echo "$(date): EA server listening on port 9090" >> $LOG_FILE
        return 0
    else
        echo "$(date): EA server not listening" >> $LOG_FILE
        return 1
    fi
}

# Run all checks
check_service genx-trading
check_service postgresql
check_service redis-server
check_database
check_redis
check_api
check_ea_connection

echo "$(date): Health check completed" >> $LOG_FILE

# Keep only last 1000 lines
tail -n 1000 $LOG_FILE > $LOG_FILE.tmp && mv $LOG_FILE.tmp $LOG_FILE
EOF

    chmod +x $APP_DIR/scripts/health-check.sh
    
    log_info "Utility scripts created"
}

# Enable services
enable_services() {
    log_step "Enabling services..."
    
    systemctl daemon-reload
    systemctl enable genx-trading
    systemctl enable genx-monitor
    
    log_info "Services enabled"
}

# Setup database
setup_database() {
    log_step "Setting up database tables..."
    
    cd $APP_DIR
    source genx_env/bin/activate
    python scripts/setup_database.py
    
    log_info "Database tables created"
}

# Redeploy system
redeploy() {
    log_step "Redeploying GenX FX Platform..."

    if [ ! -d "$APP_DIR" ]; then
        log_error "Application directory $APP_DIR not found. Perform full install first."
        exit 1
    fi

    cd $APP_DIR

    log_info "Pulling latest changes from repository..."
    # Ensure we are in a git repo
    if [ -d ".git" ]; then
        git fetch --all
        git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)
    else
        log_warn "Not a git repository at $APP_DIR. Skipping git pull."
    fi

    log_info "Updating dependencies..."
    if [ -d "genx_env" ]; then
        source genx_env/bin/activate
        pip install -r requirements.txt
    else
        log_warn "Python environment not found. Skipping pip install."
    fi

    log_info "Restarting services..."
    systemctl daemon-reload
    systemctl restart genx-trading 2>/dev/null || log_warn "genx-trading service not found or failed to restart"
    systemctl restart genx-monitor 2>/dev/null || log_warn "genx-monitor service not found or failed to restart"

    log_info "Redeployment completed successfully"
}

# Display final information
display_final_info() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Exness MT5 Demo Deployment Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Demo Account Details:${NC}"
    echo -e "Login: 279023502"
    echo -e "Server: Exness-MT5Trial8"
    echo -e "Password: <set via MT5_PASSWORD env var>"
    echo -e "Symbol: XAUUSD"
    echo -e "Timeframe: M15"
    echo ""
    echo -e "${YELLOW}VPS Access Information:${NC}"
    echo -e "VPS IP: $VPS_IP"
    echo -e "API URL: http://$VPS_IP:8000"
    echo -e "Demo Status: http://$VPS_IP/demo-status"
    echo -e "Health Check: http://$VPS_IP/health"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Start the trading system:"
    echo "   sudo systemctl start genx-trading"
    echo ""
    echo "2. Check system status:"
    echo "   sudo systemctl status genx-trading"
    echo "   sudo journalctl -u genx-trading -f"
    echo ""
    echo "3. Monitor demo trading:"
    echo "   curl http://$VPS_IP/demo-status"
    echo ""
    echo "4. Check EA connection:"
    echo "   netstat -tlnp | grep 9090"
    echo ""
    echo -e "${BLUE}EA Configuration for MT5:${NC}"
    echo "Host: $VPS_IP"
    echo "Port: 9090"
    echo "Magic Number: 279023502"
    echo "Symbol: XAUUSD"
    echo "Timeframe: M15"
    echo ""
    echo -e "${GREEN}Demo deployment completed successfully!${NC}"
    echo -e "${YELLOW}Remember: This is a demo account for testing only.${NC}"
}

# --- Main Execution ---

main() {
    log_info "Starting GenX FX Exness MT5 Demo Deployment"
    
    check_root
    check_system
    generate_passwords
    get_vps_ip
    update_system
    install_packages
    install_docker
    install_docker_compose
    configure_firewall
    setup_postgresql
    setup_redis
    setup_app_directory
    clone_repository
    setup_configuration
    create_directories
    setup_python
    create_services
    setup_nginx
    create_scripts
    enable_services
    setup_database
    display_final_info
    
    log_info "Deployment completed successfully!"
}

# Run main function
if [[ "${1:-}" == "redeploy" ]]; then
    check_root
    redeploy
else
    main "$@"
fi