#!/bin/bash

# Container Setup Script for GenX-FX Trading Platform
# Using provided credentials for GitHub, Docker Hub, and other services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up GenX-FX Trading Platform Container${NC}"

# === GitHub Configuration ===
GITHUB_USERNAME="genxdbxfx1"
GITHUB_REPOSITORY="https://github.com/genxdbxfx1-ctrl/GenX_db_FX-.git"

# === Docker Hub Configuration ===
DOCKER_USERNAME="genxdbx"
DOCKER_CONTAINER="genxdbx/genxdbxfx1"
DOCKER_EMAIL="genxdbxfx1@gmail.com"
# Do not hardcode credentials in git; provide via environment variable.
DOCKER_PASSWORD="${DOCKER_PASSWORD:-}"

# === App Credentials ===
MT5_LOGIN="279023502"
MT5_SERVER="Exness-MT5Trial8"
# Do not hardcode credentials in git; provide via environment variable.
MT5_PASSWORD="${MT5_PASSWORD:-}"

# === API Keys (placeholders) ===
GEMINI_API_KEY="your_gemini_api_key_here"
ALPHAVANTAGE_API_KEY="your_alpha_api_key_here"
NEWS_API_KEY="your_newsapi_key_here"
NEWSDATA_API_KEY="your_newsdata_key_here"

# === Backend Config ===
ENV="development"
PORT="8080"
DEBUG="true"
DATABASE_URL="mysql://root:password@localhost:3306/genxdb_fx_db"

# === Security ===
SECRET_KEY=$(openssl rand -hex 32)

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and install Docker
if ! command_exists docker; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Check and install Docker Compose
if ! command_exists docker-compose; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Login to Docker Hub
echo -e "${YELLOW}Logging into Docker Hub...${NC}"
# Try different login methods
if ! echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin; then
    echo -e "${YELLOW}Trying alternative Docker login method...${NC}"
    docker login -u "$DOCKER_USERNAME" -p "$DOCKER_PASSWORD"
fi

# Create environment file
echo -e "${YELLOW}Creating environment file...${NC}"
cat > .env << EOF
# === GitHub ===
GITHUB_USERNAME=$GITHUB_USERNAME
GITHUB_REPOSITORY=$GITHUB_REPOSITORY

# === Docker Hub ===
DOCKER_USERNAME=$DOCKER_USERNAME
DOCKER_CONTAINER=$DOCKER_CONTAINER
DOCKER_EMAIL=$DOCKER_EMAIL
DOCKER_PASSWORD=$DOCKER_PASSWORD

# === App Credentials ===
MT5_LOGIN=$MT5_LOGIN
MT5_SERVER=$MT5_SERVER
MT5_PASSWORD=$MT5_PASSWORD

# === API Keys ===
GEMINI_API_KEY=$GEMINI_API_KEY
ALPHAVANTAGE_API_KEY=$ALPHAVANTAGE_API_KEY
NEWS_API_KEY=$NEWS_API_KEY
NEWSDATA_API_KEY=$NEWSDATA_API_KEY

# === Backend Config ===
ENV=$ENV
PORT=$PORT
DEBUG=$DEBUG
DATABASE_URL=$DATABASE_URL

# === Security ===
SECRET_KEY=$SECRET_KEY

# === Heroku ===
HEROKU_TOKEN=HRKU-AAdx7OW4VQYFLAyNbE0_2jze4VpJbaTHK8sxEv1XDN3w_____ws77zaRyPXX
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

# Create Docker Compose configuration
echo -e "${YELLOW}Creating Docker Compose configuration...${NC}"
cat > docker-compose.container.yml << EOF
version: '3.8'

services:
  # Database Service
  mysql:
    image: mysql:8.0
    container_name: genxdb_fx_mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: genxdb_fx_db
      MYSQL_USER: genx_user
      MYSQL_PASSWORD: genx_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init:/docker-entrypoint-initdb.d
    networks:
      - genx_network

  # Redis for caching
  redis:
    image: redis:7-alpine
    container_name: genxdb_fx_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - genx_network

  # Backend API Service
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: genxdb_fx_api
    restart: unless-stopped
    environment:
      - DATABASE_URL=mysql://genx_user:genx_password@mysql:3306/genxdb_fx_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=$SECRET_KEY
      - MT5_LOGIN=$MT5_LOGIN
      - MT5_SERVER=$MT5_SERVER
      - MT5_PASSWORD=$MT5_PASSWORD
      - GEMINI_API_KEY=$GEMINI_API_KEY
      - ALPHAVANTAGE_API_KEY=$ALPHAVANTAGE_API_KEY
      - NEWS_API_KEY=$NEWS_API_KEY
      - NEWSDATA_API_KEY=$NEWSDATA_API_KEY
    ports:
      - "8080:8080"
    depends_on:
      - mysql
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - genx_network

  # Frontend Service
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: genxdb_fx_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      - api
    volumes:
      - ./client:/app/client
    networks:
      - genx_network

  # Trading Bot Service
  trading_bot:
    build:
      context: .
      dockerfile: Dockerfile.trading
    container_name: genxdb_fx_trading
    restart: unless-stopped
    environment:
      - DATABASE_URL=mysql://genx_user:genx_password@mysql:3306/genxdb_fx_db
      - REDIS_URL=redis://redis:6379
      - MT5_LOGIN=$MT5_LOGIN
      - MT5_SERVER=$MT5_SERVER
      - MT5_PASSWORD=$MT5_PASSWORD
    depends_on:
      - mysql
      - redis
      - api
    volumes:
      - ./expert-advisors:/app/expert-advisors
      - ./logs:/app/logs
    networks:
      - genx_network

  # Monitoring Service
  monitoring:
    image: grafana/grafana:latest
    container_name: genxdb_fx_monitoring
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - genx_network

