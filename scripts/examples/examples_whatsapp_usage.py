"""
Example: Using WhatsApp Bot in GenX Trading Platform

This example demonstrates how to integrate the WhatsApp bot with your trading signals.
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up environment (in production, use .env file)
os.environ["WHATSAPP_GROUP_URL"] = "https://chat.whatsapp.com/DYemXrBnMD63K55bjUMKYF"

from services.notifier import send_notification, send_signal, send_status_update


def example_send_trading_signal():
    """Example: Send a trading signal when AI generates one"""
    print("=" * 60)
    print("Example 1: Sending a Trading Signal")
    print("=" * 60)

    # This would typically come from your AI model
    signal = {
        "symbol": "XAUUSD",
        "action": "BUY",
        "entry": 2650.50,
        "target": 2680.00,
        "stop_loss": 2630.00,
        "confidence": 85,
        "timestamp": datetime.now().isoformat(),
        "status": "active",
    }

    # Send to all configured channels (Telegram, Discord, WhatsApp)
    results = send_signal(signal)

    print(f"\nSignal sent to channels: {results}")
    print("\n")


def example_system_startup_notification():
    """Example: Notify when the system starts"""
    print("=" * 60)
    print("Example 2: System Startup Notification")
    print("=" * 60)

    results = send_notification(
        title="🚀 System Started",
        message="GenX Trading Platform is now online and monitoring markets 24/7",
    )

    print(f"\nNotification sent to channels: {results}")
    print("\n")


def example_ai_model_status():
    """Example: Report AI model status"""
    print("=" * 60)
    print("Example 3: AI Model Status Update")
    print("=" * 60)

    results = send_status_update(
        service_name="Ensemble Predictor",
        status="online",
        details="All 5 models operational, average confidence: 87%",
    )

    print(f"\nStatus update sent to channels: {results}")
    print("\n")


def example_trade_execution_alert():
    """Example: Alert when a trade is executed"""
    print("=" * 60)
    print("Example 4: Trade Execution Alert")
    print("=" * 60)

    results = send_notification(
        title="✅ Trade Executed",
        message="BUY XAUUSD @ 2650.50\nLot Size: 0.1\nSL: 2630.00 | TP: 2680.00",
    )

    print(f"\nTrade alert sent to channels: {results}")
    print("\n")


def example_risk_warning():
    """Example: Send risk management warning"""
    print("=" * 60)
    print("Example 5: Risk Management Warning")
    print("=" * 60)

    results = send_notification(
        title="⚠️ Risk Alert",
        message="Daily loss limit approaching: 78% of max daily loss\nConsider reducing position sizes",
    )

    print(f"\nRisk warning sent to channels: {results}")
    print("\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("WhatsApp Bot Integration - Usage Examples")
    print("=" * 60 + "\n")

    examples = [
        example_send_trading_signal,
        example_system_startup_notification,
        example_ai_model_status,
        example_trade_execution_alert,
        example_risk_warning,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error running example: {e}\n")

    print("=" * 60)
    print("Integration Examples Complete")
    print("=" * 60)
    print("\n📚 For more information, see WHATSAPP_INTEGRATION_GUIDE.md\n")


if __name__ == "__main__":
    main()
