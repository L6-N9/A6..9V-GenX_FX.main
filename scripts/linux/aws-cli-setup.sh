#!/bin/bash
# AWS CLI Setup for Cursor Agent

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version

# Configure AWS (interactive)
echo "Run: aws configure"
echo "Enter your AWS Access Key ID and Secret Access Key"