volumes:
  mysql_data:
  redis_data:
  grafana_data:

networks:
  genx_network:
    driver: bridge
EOF

echo -e "${GREEN}✅ Docker Compose configuration created${NC}"

# Create Dockerfiles
echo -e "${YELLOW}Creating Dockerfiles...${NC}"

# API Dockerfile
cat > Dockerfile.api << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Frontend Dockerfile
cat > Dockerfile.frontend << EOF
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "start"]
EOF

# Trading Bot Dockerfile
cat > Dockerfile.trading << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs expert-advisors

# Run the trading bot
CMD ["python", "main.py"]
EOF

echo -e "${GREEN}✅ Dockerfiles created${NC}"

# Create database initialization script
echo -e "${YELLOW}Creating database initialization script...${NC}"
mkdir -p database/init

cat > database/init/01-init.sql << EOF
-- Initialize GenX-FX Trading Platform Database

CREATE DATABASE IF NOT EXISTS genxdb_fx_db;
USE genxdb_fx_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Trading accounts table
CREATE TABLE IF NOT EXISTS trading_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    account_name VARCHAR(100) NOT NULL,
    broker VARCHAR(50) NOT NULL,
    account_number VARCHAR(100),
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Trading pairs table
CREATE TABLE IF NOT EXISTS trading_pairs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    base_currency VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market data table
CREATE TABLE IF NOT EXISTS market_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(15,5),
    high_price DECIMAL(15,5),
    low_price DECIMAL(15,5),
    close_price DECIMAL(15,5),
    volume DECIMAL(20,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp)
);

-- Trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,2),
    price DECIMAL(15,5),
    timestamp TIMESTAMP NOT NULL,
    model_version VARCHAR(50),
    features JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp)
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    account_id INT,
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    quantity DECIMAL(15,5) NOT NULL,
    price DECIMAL(15,5) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    signal_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (account_id) REFERENCES trading_accounts(id),
    FOREIGN KEY (signal_id) REFERENCES trading_signals(id)
);

-- Insert initial data
INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@genxdbxfx1.com', 'hashed_password_placeholder')
ON DUPLICATE KEY UPDATE username=username;

INSERT INTO trading_pairs (symbol, base_currency, quote_currency) VALUES
('EUR/USD', 'EUR', 'USD'),
('GBP/USD', 'GBP', 'USD'),
('USD/JPY', 'USD', 'JPY'),
('USD/CHF', 'USD', 'CHF'),
('AUD/USD', 'AUD', 'USD'),
('USD/CAD', 'USD', 'CAD'),
('NZD/USD', 'NZD', 'USD'),
('EUR/GBP', 'EUR', 'GBP'),
('EUR/JPY', 'EUR', 'JPY'),
('GBP/JPY', 'GBP', 'JPY')
ON DUPLICATE KEY UPDATE symbol=symbol;
EOF

echo -e "${GREEN}✅ Database initialization script created${NC}"

# Build and start containers
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose -f docker-compose.container.yml build

echo -e "${YELLOW}Starting containers...${NC}"
docker-compose -f docker-compose.container.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 30

# Check container status
echo -e "${YELLOW}Checking container status...${NC}"
docker-compose -f docker-compose.container.yml ps

# Create deployment info file
cat > container_deployment_info.txt << EOF
GenX-FX Trading Platform Container Deployment
============================================

Deployment Date: $(date)
GitHub Repository: $GITHUB_REPOSITORY
Docker Hub Container: $DOCKER_CONTAINER

Services:
- MySQL Database: localhost:3306
- Redis Cache: localhost:6379
- API Backend: localhost:8080
- Frontend: localhost:3000
- Trading Bot: Running in container
- Monitoring (Grafana): localhost:3001

Credentials:
- MySQL Root Password: password
- MySQL Database: genxdb_fx_db
- MySQL User: genx_user
- MySQL Password: genx_password
- Grafana Admin Password: admin

MT5 Credentials:
- Login: $MT5_LOGIN
- Server: $MT5_SERVER
- Password: $MT5_PASSWORD

Useful Commands:
- View logs: docker-compose -f docker-compose.container.yml logs
- Stop services: docker-compose -f docker-compose.container.yml down
- Restart services: docker-compose -f docker-compose.container.yml restart
- Update containers: docker-compose -f docker-compose.container.yml pull && docker-compose -f docker-compose.container.yml up -d

API Endpoints:
- Health Check: http://localhost:8080/health
- API Documentation: http://localhost:8080/docs
- Frontend: http://localhost:3000
- Monitoring: http://localhost:3001
EOF

echo -e "${GREEN}✅ Container setup complete!${NC}"
echo -e "${GREEN}📝 Deployment information saved to container_deployment_info.txt${NC}"
echo -e "${BLUE}🌐 Access your application at: http://localhost:3000${NC}"
echo -e "${BLUE}📊 Monitoring dashboard at: http://localhost:3001${NC}"
echo -e "${BLUE}📚 API documentation at: http://localhost:8080/docs${NC}"