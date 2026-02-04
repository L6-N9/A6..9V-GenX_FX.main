#!/bin/bash
# Script to install Google Cloud CLI on Debian/Ubuntu systems

set -e

echo "🚀 Starting Google Cloud CLI installation..."

# Install prerequisite packages
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates gnupg curl

# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Add the gcloud SDK repo to the package manager
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Update and install the CLI
sudo apt-get update && sudo apt-get install -y google-cloud-cli

echo "✅ Google Cloud CLI installed successfully!"
gcloud --version
