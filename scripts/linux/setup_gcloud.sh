#!/bin/bash

# Google Cloud SDK Installation and Setup Script
# For Ubuntu/Debian systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Installing Google Cloud SDK...${NC}"

# Add Google Cloud SDK repository
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Install required packages
sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates gnupg

# Import Google Cloud SDK key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install Google Cloud SDK
sudo apt-get update && sudo apt-get install -y google-cloud-cli

echo -e "${GREEN}✅ Google Cloud SDK installed successfully!${NC}"
echo ""

# Check installation
gcloud version

echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Run: gcloud auth login"
echo "2. Run: gcloud config set project YOUR_PROJECT_ID"
echo "3. Run: gcloud auth configure-docker"
echo ""
echo -e "${BLUE}💡 Tip: Replace YOUR_PROJECT_ID with your actual Google Cloud project ID${NC}"