#!/bin/bash

# GenX Trading Platform - Deployment Fix Script
# This script diagnoses and fixes common Google Cloud deployment issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 GenX Trading Platform - Deployment Fix Script${NC}"
echo "======================================================="

# Function to check command existence
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
}

# Function to fix Docker build issues
fix_docker_issues() {
    echo -e "${YELLOW}🔧 Fixing Docker configuration...${NC}"
    
    # Use the fixed Dockerfile
    if [ -f "Dockerfile.exness.fixed" ]; then
        cp Dockerfile.exness.fixed Dockerfile.exness
        echo -e "${GREEN}✅ Updated Dockerfile.exness with fixes${NC}"
    fi
    
    # Test Docker build locally
    echo -e "${YELLOW}🧪 Testing Docker build locally...${NC}"
    if docker build -f Dockerfile.exness -t genx-trading-test . --no-cache; then
        echo -e "${GREEN}✅ Docker build successful${NC}"
        docker rmi genx-trading-test 2>/dev/null || true
    else
        echo -e "${RED}❌ Docker build failed${NC}"
        echo "Common fixes:"
        echo "1. Check if all required directories exist"
        echo "2. Verify requirements.txt has correct dependencies"
        echo "3. Ensure main.py exists and is executable"
        return 1
    fi
}

# Function to check Google Cloud configuration
check_gcloud_config() {
    echo -e "${YELLOW}🔧 Checking Google Cloud configuration...${NC}"
    
    if ! check_command gcloud; then
        echo -e "${YELLOW}Installing Google Cloud SDK...${NC}"
        chmod +x setup_gcloud.sh
        ./setup_gcloud.sh
        return 1
    fi
    
    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        echo -e "${RED}❌ Not authenticated with gcloud${NC}"
        echo "Run: gcloud auth login"
        return 1
    fi
    
    # Check project configuration
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ No project ID configured${NC}"
        echo "Run: gcloud config set project YOUR_PROJECT_ID"
        return 1
    fi
    
    echo -e "${GREEN}✅ Project ID: $PROJECT_ID${NC}"
    
    # Check required APIs
    echo -e "${YELLOW}Checking required APIs...${NC}"
    REQUIRED_APIS=("cloudbuild.googleapis.com" "run.googleapis.com" "containerregistry.googleapis.com")
    
    for api in "${REQUIRED_APIS[@]}"; do
        if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
            echo -e "${GREEN}✅ $api is enabled${NC}"
        else
            echo -e "${YELLOW}🔧 Enabling $api...${NC}"
            gcloud services enable $api --project=$PROJECT_ID
        fi
    done
}

# Function to fix Cloud Build configuration
fix_cloudbuild_config() {
    echo -e "${YELLOW}🔧 Checking Cloud Build configuration...${NC}"
    
    # Create optimized cloudbuild.yaml
    cat > cloudbuild.fixed.yaml << 'EOF'
steps:
  # Build the container image with caching
  - name: 'gcr.io/cloud-builders/docker'
    args: 
      - 'build'
      - '-f'
      - 'Dockerfile.exness'
      - '-t'
      - 'gcr.io/$PROJECT_ID/genx-exness-ea:$BUILD_ID'
      - '-t'
      - 'gcr.io/$PROJECT_ID/genx-exness-ea:latest'
      - '.'
    timeout: '1800s'
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', 'gcr.io/$PROJECT_ID/genx-exness-ea']
    timeout: '600s'
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'genx-exness-ea'
      - '--image'
      - 'gcr.io/$PROJECT_ID/genx-exness-ea:latest'
      - '--region'
      - 'europe-west1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '2'
      - '--timeout'
      - '3600'
      - '--concurrency'
      - '80'
      - '--port'
      - '8080'
      - '--set-env-vars'
      - 'BROKER=exness,TRADING_MODE=live,PYTHONPATH=/app'
      - '--max-instances'
      - '10'
      - '--min-instances'
      - '0'
    timeout: '600s'

images:
  - 'gcr.io/$PROJECT_ID/genx-exness-ea'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'E2_HIGHCPU_8'
  diskSizeGb: 100
  substitution_option: 'ALLOW_LOOSE'

timeout: '3600s'
EOF

    echo -e "${GREEN}✅ Created optimized cloudbuild.fixed.yaml${NC}"
}

# Function to check file structure
check_file_structure() {
    echo -e "${YELLOW}🔧 Checking required files and directories...${NC}"
    
    REQUIRED_FILES=("main.py" "requirements.txt" "Dockerfile.exness")
    REQUIRED_DIRS=("core" "api" "config" "utils" "services" "shared" "database" "expert-advisors")
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}✅ $file exists${NC}"
        else
            echo -e "${RED}❌ $file is missing${NC}"
        fi
    done
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}✅ $dir/ directory exists${NC}"
        else
            echo -e "${YELLOW}⚠️  $dir/ directory is missing${NC}"
        fi
    done
}

# Function to create missing health check endpoint
create_health_check() {
    echo -e "${YELLOW}🔧 Ensuring health check endpoint exists...${NC}"
    
    if ! grep -q "/health" main.py; then
        echo -e "${YELLOW}Adding health check endpoint to main.py...${NC}"
        
        cat >> main.py << 'EOF'

# Health check endpoint for Cloud Run
import http.server
import socketserver
import threading
from urllib.parse import urlparse

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "genx-trading"}')
        else:
            self.send_response(404)
            self.end_headers()

# Start health check server
def start_health_server():
    port = 8080
    with socketserver.TCPServer(("", port), HealthCheckHandler) as httpd:
        httpd.serve_forever()

# Start health check in background
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()
EOF
        echo -e "${GREEN}✅ Added health check endpoint${NC}"
    else
        echo -e "${GREEN}✅ Health check endpoint already exists${NC}"
    fi
}

# Main execution
echo -e "${BLUE}Starting diagnosis and fixes...${NC}"
echo ""

# 1. Check file structure
check_file_structure

echo ""

# 2. Check and install gcloud
check_gcloud_config

echo ""

# 3. Fix Docker issues
check_command docker && fix_docker_issues

echo ""

# 4. Fix Cloud Build configuration
fix_cloudbuild_config

echo ""

# 5. Create health check
create_health_check

echo ""
echo -e "${GREEN}🎉 Deployment fixes completed!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Run: gcloud auth login (if not authenticated)"
echo "2. Run: gcloud config set project YOUR_PROJECT_ID"
echo "3. Run: ./deploy_cloud_build_fixed.sh"
echo ""
echo -e "${YELLOW}💡 Tip: Use 'cloudbuild.fixed.yaml' for deployment${NC}"