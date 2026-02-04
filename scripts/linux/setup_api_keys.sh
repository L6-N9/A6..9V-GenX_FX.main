#!/bin/bash

# GenX_FX Trading Platform - API Key Setup Script
# This script helps you set up your API keys quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if .env file exists
if [ -f .env ]; then
    print_warning ".env file already exists. Do you want to overwrite it? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled. Your existing .env file is preserved."
        exit 0
    fi
fi

print_header "GenX_FX Trading Platform - API Key Setup"

print_status "This script will help you set up your API keys for the GenX_FX trading platform."
echo ""

# Create .env file
print_status "Creating .env file..."

cat > .env << 'EOF'
# ========================================
# GenX_FX Trading Platform - Environment Configuration
# ========================================

# ========================================
# DATABASE CONFIGURATION
# ========================================
DATABASE_URL=postgresql://user:password@localhost:5432/genx_trading
MONGODB_URL=mongodb://localhost:27017/genx_trading
REDIS_URL=redis://localhost:6379

# ========================================
# SECURITY & AUTHENTICATION
# ========================================
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here
CRYPTION_KEY=your-encryption-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========================================
# AI & MACHINE LEARNING
# ========================================
# Google Gemini AI (Primary AI for market analysis)
GEMINI_API_KEY=your-gemini-api-key-here

# OpenAI (Optional fallback)
OPENAI_API_KEY=your-openai-api-key-here

# AI Model Paths
MODEL_PATH=ai_models/market_predictor.joblib
ENSEMBLE_MODEL_PATH=ai_models/ensemble_model.joblib

# ========================================
# TRADING BROKERS & EXCHANGES
# ========================================
# Bybit Exchange
BYBIT_API_KEY=your-bybit-api-key-here
BYBIT_API_SECRET=your-bybit-api-secret-here

# FXCM (Forex Trading)
FXCM_API_KEY=your-fxcm-api-key-here
FXCM_ACCESS_TOKEN=your-fxcm-access-token-here
FXCM_ACCOUNT_ID=your-fxcm-account-id-here
FXCM_ENVIRONMENT=demo  # or "real"

# ========================================
# NEWS & MARKET DATA APIs
# ========================================
# Multi-source news aggregation
NEWSDATA_API_KEY=your-newsdata-api-key-here
ALPHAVANTAGE_API_KEY=your-alphavantage-api-key-here
NEWSAPI_ORG_KEY=your-newsapi-org-key-here
FINNHUB_API_KEY=your-finnhub-api-key-here
FMP_API_KEY=your-fmp-api-key-here

# ========================================
# SOCIAL MEDIA APIs
# ========================================
# Reddit API for sentiment analysis
REDDIT_CLIENT_ID=your-reddit-client-id-here
REDDIT_CLIENT_SECRET=your-reddit-client-secret-here
REDDIT_USERNAME=your-reddit-username-here
REDDIT_PASSWORD=your-reddit-password-here
REDDIT_USER_AGENT=GenX-Trading-Bot/1.0

# ========================================
# NOTIFICATION SERVICES
# ========================================
# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_USER_ID=your-telegram-user-id-here

# Discord Bot
DISCORD_TOKEN=your-discord-bot-token-here

# Email Notifications
GMAIL_USER=your-gmail-address@gmail.com
GMAIL_PASSWORD=your-gmail-app-password-here
GMAIL_APP_API_KEY=your-gmail-api-key-here

# ========================================
# TRADING CONFIGURATION
# ========================================
DEFAULT_SYMBOL=BTCUSDT
MAX_POSITION_SIZE=0.1
RISK_PERCENTAGE=0.02

# ========================================
# FEATURE FLAGS
# ========================================
ENABLE_NEWS_ANALYSIS=true
ENABLE_REDDIT_ANALYSIS=true
ENABLE_WEBSOCKET_FEED=true
ENABLE_GEMINI_AI=true

# ========================================
# SYSTEM CONFIGURATION
# ========================================
LOG_LEVEL=INFO
API_V1_STR=/api/v1
PROJECT_NAME=GenX-EA Trading Platform
VERSION=2.0.0

# ========================================
# INTERVALS & TIMING
# ========================================
NEWS_REFRESH_INTERVAL=300
REDDIT_REFRESH_INTERVAL=600
WEBSOCKET_RECONNECT_INTERVAL=5
MAX_WEBSOCKET_RETRIES=10
SENTIMENT_THRESHOLD=0.6

# ========================================
# DEPLOYMENT & MONITORING
# ========================================
NODE_ENV=development  # or "production"
DOMAIN=your-domain.com
EMAIL=your-email@domain.com
EOF

print_status ".env file created successfully!"

echo ""
print_header "Required API Keys Setup"

print_status "You need to configure the following REQUIRED API keys:"
echo ""

echo "🔴 CRITICAL (Required for basic functionality):"
echo "  1. GEMINI_API_KEY - Google Gemini AI for market analysis"
echo "  2. BYBIT_API_KEY - Bybit exchange for crypto trading"
echo "  3. BYBIT_API_SECRET - Bybit API secret"
echo ""

echo "🟡 IMPORTANT (Recommended for full functionality):"
echo "  4. FXCM_API_KEY - FXCM for forex trading"
echo "  5. FXCM_ACCESS_TOKEN - FXCM access token"
echo "  6. FXCM_ACCOUNT_ID - FXCM account ID"
echo ""

echo "🟢 OPTIONAL (Enhanced features):"
echo "  7. News APIs (NEWSDATA_API_KEY, ALPHAVANTAGE_API_KEY, etc.)"
echo "  8. Reddit API (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)"
echo "  9. Telegram/Discord bots (TELEGRAM_BOT_TOKEN, DISCORD_TOKEN)"
echo ""

print_status "Opening .env file for editing..."
echo ""

# Try to open the file in the default editor
if command -v code &> /dev/null; then
    print_status "Opening in VS Code..."
    code .env
elif command -v nano &> /dev/null; then
    print_status "Opening in nano..."
    nano .env
elif command -v vim &> /dev/null; then
    print_status "Opening in vim..."
    vim .env
else
    print_warning "Please manually edit the .env file with your API keys."
fi

echo ""
print_header "Next Steps"

print_status "1. Edit the .env file with your actual API keys"
print_status "2. Run the validation script: python scripts/validate_api_keys.py"
print_status "3. Start the platform: uvicorn api.main:app --reload"

echo ""
print_status "API Key Sources:"
echo "  • Gemini AI: https://makersuite.google.com/app/apikey"
echo "  • Bybit: https://www.bybit.com/en/account/api-key"
echo "  • FXCM: https://www.fxcm.com/markets/forex-trading-demo/"
echo "  • News APIs: Various providers (see API_KEY_SETUP.md for details)"

echo ""
print_warning "IMPORTANT: Never commit your .env file to version control!"
print_warning "The .env file is already in .gitignore for security."

echo ""
print_status "Setup complete! 🎉"
print_status "Your GenX_FX trading platform is ready for configuration." 