#!/bin/bash

# GenX_FX Deployment Script for Google VM
set -e

echo "🚀 Starting GenX_FX Deployment..."

# Update system and install dependencies
echo "📦 Installing dependencies..."
sudo apt update
sudo apt install -y docker.io docker-compose curl wget git nginx certbot python3-certbot-nginx

# Start and enable Docker
echo "🐳 Setting up Docker..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Create project directory
echo "📁 Setting up project directory..."
mkdir -p ~/GenX_FX
cd ~/GenX_FX

# Create .env file with your credentials
echo "🔧 Creating .env file..."
cat > .env << 'ENVEOF'
# === Docker Registry Credentials ===
DOCKER_USERNAME=
DOCKER_PASSWORD=
DOCKER_IMAGE=keamouyleng/genx_docker
DOCKER_TAG=latest

# === API Keys ===
GEMINI_API_KEY=
VANTAGE_ALPHAVANTAGE_API_KEY=
NEWS_API_KEY=
NEWSDATA_API_KEY=
FINNHUB_API_KEY=

# === Telegram Credentials ===
TELEGRAM_BOT_TOKEN=
TELEGRAM_USER_ID=

# === Gmail Credentials ===
GMAIL_USER=
GMAIL_PASSWORD=
GMAIL_APP_API_KEY=

# === Reddit Credentials ===
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=
REDDIT_USER_AGENT=GenX-Trading-Bot/1.0

# === FXCM Credentials ===
FXCM_USERNAME=
FXCM_PASSWORD=
FXCM_CONNECTION_TYPE=Demo
FXCM_URL=www.fxcorporate.com/Hosts.jsp

# === Security Keys ===
JWT_SECRET_KEY=

# === Feature Flags ===
ENABLE_NEWS_ANALYSIS=true
ENABLE_REDDIT_ANALYSIS=true
ENABLE_WEBSOCKET_FEED=true
API_PROVIDER=gemini
ENVEOF

# Clone the repository
echo "📥 Cloning GenX_FX repository..."
git clone https://github.com/Mouy-leng/GenX_FX.git .
git checkout cursor/check-docker-and-container-registration-status-5116

# Create Docker Compose file for production
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.production.yml << 'COMPOSEEOF'
version: '3.8'

services:
  genx-backend:
    build: .
    container_name: genx-backend
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "443:443"
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    volumes:
      - ./expert-advisors:/app/expert-advisors
      - ./scripts:/app/scripts
      - ./logs:/app/logs
    networks:
      - genx-network

  nginx:
    image: nginx:alpine
    container_name: genx-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - genx-backend
    networks:
      - genx-network

networks:
  genx-network:
    driver: bridge
COMPOSEEOF

# Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
cat > nginx.conf << 'NGINXEOF'
events {
    worker_connections 1024;
}

http {
    upstream genx_backend {
        server genx-backend:8080;
    }

    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location / {
            proxy_pass http://genx_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
NGINXEOF

# Create SSL directory and generate self-signed certificate
echo "🔒 Setting up SSL certificate..."
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=GenX/CN=genx.local"

# Build and start the application
echo "🚀 Building and starting GenX_FX..."
sudo docker-compose -f docker-compose.production.yml up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
sudo docker-compose -f docker-compose.production.yml ps

echo "✅ Deployment completed!"
echo "🌐 Your GenX_FX backend is now running on:"
echo "   - HTTP: http://104.198.193.129 (redirects to HTTPS)"
echo "   - HTTPS: https://104.198.193.129"
echo "   - Backend API: https://104.198.193.129:8080"
echo ""
echo "📁 EA Scripts are available in: ~/GenX_FX/expert-advisors/"
echo "📝 Logs are available in: ~/GenX_FX/logs/"