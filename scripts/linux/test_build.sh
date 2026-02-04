#!/bin/bash

echo "🧪 Testing Docker build process..."

# Test Docker build
echo "Building Docker image..."
docker build -f Dockerfile.exness -t genx-exness-test .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    
    # Test running the container
    echo "Testing container startup..."
    docker run --rm -d --name genx-test genx-exness-test
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        docker stop genx-test
        echo "Container stopped for cleanup"
    else
        echo "❌ Container failed to start"
    fi
else
    echo "❌ Docker build failed!"
    exit 1
fi