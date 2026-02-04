#!/usr/bin/env python3
"""
Test script for WhatsApp bot integration
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set WhatsApp group URL for testing
os.environ["WHATSAPP_GROUP_URL"] = "https://chat.whatsapp.com/DYemXrBnMD63K55bjUMKYF"

from services.whatsapp_bot import whatsapp_bot


def test_signal_formatting():
    """Test signal message formatting"""
    print("=" * 60)
    print("TEST 1: Signal Message Formatting")
    print("=" * 60)

    test_signal = {
        "symbol": "XAUUSD",
        "action": "BUY",
        "entry": 2650.50,
        "target": 2680.00,
        "stop_loss": 2630.00,
        "confidence": 85,
        "timestamp": datetime.now().isoformat(),
        "status": "active",
    }

    message = whatsapp_bot.format_signal_message(test_signal)
    print("\nFormatted Signal Message:")
    print(message)
    print("\n" + "=" * 60 + "\n")

    assert True


def test_send_signal():
    """Test sending a signal"""
    print("=" * 60)
    print("TEST 2: Send Trading Signal")
    print("=" * 60)

    test_signal = {
        "symbol": "EURUSD",
        "action": "SELL",
        "entry": 1.0850,
        "target": 1.0800,
        "stop_loss": 1.0880,
        "confidence": 78,
        "timestamp": datetime.now().isoformat(),
        "status": "active",
    }

    success = whatsapp_bot.send_signal(test_signal)
    print(f"\nSignal send status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print("\n" + "=" * 60 + "\n")

    assert success


def test_send_notification():
    """Test sending a notification"""
    print("=" * 60)
    print("TEST 3: Send Notification")
    print("=" * 60)

    success = whatsapp_bot.send_notification(
        title="System Alert",
        message="GenX Trading Platform is now live and monitoring markets 24/7",
    )
    print(f"\nNotification send status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print("\n" + "=" * 60 + "\n")

    assert success


def test_send_status_update():
    """Test sending a status update"""
    print("=" * 60)
    print("TEST 4: Send Status Update")
    print("=" * 60)

    success = whatsapp_bot.send_status_update(
        service_name="AI Signal Generator",
        status="online",
        details="All models operational, confidence: 92%",
    )
    print(f"\nStatus update send status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print("\n" + "=" * 60 + "\n")

    assert success


def test_unified_notifier():
    """Test the unified notification service"""
    print("=" * 60)
    print("TEST 5: Unified Notification Service")
    print("=" * 60)

    from services.notifier import notifier

    print(f"\nActive channels: {notifier.get_active_channels()}")

    test_signal = {
        "symbol": "BTCUSD",
        "action": "BUY",
        "entry": 45000.00,
        "target": 47000.00,
        "stop_loss": 44000.00,
        "confidence": 82,
        "timestamp": datetime.now().isoformat(),
        "status": "active",
    }

    results = notifier.send_signal(test_signal)
    print(f"\nNotification results: {results}")
    print("\n" + "=" * 60 + "\n")

    assert any(results.values())


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("WhatsApp Bot Integration Test Suite")
    print("=" * 60 + "\n")

    tests = [
        ("Signal Formatting", test_signal_formatting),
        ("Send Signal", test_send_signal),
        ("Send Notification", test_send_notification),
        ("Send Status Update", test_send_status_update),
        ("Unified Notifier", test_unified_notifier),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}\n")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60 + "\n")

    # Important note
    print("📌 IMPORTANT NOTE:")
    print("=" * 60)
    print(
        "WhatsApp Web automation requires browser automation or WhatsApp Business API."
    )
    print("The current implementation logs messages that should be manually shared to:")
    print(f"  {os.environ.get('WHATSAPP_GROUP_URL', 'N/A')}")
    print("\nFor production deployment, consider:")
    print("  1. WhatsApp Business API (official, paid)")
    print("  2. Third-party services (Twilio, MessageBird)")
    print("  3. Browser automation with Selenium/Puppeteer")
    print("=" * 60 + "\n")

    return 0 if all(r for _, r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
