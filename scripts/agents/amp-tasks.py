"""
AMP Task 2: Upload secrets to GitHub.

This script defines the secrets that need to be uploaded to the GitHub
repository for the application to function correctly. It is intended to be
used with the 'github-secrets-api.py' script.
"""

import os

import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "Mouy-leng/GenX_FX"

secrets = {
    "BYBIT_API_KEY": "your_bybit_key",
    "BYBIT_SECRET": "your_bybit_secret",
    "FXCM_USERNAME": "your_fxcm_username",
    "FXCM_PASSWORD": "your_fxcm_password",
    "GEMINI_API_KEY": "your_gemini_key",
    "TELEGRAM_BOT_TOKEN": "your_telegram_token",
}

print("AMP: Upload secrets to GitHub repository")
print("Run: python github-secrets-api.py")
