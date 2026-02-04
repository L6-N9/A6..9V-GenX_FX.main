#!/bin/bash

# Simple Container Setup Script for GenX-FX Trading Platform
# Works in container environments without systemd

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up GenX-FX Trading Platform (Simple Setup)${NC}"

# === GitHub Configuration ===
GITHUB_USERNAME="genxdbxfx1"
GITHUB_REPOSITORY="https://github.com/genxdbxfx1-ctrl/GenX_db_FX-.git"

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

# Start Docker daemon in background
echo -e "${YELLOW}Starting Docker daemon...${NC}"
dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2376 &
sleep 10

# Create environment file
echo -e "${YELLOW}Creating environment file...${NC}"
cat > .env << EOF
# === GitHub ===
GITHUB_USERNAME=$GITHUB_USERNAME
GITHUB_REPOSITORY=$GITHUB_REPOSITORY

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

# Create minimal Docker Compose configuration
echo -e "${YELLOW}Creating minimal Docker Compose configuration...${NC}"
cat > docker-compose.simple.yml << EOF
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

# Start containers
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose -f docker-compose.simple.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 30

# Check container status
echo -e "${YELLOW}Checking container status...${NC}"
docker-compose -f docker-compose.simple.yml ps

# Test database connection
echo -e "${YELLOW}Testing database connection...${NC}"
sleep 10
docker exec genxdb_fx_mysql mysql -u root -ppassword -e "SELECT 1;" || echo "Database connection test failed"

# Create deployment info file
cat > simple_deployment_info.txt << EOF
GenX-FX Trading Platform Simple Deployment
==========================================

Deployment Date: $(date)
GitHub Repository: $GITHUB_REPOSITORY

Services:
- MySQL Database: localhost:3306
- Redis Cache: localhost:6379
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
- View logs: docker-compose -f docker-compose.simple.yml logs
- Stop services: docker-compose -f docker-compose.simple.yml down
- Restart services: docker-compose -f docker-compose.simple.yml restart
- Access MySQL: docker exec -it genxdb_fx_mysql mysql -u root -ppassword genxdb_fx_db
- Access Redis: docker exec -it genxdb_fx_redis redis-cli

Next Steps:
1. Start the API server: python -m uvicorn api.main:app --host 0.0.0.0 --port 8080
2. Access monitoring: http://localhost:3001
3. Connect to database: localhost:3306
EOF

echo -e "${GREEN}✅ Simple container setup complete!${NC}"
echo -e "${GREEN}📝 Deployment information saved to simple_deployment_info.txt${NC}"
echo -e "${BLUE}📊 Monitoring dashboard at: http://localhost:3001${NC}"
echo -e "${BLUE}🗄️  Database ready at localhost:3306${NC}"
echo -e "${YELLOW}🚀 Next: Start the API server with: python -m uvicorn api.main:app --host 0.0.0.0 --port 8080${NC}"