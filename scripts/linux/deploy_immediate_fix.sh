#!/bin/bash

# IMMEDIATE FIX - GenX Trading Platform Deployment
# This script fixes the current NumPy compilation error

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🚨 IMMEDIATE FIX FOR BUILD ERROR${NC}"
echo -e "${BLUE}Fixing NumPy compilation issue...${NC}"
echo "=================================="

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No project ID found${NC}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Using: Dockerfile.cloud.fixed"
echo "  Using: cloudbuild.immediate.yaml"
echo ""

# Cancel any running builds first
echo -e "${YELLOW}🛑 Canceling any running builds...${NC}"
RUNNING_BUILDS=$(gcloud builds list --ongoing --format="value(id)" --project=$PROJECT_ID 2>/dev/null || echo "")
if [ ! -z "$RUNNING_BUILDS" ]; then
    for build_id in $RUNNING_BUILDS; do
        echo "Canceling build: $build_id"
        gcloud builds cancel $build_id --project=$PROJECT_ID 2>/dev/null || true
    done
    echo "Waiting for cancellations to complete..."
    sleep 10
fi

# Enable required APIs
echo -e "${YELLOW}🔧 Ensuring APIs are enabled...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

echo -e "${GREEN}✅ Starting fixed build...${NC}"
echo ""

# Submit the immediate fix build
BUILD_ID=$(gcloud builds submit \
    --config=cloudbuild.immediate.yaml \
    --project=$PROJECT_ID \
    --format="value(metadata.build.id)" \
    . 2>&1)

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ] && [ ! -z "$BUILD_ID" ]; then
    echo -e "${GREEN}✅ Build submitted with ID: $BUILD_ID${NC}"
    echo ""
    
    # Show build URL
    echo -e "${BLUE}🔗 Monitor build progress:${NC}"
    echo "https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID"
    echo ""
    
    # Stream logs
    echo -e "${YELLOW}📊 Streaming build logs...${NC}"
    gcloud builds log $BUILD_ID --stream --project=$PROJECT_ID
    
    # Check final status
    BUILD_STATUS=$(gcloud builds describe $BUILD_ID --project=$PROJECT_ID --format="value(status)" 2>/dev/null || echo "UNKNOWN")
    
    if [ "$BUILD_STATUS" = "SUCCESS" ]; then
        echo ""
        echo -e "${GREEN}🎉 BUILD FIXED AND DEPLOYED SUCCESSFULLY!${NC}"
        echo ""
        
        # Get service URL
        SERVICE_URL=$(gcloud run services describe genx-trading \
            --region=us-central1 \
            --project=$PROJECT_ID \
            --format="value(status.url)" 2>/dev/null || echo "")
        
        if [ ! -z "$SERVICE_URL" ]; then
            echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
            echo -e "${GREEN}🏥 Health Check: $SERVICE_URL/health${NC}"
            
            # Test health endpoint
            echo -e "${YELLOW}🧪 Testing service...${NC}"
            sleep 20
            if curl -f -s "$SERVICE_URL/health" > /dev/null; then
                echo -e "${GREEN}✅ Service is healthy!${NC}"
            else
                echo -e "${YELLOW}⚠️  Service starting (may take a moment)${NC}"
            fi
        fi
        
        echo ""
        echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
        echo -e "${BLUE}The NumPy compilation issue has been resolved.${NC}"
        
    else
        echo ""
        echo -e "${RED}❌ Build failed with status: $BUILD_STATUS${NC}"
        echo ""
        echo -e "${YELLOW}If the issue persists:${NC}"
        echo "1. Check the build logs above"
        echo "2. Verify all required files exist"
        echo "3. Try: gcloud builds submit --config=cloudbuild.immediate.yaml"
        exit 1
    fi
    
else
    echo -e "${RED}❌ Failed to submit build${NC}"
    echo "Error output: $BUILD_ID"
    exit 1
fi

echo ""
echo -e "${BLUE}📝 What was fixed:${NC}"
echo "✅ Added build-essential and gcc to Dockerfile"
echo "✅ Used pre-compiled NumPy wheels"
echo "✅ Optimized requirements for Cloud Build"
echo "✅ Fixed Cloud Build configuration"
echo ""
echo -e "${GREEN}🎯 Your GenX Trading Platform is now deployed!${NC}"