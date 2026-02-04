@echo off
gh auth login
gh secret set BYBIT_API_KEY --body "%BYBIT_API_KEY%"
gh secret set BYBIT_SECRET --body "%BYBIT_SECRET%"
gh secret set FXCM_USERNAME --body "%FXCM_USERNAME%"
gh secret set FXCM_PASSWORD --body "%FXCM_PASSWORD%"
gh secret set GEMINI_API_KEY --body "%GEMINI_API_KEY%"
gh secret set TELEGRAM_BOT_TOKEN --body "%TELEGRAM_BOT_TOKEN%"
gh secret set DISCORD_BOT_TOKEN --body "%DISCORD_BOT_TOKEN%"
gh variable set ENVIRONMENT --body "production"
gh variable set DEPLOY_REGION --body "us-central1"
echo GitHub secrets and variables configured