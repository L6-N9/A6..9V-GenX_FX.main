#!/bin/bash
# GenX FX Static Site Deployment Script

set -e

# Configuration
BUCKET_NAME="genx-fx-static-9319"
DISTRIBUTION_ID="E3SP3XU9YMK917"
CLOUDFRONT_URL="https://dfdc34s1qr7cw.cloudfront.net"
S3_WEBSITE_URL="https://genx-fx-static-9319.s3-website-us-east-1.amazonaws.com"

echo "🚀 Deploying GenX FX Static Site..."

# Build static files (if needed)
if [ -d "client" ]; then
    echo "📦 Building client application..."
    cd client
    if [ -f "package.json" ]; then
        npm install
        npm run build
        cd dist || cd build || cd .
    else
        echo "No build process needed, using static files as-is"
    fi
    cd ..
fi

# Upload to S3
echo "📤 Uploading files to S3 bucket: $BUCKET_NAME"
aws s3 sync client/ s3://$BUCKET_NAME/ --delete --region us-east-1

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*" --region us-east-1

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your site is available at:"
echo "   CloudFront (HTTPS): $CLOUDFRONT_URL"
echo "   S3 Website (HTTP):  $S3_WEBSITE_URL"
echo ""
echo "📊 CloudFront distribution status:"
aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.{Status:Status,DomainName:DomainName}" --region us-east-1
