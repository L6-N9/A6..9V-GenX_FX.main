#!/bin/bash
# Gitea Act Runner Setup Script for Linux
# This script automates the installation and registration of act_runner for forge.mql5.io

set -e

# Configuration
RUNNER_VERSION="0.2.10"
GITEA_INSTANCE="https://forge.mql5.io"
RUNNER_NAME="genx-vps-runner"
LABELS="ubuntu-latest:docker://node:20-bullseye,ubuntu-22.04:docker://node:20-bullseye,ubuntu-20.04:docker://node:20-bullseye"

# Use REGISTRATION_TOKEN from environment or prompt
if [ -z "$REGISTRATION_TOKEN" ]; then
    read -p "🔑 Enter your Gitea runner registration token: " REGISTRATION_TOKEN
fi

if [ -z "$REGISTRATION_TOKEN" ]; then
    echo "❌ Error: Registration token is required."
    exit 1
fi

echo "🚀 Starting Gitea Act Runner setup..."

# 1. Prerequisite check: Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️ Warning: Docker not found. It is required for most runner tasks."
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 2. Download act_runner
echo "📥 Downloading act_runner v${RUNNER_VERSION}..."
ARCH=$(uname -m)
case $ARCH in
    x86_64) BINARY="act_runner-${RUNNER_VERSION}-linux-amd64" ;;
    aarch64) BINARY="act_runner-${RUNNER_VERSION}-linux-arm64" ;;
    *) echo "❌ Unsupported architecture: $ARCH"; exit 1 ;;
esac

if [ ! -f act_runner ]; then
    curl -L "https://gitea.com/gitea/act_runner/releases/download/v${RUNNER_VERSION}/${BINARY}" -o act_runner
    chmod +x act_runner
fi

# 3. Use existing config if available, else generate
if [ ! -f config.yaml ] && [ -f runner_config.yaml ]; then
    echo "⚙️ Using provided runner_config.yaml..."
    cp runner_config.yaml config.yaml
elif [ ! -f config.yaml ]; then
    echo "⚙️ Generating default configuration..."
    ./act_runner generate-config > config.yaml
fi

# 4. Register the runner
echo "📝 Registering runner with ${GITEA_INSTANCE}..."
if [ -f .runner ]; then
    echo "⚠️ Runner already registered. Re-registering..."
fi

if ! ./act_runner register \
    --instance "${GITEA_INSTANCE}" \
    --token "${REGISTRATION_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --labels "${LABELS}" \
    --no-interactive; then
    echo "❌ Error: Registration failed."
    exit 1
fi

# 5. Create systemd service (Optional)
if [ -f /etc/systemd/system/act_runner.service ]; then
    echo "⚠️ Systemd service already exists. Updating..."
    sudo systemctl stop act_runner || true
fi

echo "🔧 Creating systemd service..."
cat <<EOF | sudo tee /etc/systemd/system/act_runner.service
[Unit]
Description=Gitea Act Runner
After=network.target docker.service

[Service]
ExecStart=$(pwd)/act_runner daemon --config $(pwd)/config.yaml
WorkingDirectory=$(pwd)
Restart=always
RestartSec=5
User=$(whoami)

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Setup complete!"
echo "To start the runner, run:"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable act_runner"
echo "  sudo systemctl start act_runner"
echo ""
echo "To check status:"
echo "  sudo systemctl status act_runner"
