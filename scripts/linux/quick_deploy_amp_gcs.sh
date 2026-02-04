#!/bin/bash

# Quick AMP System GCS Deployment
# Simplified deployment script for rapid deployment

set -e

# Configuration
PROJECT_ID="fortress-notes-omrjz"
REGION="us-central1"
SERVICE_NAME="amp-trading-system"
BUCKET_NAME="amp-trading-system-data"
: "${GOOGLE_APPLICATION_CREDENTIALS:?Set GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON key file (do not commit it).}"
: "${AMP_TOKEN:?Set AMP_TOKEN in your environment.}"

# Optional (only if your deployment needs it)
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

echo "🚀 Quick AMP System GCS Deployment"
echo "=================================="

if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  echo "❌ GOOGLE_APPLICATION_CREDENTIALS file not found: $GOOGLE_APPLICATION_CREDENTIALS"
  exit 1
fi

# Install gcloud if not available
if ! command -v gcloud &> /dev/null; then
    echo "📥 Installing Google Cloud CLI..."
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
    source ~/.bashrc
fi

echo "✅ Google Cloud CLI ready"

# Authenticate and set project
gcloud config set project $PROJECT_ID
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"

echo "✅ Authenticated with Google Cloud"

# Create GCS bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME 2>/dev/null || echo "ℹ️  Bucket already exists"

echo "✅ GCS bucket ready"

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

echo "✅ Deployment package created"

# Upload to GCS
gsutil cp amp-system.tar.gz gs://$BUCKET_NAME/
gsutil cp amp_config.json gs://$BUCKET_NAME/
gsutil cp amp_auth.json gs://$BUCKET_NAME/

echo "✅ Files uploaded to GCS"

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

echo "✅ Dockerfile created"

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "AMP_TOKEN=$AMP_TOKEN,PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME${GITHUB_TOKEN:+,GITHUB_TOKEN=$GITHUB_TOKEN}"

echo "✅ Deployed to Cloud Run"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null || echo "Service URL will be available after deployment completes")

echo ""
echo "🎉 AMP System GCS Deployment Complete!"
echo "======================================"
echo "GCS Bucket: gs://$BUCKET_NAME"
echo "Cloud Run Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "Service URL: $SERVICE_URL"
echo ""
echo "📋 Next Steps:"
echo "1. Monitor: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "2. Logs: gcloud logs tail --service=$SERVICE_NAME"
echo "3. Access: gcloud run services call $SERVICE_NAME --region=$REGION"