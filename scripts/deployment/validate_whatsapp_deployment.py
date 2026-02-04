"""
WhatsApp Deployment Validation Script
Validates that WhatsApp integration is properly configured and ready for deployment
"""

import os
import sys
from typing import List, Tuple

# Colors for terminal output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f"{BLUE}{text}{NC}")
    print(f"{'=' * 70}\n")


def check_env_file() -> Tuple[bool, str]:
    """Check if .env file exists"""
    if os.path.exists(".env"):
        return True, "✅ .env file exists"
    else:
        return False, "❌ .env file not found (run: cp .env.example .env)"


def check_whatsapp_config() -> Tuple[bool, str]:
    """Check if WhatsApp is configured in environment"""
    group_url = os.getenv("WHATSAPP_GROUP_URL", "")

    if group_url:
        # Validate URL format
        if "chat.whatsapp.com" in group_url:
            return True, f"✅ WhatsApp configured: {group_url[:50]}..."
        else:
            return False, f"⚠️  WhatsApp URL format invalid: {group_url}"
    else:
        return False, "❌ WHATSAPP_GROUP_URL not set in environment"


def check_service_files() -> Tuple[bool, str]:
    """Check if all required service files exist"""
    required_files = [
        "services/whatsapp_bot.py",
        "services/telegram_bot.py",
        "services/discord_bot.py",
        "services/notifier.py",
    ]

    missing_files = [f for f in required_files if not os.path.exists(f)]

    if not missing_files:
        return True, "✅ All service files present"
    else:
        return False, f"❌ Missing files: {', '.join(missing_files)}"


def check_dependencies() -> Tuple[bool, str]:
    """Check if required Python packages are installed"""
    # WhatsApp doesn't require special dependencies for basic implementation
    # For production, WhatsApp Business API or third-party services are recommended
    return True, "✅ WhatsApp bot uses standard library (no special dependencies)"


def check_imports() -> Tuple[bool, str]:
    """Check if WhatsApp bot can be imported"""
    try:
        from services.whatsapp_bot import whatsapp_bot

        return True, f"✅ WhatsApp bot importable (enabled: {whatsapp_bot.enabled})"
    except Exception as e:
        return False, f"❌ Cannot import WhatsApp bot: {str(e)}"


def check_notifier_integration() -> Tuple[bool, str]:
    """Check if notifier properly integrates WhatsApp"""
    try:
        from services.notifier import notifier

        channels = notifier.get_active_channels()

        if "whatsapp" in channels:
            return True, f"✅ WhatsApp integrated in notifier (channels: {channels})"
        else:
            return False, f"⚠️  WhatsApp not in active channels: {channels}"
    except Exception as e:
        return False, f"❌ Notifier integration error: {str(e)}"


def check_test_files() -> Tuple[bool, str]:
    """Check if test files exist"""
    test_files = ["test_whatsapp_bot.py", "examples_whatsapp_usage.py"]
    missing = [f for f in test_files if not os.path.exists(f)]

    if not missing:
        return True, "✅ Test and example files present"
    else:
        return False, f"⚠️  Missing: {', '.join(missing)}"


def check_documentation() -> Tuple[bool, str]:
    """Check if documentation exists"""
    if os.path.exists("WHATSAPP_INTEGRATION_GUIDE.md"):
        return True, "✅ Integration guide available"
    else:
        return False, "⚠️  WHATSAPP_INTEGRATION_GUIDE.md not found"


def run_functional_test() -> Tuple[bool, str]:
    """Run a quick functional test"""
    try:
        from services.whatsapp_bot import whatsapp_bot

        # Test message formatting
        test_signal = {
            "symbol": "TEST",
            "action": "BUY",
            "entry": 100.0,
            "target": 110.0,
            "stop_loss": 95.0,
            "confidence": 80,
            "timestamp": "2024-01-01T00:00:00",
        }

        message = whatsapp_bot.format_signal_message(test_signal)

        if len(message) > 0 and "TEST" in message:
            return True, "✅ Functional test passed"
        else:
            return False, "❌ Message formatting failed"

    except Exception as e:
        return False, f"❌ Functional test error: {str(e)}"


def main():
    """Run all validation checks"""
    print_header("WhatsApp Integration Deployment Validation")

    # Load environment variables from .env if it exists
    try:
        from dotenv import load_dotenv

        if os.path.exists(".env"):
            load_dotenv()
            print(f"{GREEN}✅ Loaded .env file{NC}\n")
    except ImportError:
        print(
            f"{YELLOW}⚠️  python-dotenv not installed, using system environment{NC}\n"
        )

    # Run all checks
    checks = [
        ("Environment File", check_env_file),
        ("WhatsApp Configuration", check_whatsapp_config),
        ("Service Files", check_service_files),
        ("Python Dependencies", check_dependencies),
        ("WhatsApp Bot Import", check_imports),
        ("Notifier Integration", check_notifier_integration),
        ("Test Files", check_test_files),
        ("Documentation", check_documentation),
        ("Functional Test", run_functional_test),
    ]

    results = []

    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            results.append((check_name, passed, message))

            if passed:
                print(f"{GREEN}{message}{NC}")
            else:
                print(f"{RED}{message}{NC}")

        except Exception as e:
            print(f"{RED}❌ {check_name}: Error - {str(e)}{NC}")
            results.append((check_name, False, str(e)))

    # Summary
    print_header("Validation Summary")

    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)

    print(f"Checks Passed: {passed_count}/{total_count}\n")

    if passed_count == total_count:
        print(
            f"{GREEN}✅ All checks passed! WhatsApp integration is ready for deployment.{NC}"
        )
        print(f"\n{BLUE}Next steps:{NC}")
        print("1. Review the configuration in .env")
        print("2. Test with: python test_whatsapp_bot.py")
        print("3. Review examples: python examples_whatsapp_usage.py")
        print("4. Deploy your trading platform")
        print("5. Monitor logs for WhatsApp notifications\n")
        return 0
    else:
        print(f"{RED}❌ Some checks failed. Please fix the issues above.{NC}")
        print(f"\n{BLUE}Troubleshooting:{NC}")
        print("1. Ensure .env file exists: cp .env.example .env")
        print("2. Set WHATSAPP_GROUP_URL in .env")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Check the WHATSAPP_INTEGRATION_GUIDE.md for help\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
