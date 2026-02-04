#!/bin/bash

# AMP System User Data Script
# This script runs when the EC2 instance starts up

set -e

# Update system
yum update -y

# Install required packages
yum install -y python3 python3-pip git docker

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Create application directory
mkdir -p /opt/amp-system
cd /opt/amp-system

# Create environment file
cat > .env << 'ENVEOF'
# AMP System Environment Configuration
AMP_TOKEN=

# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET=${project_name}-data
DYNAMODB_TABLE=${project_name}-data

# System Configuration
AMP_ENV=${environment}
LOG_LEVEL=INFO
DEBUG=false

# Port Configuration
API_PORT=8000
GRAFANA_PORT=3000
ENVEOF

# Create docker-compose file
cat > docker-compose.yml << 'COMPOSEEOF'
version: '3.8'

services:
  amp-system:
    image: keamouyleng/genx-fx:latest
    container_name: amp-trading-system
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./reports:/app/reports
      - ./.env:/app/.env:ro
    environment:
      - PYTHONPATH=/app
      - AMP_ENV=production
      - AWS_REGION=us-east-1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: amp-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    container_name: amp-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: amp_trading
      POSTGRES_USER: amp_user
      POSTGRES_PASSWORD: amp_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  grafana:
    image: grafana/grafana:latest
    container_name: amp-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=amp_admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  redis_data:
  postgres_data:
  grafana_data:
COMPOSEEOF

# Create necessary directories
mkdir -p logs data reports

# Pull and start containers
docker-compose up -d

# Wait for containers to start
sleep 30

# Authenticate AMP system
set -a
source /opt/amp-system/.env
set +a
if [ -n "${AMP_TOKEN:-}" ]; then
  docker exec -it amp-trading-system amp auth --token "$AMP_TOKEN" || true
fi

# Start scheduler
docker exec -it amp-trading-system amp schedule --start || true

# Create startup script
cat > /opt/amp-system/start_amp.sh << 'STARTEOF'
#!/bin/bash
cd /opt/amp-system
docker-compose up -d
sleep 10
docker exec -it amp-trading-system amp schedule --start || true
echo "AMP system started successfully!"
STARTEOF

chmod +x /opt/amp-system/start_amp.sh

# Create systemd service
cat > /etc/systemd/system/amp-system.service << 'SERVICEEOF'
[Unit]
Description=AMP Trading System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/amp-system
ExecStart=/opt/amp-system/start_amp.sh
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Enable and start service
systemctl enable amp-system.service
systemctl start amp-system.service

# Create health check script
cat > /opt/amp-system/health_check.sh << 'HEALTHEOF'
#!/bin/bash
# Health check script for the AMP system

# Check if Docker is running
if ! systemctl is-active --quiet docker; then
    echo "Docker is not running"
    exit 1
fi

# Check if AMP container is running
if ! docker ps | grep -q amp-trading-system; then
    echo "AMP container is not running"
    exit 1
fi

# Check if API is responding
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "AMP API is not responding"
    exit 1
fi

echo "AMP system is healthy"
exit 0
HEALTHEOF

chmod +x /opt/amp-system/health_check.sh

# Create monitoring script
cat > /opt/amp-system/monitor.sh << 'MONITOREOF'
#!/bin/bash
# Monitoring script for the AMP system

echo "=== AMP System Status ==="
echo "Timestamp: $(date)"
echo ""

# System resources
echo "System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
echo ""

# Docker containers
echo "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# AMP system status
echo "AMP System Status:"
if docker exec amp-trading-system amp status > /dev/null 2>&1; then
    docker exec amp-trading-system amp status
else
    echo "AMP CLI not responding"
fi
echo ""

# Logs (last 10 lines)
echo "Recent Logs:"
docker logs --tail 10 amp-trading-system
MONITOREOF

chmod +x /opt/amp-system/monitor.sh

# Create crontab for monitoring
cat > /tmp/amp_cron << 'CRONEOF'
# Monitor AMP system every 5 minutes
*/5 * * * * /opt/amp-system/health_check.sh >> /var/log/amp-health.log 2>&1

# Daily system monitoring report
0 9 * * * /opt/amp-system/monitor.sh >> /var/log/amp-monitor.log 2>&1
CRONEOF

crontab /tmp/amp_cron

echo "AMP system deployment completed!"
echo "System will be available at:"
echo "- AMP API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/health"
echo "- Grafana: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "- Grafana Credentials: admin / amp_admin"