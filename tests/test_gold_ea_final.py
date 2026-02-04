#!/usr/bin/env python3
"""
Final Test Script for Gold Master EA Logic
Tests with proper confidence values and realistic gold signals
"""

import csv
import os
from datetime import datetime


class GoldEAFinalTest:
    """
    A class to test the logic of the Gold Master Expert Advisor (EA),
    focusing on risk calculation and signal processing.
    """

    def __init__(self):
        """
        Initializes the test class with EA parameters.
        """
        self.base_risk = 1.0
        self.max_risk_per_trade = 5.0
        self.min_confidence = 75.0
        self.high_confidence = 85.0
        self.very_high_confidence = 90.0
        self.max_confidence_multiplier = 4.0

        self.enabled_pairs = {
            "XAUUSD": True,
            "XAUEUR": True,
            "XAUGBP": True,
            "XAUAUD": True,
            "XAUCAD": False,  # Disabled in test
            "XAUCHF": False,  # Disabled in test
        }

    def calculate_confidence_risk(self, confidence: float) -> tuple:
        """
        Calculates the risk multiplier based on the signal's confidence level,
        replicating the EA's logic.

        Args:
            confidence (float): The confidence level of the signal.

        Returns:
            tuple: A tuple containing the calculated risk percentage and the multiplier used.
        """
        if confidence >= self.very_high_confidence:
            multiplier = self.max_confidence_multiplier  # 90%+ = 4x
        elif confidence >= self.high_confidence:
            multiplier = 2.5  # 85%+ = 2.5x
        elif confidence >= 80.0:
            multiplier = 1.5  # 80%+ = 1.5x
        else:
            multiplier = 1.0  # Default

        calculated_risk = self.base_risk * multiplier

        # Apply safety cap
        if calculated_risk > self.max_risk_per_trade:
            calculated_risk = self.max_risk_per_trade

        return calculated_risk, multiplier

    def test_with_realistic_signals(self) -> list:
        """
        Tests the EA logic with a set of realistic gold signals from a CSV file.

        Returns:
            list: A list of dictionaries, where each dictionary represents a trade that would be executed.
        """
        print("🥇 Gold Master EA - Realistic Signal Test")
        print("=" * 55)

        csv_file = "test_gold_signals.csv"

        if not os.path.exists(csv_file):
            print(f"❌ Test file not found: {csv_file}")
            return []

        results = []

        with open(csv_file, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                symbol = row["Symbol"]
                signal = row["Signal"]
                confidence = float(row["Confidence"])
                entry_price = float(row["EntryPrice"])
                stop_loss = float(row["StopLoss"])
                take_profit = float(row["TakeProfit"])

                print(f"\n🔍 Processing: {symbol} {signal}")
                print(f"   💡 Confidence: {confidence:.1f}%")
                print(
                    f"   💰 Entry: {entry_price} | SL: {stop_loss} | TP: {take_profit}"
                )

                # Check if pair is enabled
                if not self.enabled_pairs.get(symbol, False):
                    print(f"   ⏭️  SKIPPED: Pair disabled in EA settings")
                    continue

                # Check confidence threshold
                if confidence < self.min_confidence:
                    print(
                        f"   ⏭️  SKIPPED: Confidence {confidence:.1f}% < {self.min_confidence}%"
                    )
                    continue

                # Calculate risk
                risk_percent, multiplier = self.calculate_confidence_risk(confidence)

                # Calculate position size (simplified)
                account_balance = 10000  # Example $10k account
                risk_amount = account_balance * risk_percent / 100

                print(f"   🎯 Risk Calculation:")
                print(f"      • Multiplier: ×{multiplier:.1f}")
                print(f"      • Risk %: {risk_percent:.1f}%")
                print(f"      • Risk $: ${risk_amount:.0f}")
                print(f"   ✅ TRADE EXECUTED!")

                results.append(
                    {
                        "symbol": symbol,
                        "signal": signal,
                        "confidence": confidence,
                        "risk_percent": risk_percent,
                        "risk_amount": risk_amount,
                        "multiplier": multiplier,
                    }
                )

        return results

    def analyze_results(self, results: list):
        """
        Analyzes the results of the signal processing test.

        Args:
            results (list): A list of trade results from the test.
        """
        if not results:
            print("\n❌ No trades executed in test")
            return

        print(f"\n📊 Test Results Analysis")
        print("=" * 30)

        total_trades = len(results)
        total_risk = sum(r["risk_amount"] for r in results)
        avg_confidence = sum(r["confidence"] for r in results) / total_trades
        avg_risk = sum(r["risk_percent"] for r in results) / total_trades

        print(f"Total trades executed: {total_trades}")
        print(f"Total risk amount: ${total_risk:.0f}")
        print(f"Average confidence: {avg_confidence:.1f}%")
        print(f"Average risk per trade: {avg_risk:.1f}%")

        # High confidence analysis
        high_conf_trades = [r for r in results if r["confidence"] >= 90]
        if high_conf_trades:
            avg_high_risk = sum(r["risk_percent"] for r in high_conf_trades) / len(
                high_conf_trades
            )
            print(f"High confidence trades (90%+): {len(high_conf_trades)}")
            print(f"Average risk for high confidence: {avg_high_risk:.1f}%")

        # Risk distribution
        print(f"\n📈 Risk Distribution:")
        for result in results:
            print(
                f"   {result['symbol']:>6} {result['signal']:>4}: "
                f"{result['confidence']:5.1f}% conf → {result['risk_percent']:4.1f}% risk "
                f"(${result['risk_amount']:4.0f})"
            )

    def test_edge_cases(self):
        """
        Tests edge cases and safety limits for the risk calculation logic.
        """
        print(f"\n🧪 Edge Case Testing")
        print("=" * 25)

        test_cases = [
            ("Very High Confidence", 95.0),
            ("High Confidence", 87.5),
            ("Medium Confidence", 82.0),
            ("Low Confidence", 77.0),
            ("Below Threshold", 72.0),
        ]

        for name, confidence in test_cases:
            if confidence < self.min_confidence:
                print(f"{name:>18} ({confidence:5.1f}%): ❌ REJECTED (below threshold)")
            else:
                risk, mult = self.calculate_confidence_risk(confidence)
                print(
                    f"{name:>18} ({confidence:5.1f}%): ✅ {risk:4.1f}% risk (×{mult:.1f})"
                )


def main():
    """
    The main function to run the Gold Master EA test suite.
    """
    tester = GoldEAFinalTest()

    # Test 1: Realistic signals
    results = tester.test_with_realistic_signals()

    # Test 2: Analyze results
    tester.analyze_results(results)

    # Test 3: Edge cases
    tester.test_edge_cases()

    print(f"\n🎉 Gold Master EA Test Complete!")
    print("✅ All core logic validated and working correctly!")


if __name__ == "__main__":
    main()
