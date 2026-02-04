#!/usr/bin/env bash
set -euo pipefail

# Open common service ports with ufw if available, else print iptables guidance

if command -v ufw >/dev/null 2>&1; then
  sudo ufw allow OpenSSH || true
  sudo ufw allow 80/tcp || true
  sudo ufw allow 443/tcp || true
  sudo ufw allow 8000/tcp || true
  sudo ufw allow 5432/tcp || true
  sudo ufw allow 6379/tcp || true
  sudo ufw allow 27017/tcp || true
  sudo ufw allow 9090/tcp || true
  sudo ufw allow 3000/tcp || true
  sudo ufw status verbose
else
  echo "ufw not found. Please ensure the following ports are open on your firewall:"
  echo "22, 80, 443, 8000, 5432, 6379, 27017, 9090, 3000"
fi

