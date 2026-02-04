#!/bin/bash
# WhatsApp Deployment Setup Script for GenX Trading Platform
# This script configures the WhatsApp integration for signal notifications

set -e

echo "======================================================================"
echo "GenX Trading Platform - WhatsApp Integration Setup"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
fi

# Function to update or add environment variable
update_env_var() {
    local key=$1
    local value=$2
    local file=".env"

    if grep -q "^${key}=" "$file"; then
        # Update existing variable
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
        echo -e "${GREEN}✅ Updated ${key}${NC}"
    else
        # Add new variable
        echo "${key}=${value}" >> "$file"
        echo -e "${GREEN}✅ Added ${key}${NC}"
    fi
}

# Prompt for WhatsApp group URL if not provided as argument
if [ -n "$1" ]; then
    WHATSAPP_GROUP_URL="$1"
else
    echo -e "${YELLOW}Enter WhatsApp group URL (or press Enter to use default):${NC}"
    read -r WHATSAPP_GROUP_URL

    # Use default if not provided
    if [ -z "$WHATSAPP_GROUP_URL" ]; then
        WHATSAPP_GROUP_URL="https://chat.whatsapp.com/DYemXrBnMD63K55bjUMKYF"
        echo -e "${YELLOW}Using default group URL${NC}"
    fi
fi

echo ""
echo "======================================================================"
echo "Configuring WhatsApp Integration"
echo "======================================================================"

# Update .env file with WhatsApp configuration
update_env_var "WHATSAPP_GROUP_URL" "$WHATSAPP_GROUP_URL"

echo ""
echo "======================================================================"
echo "Installing Dependencies"
echo "======================================================================"

# Check if pip is available
if command -v pip &> /dev/null; then
    echo -e "${GREEN}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ pip not found. Please install Python and pip first.${NC}"
    exit 1
fi

echo ""
echo "======================================================================"
echo "Testing WhatsApp Integration"
echo "======================================================================"

# Run the test script
if [ -f "test_whatsapp_bot.py" ]; then
    echo -e "${GREEN}Running integration tests...${NC}"
    python test_whatsapp_bot.py

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
    else
        echo -e "${RED}❌ Some tests failed. Please check the output above.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Test script not found, skipping tests${NC}"
fi

echo ""
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo -e "${GREEN}WhatsApp integration is now configured!${NC}"
echo ""
echo "📌 Group URL: $WHATSAPP_GROUP_URL"
echo ""
echo "Next steps:"
echo "1. Verify the group URL is correct and you have access"
echo "2. Review the WhatsApp Integration Guide: WHATSAPP_INTEGRATION_GUIDE.md"
echo "3. Start the trading platform: npm run dev"
echo "4. Monitor logs for WhatsApp notifications"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "- Current implementation logs messages for manual sharing"
echo "- For automated messaging, consider WhatsApp Business API"
echo "- See WHATSAPP_INTEGRATION_GUIDE.md for production options"
echo ""
echo "======================================================================"
