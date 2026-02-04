#!/usr/bin/env python3
"""
Test Script for Gold Master EA Logic
Simulates the EA's decision-making process
"""

import csv
import os
from datetime import datetime


class GoldEASimulator:
    """
    A class to simulate and test the logic of the Gold Master Expert Advisor (EA).
    """

    def __init__(self):
        """
        Initializes the simulator with the EA's parameters.
        """
        self.base_risk = 1.0
        self.max_risk_per_trade = 5.0
        self.min_confidence = 75.0
        self.high_confidence = 85.0
        self.very_high_confidence = 90.0
        self.max_confidence_multiplier = 4.0

        self.gold_pairs = ["XAUUSD", "XAUEUR", "XAUGBP", "XAUAUD", "XAUCAD", "XAUCHF"]
        self.enabled_pairs = {
            "XAUUSD": True,
            "XAUEUR": True,
            "XAUGBP": True,
            "XAUAUD": True,
            "XAUCAD": False,
            "XAUCHF": False,
        }

    def is_gold_pair(self, symbol: str) -> bool:
        """
        Checks if a given symbol is a gold pair.

        Args:
            symbol (str): The symbol to check.

        Returns:
            bool: True if the symbol is a gold pair, False otherwise.
        """
        return symbol.startswith("XAU")

    def is_pair_enabled(self, symbol: str) -> bool:
        """
        Checks if a given trading pair is enabled in the EA's settings.

        Args:
            symbol (str): The symbol to check.

        Returns:
            bool: True if the pair is enabled, False otherwise.
        """
        return self.enabled_pairs.get(symbol, False)

    def calculate_confidence_risk(self, confidence: float) -> tuple:
        """
        Calculates the risk multiplier based on the signal's confidence level.

        Args:
            confidence (float): The confidence level of the signal (as a decimal).

        Returns:
            tuple: A tuple containing the calculated risk percentage and the multiplier used.
        """
        confidence = float(confidence) * 100  # Convert decimal to percentage

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

    def process_signals(self, csv_file: str) -> list:
        """
        Processes trading signals from a CSV file, simulating the EA's decision-making process.

        Args:
            csv_file (str): The path to the CSV file containing the signals.

        Returns:
            list: A list of dictionaries, where each dictionary represents a signal that would be processed.
        """
        results = []

        print("🥇 Gold Master EA Simulation Test")
        print("=" * 50)

        if not os.path.exists(csv_file):
            print(f"❌ Signal file not found: {csv_file}")
            return results

        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip header

            gold_signals = 0
            processed_signals = 0

            for row in reader:
                if len(row) < 8:
                    continue

                if len(row) >= 9:
                    (
                        magic,
                        symbol,
                        signal,
                        entry_price,
                        stop_loss,
                        take_profit,
                        lot_size,
                        confidence_val,
                        timestamp,
                    ) = row
                    # In standardized format, confidence is at index 7 (already percentage)
                    confidence = float(confidence_val) / 100.0
                else:
                    (
                        magic,
                        symbol,
                        signal,
                        entry_price,
                        stop_loss,
                        take_profit,
                        lot_size,
                        timestamp,
                    ) = row
                    # Fallback for 8-column format
                    confidence = float(lot_size)

                # Check if it's a gold pair
                if not self.is_gold_pair(symbol):
                    continue

                gold_signals += 1

                # Check if pair is enabled
                if not self.is_pair_enabled(symbol):
                    print(f"⏭️  {symbol} {signal} - SKIPPED (pair disabled)")
                    continue

                # Check confidence threshold
                confidence_pct = confidence * 100
                if confidence_pct < self.min_confidence:
                    print(
                        f"⏭️  {symbol} {signal} - SKIPPED (confidence {confidence_pct:.1f}% < {self.min_confidence}%)"
                    )
                    continue

                # Calculate risk
                risk_percent, multiplier = self.calculate_confidence_risk(confidence)

                print(f"🥇 {symbol} {signal}")
                print(
                    f"   💡 Confidence: {confidence_pct:.1f}% → Risk: {risk_percent:.1f}% (×{multiplier})"
                )
                print(
                    f"   💰 Entry: {entry_price} | SL: {stop_loss} | TP: {take_profit}"
                )
                print(f"   ✅ WOULD EXECUTE TRADE")
                print()

                results.append(
                    {
                        "symbol": symbol,
                        "signal": signal,
                        "confidence": confidence_pct,
                        "risk_percent": risk_percent,
                        "multiplier": multiplier,
                        "entry_price": float(entry_price),
                    }
                )

                processed_signals += 1

        print(f"📊 Test Summary:")
        print(f"   Total gold signals found: {gold_signals}")
        print(f"   Signals processed: {processed_signals}")
        print(f"   Signals executed: {len(results)}")
        print()

        return results

    def test_risk_scaling(self):
        """
        Tests the confidence-based risk scaling logic.
        """
        print("🎯 Risk Scaling Test")
        print("=" * 30)

        test_confidences = [0.72, 0.78, 0.82, 0.87, 0.92, 0.95]

        for conf in test_confidences:
            risk, mult = self.calculate_confidence_risk(conf)
            conf_pct = conf * 100
            print(f"Confidence {conf_pct:5.1f}% → Risk {risk:5.1f}% (×{mult:.1f})")
        print()


def main():
    """
    The main function to run the Gold EA simulation and tests.
    """
    simulator = GoldEASimulator()

    # Test 1: Risk scaling logic
    simulator.test_risk_scaling()

    # Test 2: Process actual signals
    csv_file = "signal_output/MT4_Signals.csv"
    results = simulator.process_signals(csv_file)

    # Test 3: Analyze results
    if results:
        print("📈 Analysis:")
        avg_confidence = sum(r["confidence"] for r in results) / len(results)
        avg_risk = sum(r["risk_percent"] for r in results) / len(results)

        print(f"   Average confidence: {avg_confidence:.1f}%")
        print(f"   Average risk: {avg_risk:.1f}%")

        high_conf_trades = [r for r in results if r["confidence"] >= 90]
        print(f"   High confidence trades (90%+): {len(high_conf_trades)}")

        if high_conf_trades:
            avg_high_risk = sum(r["risk_percent"] for r in high_conf_trades) / len(
                high_conf_trades
            )
            print(f"   Average risk for high confidence: {avg_high_risk:.1f}%")


if __name__ == "__main__":
    main()
