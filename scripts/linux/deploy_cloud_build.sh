#!/bin/bash

# GenX Trading System - Cloud Build Deployment Script
# This script triggers the Cloud Build process for the Exness EA deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-""}
REGION=${REGION:-"europe-west1"}
SERVICE_NAME="genx-exness-ea"

echo -e "${BLUE}🚀 GenX Trading System - Cloud Build Deployment${NC}"
echo "=================================================="

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Please install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}❌ Error: Not authenticated with gcloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Get project ID if not set
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ Error: No project ID found${NC}"
        echo "Please set your project: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo ""

# Enable required APIs
echo -e "${YELLOW}🔧 Ensuring required APIs are enabled...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

echo -e "${YELLOW}🏗️  Starting Cloud Build...${NC}"

# Submit the build
BUILD_ID=$(gcloud builds submit \
    --config=cloudbuild.yaml \
    --project=$PROJECT_ID \
    --format="value(metadata.build.id)" \
    .)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build submitted successfully!${NC}"
    echo "  Build ID: $BUILD_ID"
    echo ""
    
    # Watch the build progress
    echo -e "${YELLOW}👀 Monitoring build progress...${NC}"
    gcloud builds log $BUILD_ID --stream --project=$PROJECT_ID
    
    # Check final build status
    BUILD_STATUS=$(gcloud builds describe $BUILD_ID --project=$PROJECT_ID --format="value(status)")
    
    if [ "$BUILD_STATUS" = "SUCCESS" ]; then
        echo ""
        echo -e "${GREEN}🎉 Deployment successful!${NC}"
        echo ""
        echo -e "${BLUE}📊 Service Information:${NC}"
        echo "  Service Name: $SERVICE_NAME"
        echo "  Region: $REGION"
        echo ""
        
        # Get service URL
        SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
            --region=$REGION \
            --project=$PROJECT_ID \
            --format="value(status.url)")
        
        if [ ! -z "$SERVICE_URL" ]; then
            echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
            echo -e "${GREEN}🏥 Health Check: $SERVICE_URL/health${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}✅ GenX Trading System is now running on Cloud Run!${NC}"
        
    else
        echo ""
        echo -e "${RED}❌ Build failed with status: $BUILD_STATUS${NC}"
        echo "Check the build logs above for details."
        exit 1
    fi
    
else
    echo -e "${RED}❌ Failed to submit build${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Monitor your trading signals in the Cloud Run logs"
echo "2. Check the health endpoint: $SERVICE_URL/health"
echo "3. Configure your MT4/5 EA to connect to the service"
echo ""
echo -e "${YELLOW}💡 Tip: Use 'gcloud run logs tail $SERVICE_NAME --region=$REGION' to follow logs${NC}"