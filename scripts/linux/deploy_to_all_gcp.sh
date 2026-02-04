#!/bin/bash

# GenX FX Multi-Project GCP Deployment Script
# Deploys the application to all specified Google Cloud projects

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Target Projects
PROJECTS=(
    "fortress-notes-omrjz"
    "genx-467217"
    "soloist-ai-a6-9v"
    "crested-climber-464919-b2"
    "genx-fx-trading"
)

# Configuration
REGION="us-central1"
CONFIG_FILE="cloudbuild.immediate.yaml"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI not found. Please install it first."
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    print_error "No active Google Cloud account found. Please run 'gcloud auth login' or 'gcloud auth activate-service-account'."
    exit 1
fi

echo -e "${GREEN}🚀 Starting Multi-Project Deployment${NC}"
echo "=================================================="

for PROJECT_ID in "${PROJECTS[@]}"; do
    echo ""
    print_status "Deploying to Project: $PROJECT_ID"

    # Set project
    if ! gcloud config set project "$PROJECT_ID" 2>/dev/null; then
        print_error "Failed to set project to $PROJECT_ID. Skipping..."
        continue
    fi

    # Enable necessary APIs
    print_status "Enabling required APIs for $PROJECT_ID..."
    gcloud services enable cloudbuild.googleapis.com \
        run.googleapis.com \
        artifactregistry.googleapis.com \
        --project "$PROJECT_ID"

    # Submit build
    print_status "Submitting Cloud Build for $PROJECT_ID..."
    if gcloud builds submit --config "$CONFIG_FILE" --project "$PROJECT_ID"; then
        print_success "Successfully deployed to $PROJECT_ID"
    else
        print_error "Deployment failed for $PROJECT_ID"
    fi
done

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Multi-Project Deployment Process Completed!${NC}"
