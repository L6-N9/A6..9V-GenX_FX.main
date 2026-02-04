#!/bin/bash

# GenX Trading Platform - Complete AMP Update Command
# This script updates the project with all new integrations

# Define amp function to use local python wrapper
amp() {
    python3 amp_wrapper.py "$@"
}

echo "🚀 Starting GenX Trading Platform AMP Update..."

# Main update command
amp update \
  --env .env \
  --set api_provider=gemini \
  --add-dependency google-generativeai>=0.3.0 \
  --add-dependency praw>=7.7.0 \
  --add-dependency newsapi-python>=0.2.6 \
  --add-dependency alpha-vantage>=2.3.1 \
  --add-dependency finnhub-python>=2.4.0 \
  --add-dependency beautifulsoup4>=4.12.0 \
  --add-dependency lxml>=4.9.0 \
  --add-dependency textblob>=0.17.1 \
  --add-dependency websockets>=11.0 \
  --add-env GEMINI_API_KEY=$GEMINI_API_KEY \
  --add-env NEWSDATA_API_KEY=$NEWSDATA_API_KEY \
  --add-env ALPHAVANTAGE_API_KEY=$ALPHAVANTAGE_API_KEY \
  --add-env CONTEXTUALWEB_API_KEY=$CONTEXTUALWEB_API_KEY \
  --add-env PREPNEWS_API_KEY=$PREPNEWS_API_KEY \
  --add-env FMP_API_KEY=$FMP_API_KEY \
  --add-env NEWSAPI_ORG_KEY=$NEWSAPI_ORG_KEY \
  --add-env FINNHUB_API_KEY=$FINNHUB_API_KEY \
  --add-env REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID \
  --add-env REDDIT_CLIENT_SECRET=$REDDIT_CLIENT_SECRET \
  --add-env REDDIT_USERNAME=$REDDIT_USERNAME \
  --add-env REDDIT_PASSWORD=$REDDIT_PASSWORD \
  --add-env REDDIT_USER_AGENT="GenX-Trading-Bot/1.0" \
  --add-env ENABLE_NEWS_ANALYSIS=true \
  --add-env ENABLE_REDDIT_ANALYSIS=true \
  --add-env ENABLE_WEBSOCKET_FEED=true \
  --add-env NEWS_REFRESH_INTERVAL=300 \
  --add-env REDDIT_REFRESH_INTERVAL=600 \
  --add-env WEBSOCKET_RECONNECT_INTERVAL=5 \
  --add-env MAX_WEBSOCKET_RETRIES=10 \
  --add-env SENTIMENT_THRESHOLD=0.6 \
  --description "Complete integration: Gemini AI, Reddit signals, multi-source news, and WebSocket streams"

echo "✅ Main AMP update complete!"

# Install individual plugins
echo "📦 Installing AMP plugins..."

# Gemini AI Integration
amp plugin-install gemini-integration \
  --source genx-trading \
  --enable-service gemini_service \
  --description "Google Gemini AI integration for market analysis"

# Reddit Signals
amp plugin-install reddit-signals \
  --source genx-trading \
  --enable-service reddit_service \
  --description "Reddit integration for social sentiment analysis"

# News Aggregator
amp plugin-install news-aggregator \
  --source genx-trading \
  --enable-service news_service \
  --description "Multi-source news aggregation for market analysis"

# WebSocket Streams
amp plugin-install websocket-streams \
  --source genx-trading \
  --enable-service websocket_service \
  --description "Multi-exchange WebSocket streams for real-time data"

echo "🎉 All AMP plugins installed successfully!"

# Additional configuration
echo "⚙️ Configuring services..."

# Update API configuration
amp config-set \
  --api-provider gemini \
  --enable-sentiment-analysis \
  --enable-social-signals \
  --enable-news-feeds \
  --enable-websocket-streams

# Set up service dependencies
amp service-enable \
  gemini_service \
  reddit_service \
  news_service \
  websocket_service

echo "🔧 Service configuration complete!"

# Verify installation
echo "🔍 Verifying installation..."

amp verify \
  --check-dependencies \
  --check-env-vars \
  --check-services \
  --check-api-keys

echo "✅ Installation verification complete!"

echo "🎯 GenX Trading Platform AMP Update Summary:"
echo "   ✅ Switched to Gemini AI API"
echo "   ✅ Added Reddit integration"
echo "   ✅ Added multi-source news aggregation"
echo "   ✅ Added WebSocket streaming"
echo "   ✅ Enhanced sentiment analysis"
echo "   ✅ Configured all services"
echo ""
echo "🚀 Your trading platform is now ready with advanced AI and real-time data!"
echo ""
echo "📝 Next steps:"
echo "   1. Set your API keys in .env file"
echo "   2. Test the new services: amp test --all"
echo "   3. Deploy to production: amp deploy"
