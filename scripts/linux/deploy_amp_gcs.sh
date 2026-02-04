#!/bin/bash

# AMP System GCS Deployment Script
# Deploys the AMP trading system to Google Cloud Storage and Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="fortress-notes-omrjz"
REGION="us-central1"
SERVICE_NAME="amp-trading-system"
BUCKET_NAME="amp-trading-system-data"
: "${GOOGLE_APPLICATION_CREDENTIALS:?Set GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON key file (do not commit it).}"
: "${AMP_TOKEN:?Set AMP_TOKEN in your environment.}"

# Optional (only if your deployment needs it)
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI not found. Installing..."
        curl https://sdk.cloud.google.com | bash
        exec -l $SHELL
        source ~/.bashrc
    fi
    print_success "Google Cloud CLI is available"
}

# Authenticate with Google Cloud
authenticate_gcloud() {
    print_status "Authenticating with Google Cloud..."
    
    if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        print_error "GOOGLE_APPLICATION_CREDENTIALS file not found: $GOOGLE_APPLICATION_CREDENTIALS"
        exit 1
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    
    # Authenticate with service account
    gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
    
    print_success "Authenticated with Google Cloud"
}

# Create GCS bucket
create_gcs_bucket() {
    print_status "Creating GCS bucket: $BUCKET_NAME"
    
    if ! gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
        gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
        print_success "Created GCS bucket: $BUCKET_NAME"
    else
        print_warning "Bucket $BUCKET_NAME already exists"
    fi
}

# Upload AMP system files to GCS
upload_to_gcs() {
    print_status "Uploading AMP system files to GCS..."
    
    # Create deployment package
    tar -czf amp-system.tar.gz \
        amp_cli.py \
        amp_config.json \
        amp_auth.json \
        amp-plugins/ \
        requirements-amp.txt \
        docker-compose.amp.yml \
        --exclude='*.pyc' \
        --exclude='__pycache__'
    
    # Upload to GCS
    gsutil cp amp-system.tar.gz gs://$BUCKET_NAME/
    gsutil cp amp_config.json gs://$BUCKET_NAME/
    gsutil cp amp_auth.json gs://$BUCKET_NAME/
    
    print_success "Uploaded AMP system files to GCS"
}

# Create Cloud Run service
deploy_to_cloud_run() {
    print_status "Deploying AMP system to Cloud Run..."
    
    # Create Dockerfile for Cloud Run
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-amp.txt .
RUN pip install -r requirements-amp.txt

# Copy application files
COPY amp_cli.py .
COPY amp_config.json .
COPY amp_auth.json .
COPY amp-plugins/ ./amp-plugins/

# Create startup script
RUN echo '#!/bin/bash\npython3 amp_cli.py status' > start.sh && chmod +x start.sh

# Expose port
EXPOSE 8080

# Start the application
CMD ["python3", "amp_cli.py", "status"]
EOF

    # Build and deploy to Cloud Run
    gcloud run deploy $SERVICE_NAME \
        --source . \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10 \
        --set-env-vars "AMP_TOKEN=$AMP_TOKEN,PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME${GITHUB_TOKEN:+,GITHUB_TOKEN=$GITHUB_TOKEN}"

    print_success "Deployed AMP system to Cloud Run"
}

# Create environment file
create_env_file() {
    print_status "Creating environment file..."
    
    cat > .env.example << EOF
# AMP System Environment Configuration (template)
# Copy to .env (gitignored) and fill values. Do NOT commit real credentials.

AMP_TOKEN=
GITHUB_TOKEN=
PROJECT_ID=$PROJECT_ID
BUCKET_NAME=$BUCKET_NAME
REGION=$REGION
SERVICE_NAME=$SERVICE_NAME

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account-key.json

# AMP System Configuration
AMP_ENV=production
AMP_LOG_LEVEL=INFO
AMP_API_PORT=8080
EOF

    print_success "Wrote .env.example (template only)"
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Get the Cloud Run service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    print_status "Service URL: $SERVICE_URL"
    
    # Test the service
    if curl -s "$SERVICE_URL" > /dev/null; then
        print_success "Deployment test successful"
    else
        print_warning "Deployment test failed - service may still be starting"
    fi
}

# Main deployment function
main() {
    echo -e "${GREEN}🚀 Starting AMP System GCS Deployment${NC}"
    echo "=================================================="
    
    print_status "Project ID: $PROJECT_ID"
    print_status "Region: $REGION"
    print_status "Service Name: $SERVICE_NAME"
    print_status "Bucket Name: $BUCKET_NAME"
    
    # Execute deployment steps
    check_gcloud
    authenticate_gcloud
    create_gcs_bucket
    upload_to_gcs
    create_env_file
    deploy_to_cloud_run
    test_deployment
    
    echo ""
    echo -e "${GREEN}🎉 AMP System GCS Deployment Complete!${NC}"
    echo "=================================================="
    print_success "GCS Bucket: gs://$BUCKET_NAME"
    print_success "Cloud Run Service: $SERVICE_NAME"
    print_success "Region: $REGION"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null || echo "Service URL will be available after deployment completes")
    print_success "Service URL: $SERVICE_URL"
    
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. Monitor deployment: gcloud run services describe $SERVICE_NAME --region=$REGION"
    echo "2. View logs: gcloud logs tail --service=$SERVICE_NAME"
    echo "3. Access AMP CLI: gcloud run services call $SERVICE_NAME --region=$REGION"
    echo "4. Upload data: gsutil cp your-data.csv gs://$BUCKET_NAME/"
}

# Run main function
main "$@"