import json
import os
import subprocess

# Load environment variables
with open(".env", "r") as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

# GitHub secrets to set
secrets = {
    "BYBIT_API_KEY": os.getenv("BYBIT_API_KEY", ""),
    "BYBIT_SECRET": os.getenv("BYBIT_SECRET", ""),
    "FXCM_USERNAME": os.getenv("FXCM_USERNAME", ""),
    "FXCM_PASSWORD": os.getenv("FXCM_PASSWORD", ""),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "DISCORD_BOT_TOKEN": os.getenv("DISCORD_BOT_TOKEN", ""),
}

print("GitHub secrets configured locally. Use GitHub web interface to set them.")
for key, value in secrets.items():
    if value:
        print(f"{key}: {'*' * len(value)}")
