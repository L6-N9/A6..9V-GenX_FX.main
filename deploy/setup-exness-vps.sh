#!/bin/bash

# Exness VPS Setup Script
# Automates setup on Debian-based systems (Ubuntu/Debian)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_warning "This script usually requires root privileges. We will use sudo."
    SUDO="sudo"
else
    SUDO=""
fi

# Update System
update_system() {
    print_status "Updating system packages..."
    $SUDO apt-get update && $SUDO apt-get upgrade -y
    $SUDO apt-get install -y curl git build-essential software-properties-common ufw
    print_success "System updated."
}

# Install Python 3.12
install_python() {
    print_status "Checking Python version..."
    if command -v python3.12 &> /dev/null; then
        print_success "Python 3.12 is already installed."
    else
        print_status "Installing Python 3.12..."
        # Check if Ubuntu
        if grep -q "Ubuntu" /etc/os-release; then
            $SUDO add-apt-repository -y ppa:deadsnakes/ppa
            $SUDO apt-get update
            $SUDO apt-get install -y python3.12 python3.12-venv python3.12-dev
        else
            # Debian or other - might need source build or different repo
            print_warning "Not Ubuntu. Attempting to install from default repos or might require manual install."
            $SUDO apt-get install -y python3.12 || print_error "Could not install Python 3.12 via apt. You might need to build from source."
        fi

        # Ensure python3 points to python3.12 if desired, or just verify installation
        if command -v python3.12 &> /dev/null; then
             print_success "Python 3.12 installed successfully."
        else
             print_error "Python 3.12 installation failed."
             exit 1
        fi
    fi
}

# Install Node.js 20
install_node() {
    print_status "Checking Node.js version..."
    if command -v node &> /dev/null; then
         # Check version
         NODE_VERSION=$(node --version)
         if [[ "$NODE_VERSION" == *"v20"* ]] || [[ "$NODE_VERSION" > "v20" ]]; then
             print_success "Node.js $NODE_VERSION is already installed."
             return
         fi
    fi

    print_status "Installing Node.js 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | $SUDO -E bash -
    $SUDO apt-get install -y nodejs
    print_success "Node.js installed: $(node --version)"
}

# Install pnpm
install_pnpm() {
    print_status "Installing pnpm..."
    if command -v pnpm &> /dev/null; then
        print_success "pnpm is already installed."
    else
        $SUDO npm install -g pnpm
        print_success "pnpm installed: $(pnpm --version)"
    fi
}

# Configure UFW
configure_firewall() {
    print_status "Configuring UFW Firewall..."
    $SUDO ufw allow ssh
    $SUDO ufw allow http
    $SUDO ufw allow https
    $SUDO ufw allow 8000/tcp # Backend
    $SUDO ufw allow 5000/tcp # Node Service
    $SUDO ufw allow 5173/tcp # Vite Frontend

    # Enable UFW
    # $SUDO ufw --force enable # Commented out to avoid locking out, user should enable manually or confirm
    print_warning "Firewall rules added. Run 'sudo ufw enable' to enforce."
}

# Main
main() {
    print_status "Starting Exness VPS Setup..."
    update_system
    install_python
    install_node
    install_pnpm
    configure_firewall
    print_success "Exness VPS Setup Completed!"
}

main
