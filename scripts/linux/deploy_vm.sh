#!/bin/bash
# GenX FX VM Deployment Script
# Sets up 24/7 trading on Google Cloud VM

echo "🚀 Setting up GenX FX for 24/7 trading..."

# Activate virtual environment
source genx_env/bin/activate

# Update system packages
echo "📦 Updating system packages..."
sudo apt update -qq

# Install screen for background processes
sudo apt install -y screen curl

# Create directories
mkdir -p logs
mkdir -p backups

# Create systemd service file
echo "⚙️ Creating system service..."
sudo tee /etc/systemd/system/genx-trading.service > /dev/null <<EOF
[Unit]
Description=GenX FX Trading System
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PWD
Environment=PATH=$PWD/genx_env/bin:/usr/bin:/bin
ExecStart=$PWD/genx_env/bin/python $PWD/amp_cli.py run --daemon
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create web server service
sudo tee /etc/systemd/system/genx-web.service > /dev/null <<EOF
[Unit]
Description=GenX FX Web Server
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PWD
Environment=PATH=$PWD/genx_env/bin:/usr/bin:/bin
ExecStart=$PWD/genx_env/bin/python -m http.server 8080 --directory signal_output
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
echo "🔄 Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable genx-trading.service
sudo systemctl enable genx-web.service

# Create cron job for signal generation
echo "⏰ Setting up automatic signal generation..."
(crontab -l 2>/dev/null; echo "*/5 * * * * cd $PWD && $PWD/genx_env/bin/python demo_excel_generator.py >> logs/signals.log 2>&1") | crontab -

# Create backup script
cat > backup_genx.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/genx_backup_$DATE"
mkdir -p "$BACKUP_DIR"

# Backup important files
cp -r signal_output "$BACKUP_DIR/"
cp -r logs "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/" 2>/dev/null || true
cp amp_config.json "$BACKUP_DIR/" 2>/dev/null || true

# Create archive
tar -czf "backups/genx_backup_$DATE.tar.gz" -C backups "genx_backup_$DATE"
rm -rf "$BACKUP_DIR"

echo "Backup created: genx_backup_$DATE.tar.gz"

# Keep only last 7 backups
cd backups
ls -t genx_backup_*.tar.gz | tail -n +8 | xargs -r rm --
EOF

chmod +x backup_genx.sh

# Set up daily backup
(crontab -l 2>/dev/null; echo "0 2 * * * cd $PWD && ./backup_genx.sh >> logs/backup.log 2>&1") | crontab -

# Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 8080/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "=== GenX FX System Status ==="
echo "Date: $(date)"
echo

echo "🔄 Services:"
systemctl is-active genx-trading.service
systemctl is-active genx-web.service
echo

echo "💾 Disk Usage:"
df -h /
echo

echo "🧠 Memory Usage:"
free -h
echo

echo "⚡ CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"% used"}'
echo

echo "📊 Latest Signals:"
ls -la signal_output/ | tail -3
echo

echo "📈 AMP Status:"
source genx_env/bin/activate && python3 amp_cli.py status 2>/dev/null || echo "AMP not running"
EOF

chmod +x monitor.sh

# Start services
echo "🚀 Starting services..."
sudo systemctl start genx-trading.service
sudo systemctl start genx-web.service

# Generate initial signals
echo "📊 Generating initial signals..."
python3 demo_excel_generator.py

echo "✅ Deployment complete!"
echo
echo "📋 System Status:"
echo "  🌐 Web Server: http://34.71.143.222:8080"
echo "  📊 Signals: http://34.71.143.222:8080/MT4_Signals.csv"
echo "  📱 Monitor: ./monitor.sh"
echo "  💾 Backup: ./backup_genx.sh"
echo
echo "🔍 Check status:"
echo "  sudo systemctl status genx-trading.service"
echo "  sudo systemctl status genx-web.service"
echo "  ./monitor.sh"
echo
echo "📝 View logs:"
echo "  tail -f logs/signals.log"
echo "  journalctl -u genx-trading.service -f"
echo
echo "🎉 Your trading system is now running 24/7!"