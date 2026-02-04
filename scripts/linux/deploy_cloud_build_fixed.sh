#!/bin/bash

# GenX Trading System - Fixed Cloud Build Deployment Script
# This script uses the improved configurations to deploy successfully

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

echo -e "${BLUE}🚀 GenX Trading System - Fixed Cloud Build Deployment${NC}"
echo "=========================================================="

# Pre-deployment checks
echo -e "${YELLOW}🔍 Running pre-deployment checks...${NC}"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Run the fix script first: ./fix_deployment.sh"
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

# Check if required files exist
if [ ! -f "cloudbuild.fixed.yaml" ]; then
    echo -e "${RED}❌ Error: cloudbuild.fixed.yaml not found${NC}"
    echo "Run the fix script first: ./fix_deployment.sh"
    exit 1
fi

if [ ! -f "Dockerfile.exness.fixed" ]; then
    echo -e "${RED}❌ Error: Dockerfile.exness.fixed not found${NC}"
    echo "Run the fix script first: ./fix_deployment.sh"
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo ""

# Enable required APIs with error handling
echo -e "${YELLOW}🔧 Ensuring required APIs are enabled...${NC}"
REQUIRED_APIS=("cloudbuild.googleapis.com" "run.googleapis.com" "containerregistry.googleapis.com" "artifactregistry.googleapis.com")

for api in "${REQUIRED_APIS[@]}"; do
    echo "Enabling $api..."
    if ! gcloud services enable $api --project=$PROJECT_ID; then
        echo -e "${YELLOW}⚠️  Warning: Could not enable $api (might already be enabled)${NC}"
    fi
done

# Use fixed configurations
echo -e "${YELLOW}📝 Using fixed configurations...${NC}"
cp Dockerfile.exness.fixed Dockerfile.exness
echo "✅ Using fixed Dockerfile"

echo -e "${YELLOW}🏗️  Starting Cloud Build with fixed configuration...${NC}"

# Submit the build with the fixed configuration
BUILD_ID=$(gcloud builds submit \
    --config=cloudbuild.fixed.yaml \
    --project=$PROJECT_ID \
    --format="value(metadata.build.id)" \
    . 2>&1)

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ] && [ ! -z "$BUILD_ID" ]; then
    echo -e "${GREEN}✅ Build submitted successfully!${NC}"
    echo "  Build ID: $BUILD_ID"
    echo ""
    
    # Watch the build progress
    echo -e "${YELLOW}👀 Monitoring build progress...${NC}"
    echo "  You can also view the build at:"
    echo "  https://console.cloud.google.com/cloud-build/builds/$BUILD_ID?project=$PROJECT_ID"
    echo ""
    
    if gcloud builds log $BUILD_ID --stream --project=$PROJECT_ID; then
        # Check final build status
        BUILD_STATUS=$(gcloud builds describe $BUILD_ID --project=$PROJECT_ID --format="value(status)" 2>/dev/null || echo "UNKNOWN")
        
        if [ "$BUILD_STATUS" = "SUCCESS" ]; then
            echo ""
            echo -e "${GREEN}🎉 Deployment successful!${NC}"
            echo ""
            echo -e "${BLUE}📊 Service Information:${NC}"
            echo "  Service Name: $SERVICE_NAME"
            echo "  Region: $REGION"
            echo ""
            
            # Get service URL with retry
            echo -e "${YELLOW}🔍 Getting service URL...${NC}"
            sleep 10  # Wait for service to be ready
            
            SERVICE_URL=""
            for i in {1..5}; do
                SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
                    --region=$REGION \
                    --project=$PROJECT_ID \
                    --format="value(status.url)" 2>/dev/null || echo "")
                
                if [ ! -z "$SERVICE_URL" ]; then
                    break
                fi
                echo "Waiting for service to be ready... (attempt $i/5)"
                sleep 5
            done
            
            if [ ! -z "$SERVICE_URL" ]; then
                echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
                echo -e "${GREEN}🏥 Health Check: $SERVICE_URL/health${NC}"
                
                # Test health endpoint
                echo -e "${YELLOW}🧪 Testing health endpoint...${NC}"
                sleep 15  # Give service time to start
                if curl -f "$SERVICE_URL/health" &>/dev/null; then
                    echo -e "${GREEN}✅ Health check passed!${NC}"
                else
                    echo -e "${YELLOW}⚠️  Health check failed (service might still be starting)${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  Could not retrieve service URL${NC}"
            fi
            
            echo ""
            echo -e "${GREEN}✅ GenX Trading System is now running on Cloud Run!${NC}"
            
        else
            echo ""
            echo -e "${RED}❌ Build failed with status: $BUILD_STATUS${NC}"
            echo ""
            echo -e "${YELLOW}📝 Troubleshooting tips:${NC}"
            echo "1. Check the build logs above for specific errors"
            echo "2. Verify all required files exist in the repository"
            echo "3. Check Docker configuration and dependencies"
            echo "4. Run: ./fix_deployment.sh to diagnose issues"
            exit 1
        fi
    else
        echo -e "${RED}❌ Failed to stream build logs${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ Failed to submit build${NC}"
    echo "Build output: $BUILD_ID"
    echo ""
    echo -e "${YELLOW}📝 Troubleshooting tips:${NC}"
    echo "1. Check your internet connection"
    echo "2. Verify project permissions"
    echo "3. Ensure all required APIs are enabled"
    echo "4. Run: ./fix_deployment.sh to diagnose issues"
    exit 1
fi

echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "1. Monitor your trading signals: gcloud run logs tail $SERVICE_NAME --region=$REGION"
echo "2. Check service metrics in Cloud Console"
echo "3. Configure your MT4/5 EA to connect to: $SERVICE_URL"
echo ""
echo -e "${YELLOW}💡 Useful commands:${NC}"
echo "• View logs: gcloud run logs tail $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo "• Service info: gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo "• Update service: gcloud run services update $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"