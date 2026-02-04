#!/usr/bin/env python3
"""
Test script for GenX FX Gold Signal Generator
"""

import json
import time
from datetime import datetime

import requests


def test_vps_connection() -> bool:
    """
    Tests the connection to the VPS.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    print("🔍 Testing VPS connection...")
    try:
        response = requests.get("http://34.71.143.222:8080/health", timeout=10)
        if response.status_code == 200:
            print("✅ VPS connection successful")
            return True
        else:
            print(f"⚠️ VPS responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ VPS connection failed: {e}")
        return False


def test_local_api() -> bool:
    """
    Tests the connection to the local API.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    print("🔍 Testing local API...")
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Local API connection successful")
            return True
        else:
            print(f"⚠️ Local API responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Local API connection failed: {e}")
        return False


def test_signal_generation() -> bool:
    """
    Tests the signal generation and submission process.

    Returns:
        bool: Always returns True after attempting the tests.
    """
    print("🔍 Testing signal generation...")

    # Test signal data
    test_signal = {
        "timestamp": datetime.now().isoformat(),
        "symbol": "XAUUSD",
        "action": "BUY",
        "entry_price": 2000.0,
        "stop_loss": 1990.0,
        "take_profit": 2020.0,
        "confidence": 85.0,
        "reasoning": "Test signal for verification",
        "source": "test",
    }

    # Save to CSV file (Standardized GenX Format - 9 Columns)
    magic = hash(f"{test_signal['symbol']}_{test_signal['timestamp']}") % 2147483647
    lot_size = round(test_signal["confidence"] / 1000.0, 2)
    if lot_size < 0.01:
        lot_size = 0.01

    confidence = test_signal["confidence"]

    csv_data = "Magic,Symbol,Signal,EntryPrice,StopLoss,TakeProfit,LotSize,Confidence,Timestamp\n"
    csv_data += f"{magic},{test_signal['symbol']},{test_signal['action']},"
    csv_data += f"{test_signal['entry_price']},{test_signal['stop_loss']},{test_signal['take_profit']},"
    csv_data += f"{lot_size},{confidence},{test_signal['timestamp']}\n"

    with open("MT4_Signals.csv", "w") as f:
        f.write(csv_data)

    print("✅ Test signal saved to MT4_Signals.csv")

    # Try to send to VPS
    try:
        response = requests.post(
            "http://34.71.143.222:8080/api/signals",
            json={"signals": [test_signal]},
            timeout=10,
        )
        if response.status_code == 200:
            print("✅ Test signal sent to VPS successfully")
        else:
            print(f"⚠️ VPS responded with status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to send to VPS: {e}")

    # Try to send to local API
    try:
        response = requests.post(
            "http://localhost:8080/api/v1/predictions",
            json={"signals": [test_signal]},
            timeout=5,
        )
        if response.status_code == 200:
            print("✅ Test signal sent to local API successfully")
        else:
            print(f"⚠️ Local API responded with status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to send to local API: {e}")

    return True


def main():
    """
    Runs all tests for the gold signal generator and prints a summary of the results.
    """
    print("🧪 GenX FX Gold Signal Generator Test")
    print("=" * 40)

    # Test VPS connection
    vps_ok = test_vps_connection()

    # Test local API
    local_ok = test_local_api()

    # Test signal generation
    signal_ok = test_signal_generation()

    print("\n📊 Test Results:")
    print(f"  • VPS Connection: {'✅' if vps_ok else '❌'}")
    print(f"  • Local API: {'✅' if local_ok else '❌'}")
    print(f"  • Signal Generation: {'✅' if signal_ok else '❌'}")

    if vps_ok and local_ok and signal_ok:
        print("\n🎉 All tests passed! System is ready for 24/7 operation.")
        print("\n🚀 To start the service:")
        print("   python gold-signal-generator.py")
        print("   or")
        print("   start-gold-signals.bat")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")

    print("\n📡 VPS Integration:")
    print("   • VPS URL: http://34.71.143.222:8080")
    print("   • Signal file: MT4_Signals.csv")
    print("   • EA can read from: http://34.71.143.222:8080/MT4_Signals.csv")


if __name__ == "__main__":
    main()
