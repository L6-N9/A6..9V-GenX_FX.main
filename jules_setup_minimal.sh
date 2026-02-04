#!/bin/bash
set -e

echo "🚀 Starting Minimal Jules Setup..."

# Install Firebase and Google AI tools
echo "📦 Installing global tools..."
npm install -g firebase-tools @google/generative-ai

# Install project dependencies
echo "📦 Installing project dependencies..."
if ! command -v pnpm &> /dev/null; then npm install -g pnpm; fi
pnpm install

echo "✅ Minimal Setup Complete!"
