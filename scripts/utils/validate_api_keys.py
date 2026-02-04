#!/usr/bin/env python3
"""
GenX_FX Trading Platform - API Key Validation Script
Validates all API keys and tests connections
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

import aiohttp

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class APIKeyValidator:
    """Validates API keys and tests connections"""

    def __init__(self):
        self.results = {}
        self.env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

    def load_env_file(self) -> bool:
        """Load environment variables from .env file"""
        if not os.path.exists(self.env_file):
            print(f"❌ .env file not found at: {self.env_file}")
            return False

        try:
            with open(self.env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key] = value
            print("✅ Environment variables loaded from .env")
            return True
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
            return False

    def check_api_key_exists(self, key_name: str, required: bool = False) -> bool:
        """Check if API key exists in environment"""
        value = os.getenv(key_name)
        if not value or value == f"your-{key_name.lower()}-here":
            if required:
                print(f"❌ {key_name}: MISSING (Required)")
                return False
            else:
                print(f"⚠️  {key_name}: Not set (Optional)")
                return False
        else:
            print(f"✅ {key_name}: Set")
            return True

    async def test_gemini_ai(self) -> bool:
        """Test Gemini AI connection"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return False

            # Simple test - try to import and initialize
            import google.generativeai as genai

            genai.configure(api_key=api_key)

            # Test with a simple prompt
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content("Hello, test connection")

            if response.text:
                print("✅ Gemini AI: Connection successful")
                return True
            else:
                print("❌ Gemini AI: No response received")
                return False

        except Exception as e:
            print(f"❌ Gemini AI: Connection failed - {e}")
            return False

    async def test_bybit_api(self) -> bool:
        """Test Bybit API connection"""
        try:
            api_key = os.getenv("BYBIT_API_KEY")
            api_secret = os.getenv("BYBIT_API_SECRET")

            if not api_key or not api_secret:
                return False

            # Test with pybit
            from pybit.unified_trading import HTTP

            session = HTTP(
                testnet=False,
                api_key=api_key,
                api_secret=api_secret,
            )

            # Test market data endpoint
            response = session.get_kline(
                category="spot", symbol="BTCUSDT", interval="1", limit=1
            )

            if response and "result" in response:
                print("✅ Bybit API: Connection successful")
                return True
            else:
                print("❌ Bybit API: Invalid response")
                return False

        except Exception as e:
            print(f"❌ Bybit API: Connection failed - {e}")
            return False

    async def test_news_api(self) -> bool:
        """Test News API connection"""
        try:
            api_key = os.getenv("NEWSAPI_ORG_KEY")
            if not api_key:
                return False

            # Test NewsAPI.org
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "ok":
                            print("✅ News API: Connection successful")
                            return True

            print("❌ News API: Invalid response")
            return False

        except Exception as e:
            print(f"❌ News API: Connection failed - {e}")
            return False

    async def test_reddit_api(self) -> bool:
        """Test Reddit API connection"""
        try:
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")

            if not client_id or not client_secret:
                return False

            # Test with praw
            import praw

            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="GenX-Trading-Bot/1.0",
            )

            # Test by getting a subreddit
            subreddit = reddit.subreddit("wallstreetbets")
            posts = list(subreddit.hot(limit=1))

            if posts:
                print("✅ Reddit API: Connection successful")
                return True
            else:
                print("❌ Reddit API: No posts retrieved")
                return False

        except Exception as e:
            print(f"❌ Reddit API: Connection failed - {e}")
            return False

    async def test_telegram_bot(self) -> bool:
        """Test Telegram Bot connection"""
        try:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                return False

            # Test bot info endpoint
            url = f"https://api.telegram.org/bot{bot_token}/getMe"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            print("✅ Telegram Bot: Connection successful")
                            return True

            print("❌ Telegram Bot: Invalid response")
            return False

        except Exception as e:
            print(f"❌ Telegram Bot: Connection failed - {e}")
            return False

    async def validate_all(self) -> Dict[str, bool]:
        """Validate all API keys and test connections"""
        print("🔧 GenX_FX API Key Validation")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Load environment variables
        if not self.load_env_file():
            return {}

        print("📋 API Key Status:")
        print("-" * 30)

        # Check required API keys
        required_keys = ["GEMINI_API_KEY", "BYBIT_API_KEY", "BYBIT_API_SECRET"]

        optional_keys = [
            "FXCM_API_KEY",
            "FXCM_ACCESS_TOKEN",
            "NEWSDATA_API_KEY",
            "ALPHAVANTAGE_API_KEY",
            "NEWSAPI_ORG_KEY",
            "FINNHUB_API_KEY",
            "FMP_API_KEY",
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "TELEGRAM_BOT_TOKEN",
            "DISCORD_TOKEN",
        ]

        # Check all keys
        for key in required_keys:
            self.results[key] = self.check_api_key_exists(key, required=True)

        for key in optional_keys:
            self.results[key] = self.check_api_key_exists(key, required=False)

        print()
        print("🧪 Testing API Connections:")
        print("-" * 30)

        # Test connections
        connection_tests = [
            ("Gemini AI", self.test_gemini_ai),
            ("Bybit API", self.test_bybit_api),
            ("News API", self.test_news_api),
            ("Reddit API", self.test_reddit_api),
            ("Telegram Bot", self.test_telegram_bot),
        ]

        for name, test_func in connection_tests:
            try:
                result = await test_func()
                self.results[f"{name}_connection"] = result
            except Exception as e:
                print(f"❌ {name}: Test failed - {e}")
                self.results[f"{name}_connection"] = False

        return self.results

    def generate_report(self) -> str:
        """Generate a validation report"""
        print()
        print("📊 Validation Report:")
        print("=" * 50)

        required_passed = 0
        required_total = 0
        optional_passed = 0
        optional_total = 0

        for key, value in self.results.items():
            if "connection" in key:
                continue

            if key in ["GEMINI_API_KEY", "BYBIT_API_KEY", "BYBIT_API_SECRET"]:
                required_total += 1
                if value:
                    required_passed += 1
            else:
                optional_total += 1
                if value:
                    optional_passed += 1

        print(f"Required API Keys: {required_passed}/{required_total} ✅")
        print(f"Optional API Keys: {optional_passed}/{optional_total} ✅")

        if required_passed == required_total:
            print("🎉 All required API keys are configured!")
            print("🚀 Your GenX_FX platform is ready to start!")
        else:
            print("⚠️  Some required API keys are missing.")
            print("Please configure the missing keys before starting the platform.")

        return "success" if required_passed == required_total else "incomplete"


async def main():
    """Main validation function"""
    validator = APIKeyValidator()
    results = await validator.validate_all()
    status = validator.generate_report()

    # Exit with appropriate code
    sys.exit(0 if status == "success" else 1)


if __name__ == "__main__":
    asyncio.run(main())
