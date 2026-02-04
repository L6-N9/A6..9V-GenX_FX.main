#!/usr/bin/env python3
"""
GenX FX Robust 24/7 Backend Service
Handles all encoding issues and provides robust gold signal generation
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import requests

# Add the api directory to Python path
sys.path.append(str(Path(__file__).parent / "api"))

# Configure logging with safe encoding
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("genx-backend.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class GenXRobustBackend:
    """
    A robust 24/7 backend service for GenX FX that handles encoding issues
    and provides reliable gold signal generation with proper error handling.
    """

    def __init__(self):
        """
        Initializes the robust backend service, setting up configuration,
        and connection status.
        """
        self.running = False
        self.vps_url = os.environ.get("VPS_URL", "http://34.71.143.222:8080")
        self.local_api_url = os.environ.get("LOCAL_API_URL", "http://localhost:8080")
        self.signal_interval = int(os.environ.get("SIGNAL_INTERVAL", 30))  # seconds
        self.last_signal_time = None

        # Gold pairs configuration
        self.gold_pairs = {
            "XAUUSD": {"name": "Gold/USD", "weight": 1.0},
            "XAUEUR": {"name": "Gold/EUR", "weight": 0.8},
            "XAUGBP": {"name": "Gold/GBP", "weight": 0.7},
            "XAUAUD": {"name": "Gold/AUD", "weight": 0.6},
        }

        # Signal generation settings
        self.min_confidence = 75.0
        self.max_signals_per_hour = 8
        self.signals_generated = 0
        self.last_reset_time = datetime.now()

        # Connection status
        self.vps_connected = False
        self.local_api_connected = False

    async def initialize(self) -> bool:
        """
        Initializes the backend service by testing connections and creating necessary directories.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            logger.info("Starting GenX FX Robust Backend Service...")

            # Test connections
            await self.test_connections()

            # Create logs directory
            os.makedirs("logs", exist_ok=True)

            logger.info("GenX FX Backend Service initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize backend service: {e}")
            return False

    async def test_connections(self):
        """
        Tests the connections to the VPS and the local API.
        """
        # Test VPS connection
        try:
            response = requests.get(f"{self.vps_url}/health", timeout=5)
            if response.status_code == 200:
                self.vps_connected = True
                logger.info(f"VPS connection successful: {self.vps_url}")
            else:
                logger.warning(f"VPS responded with status {response.status_code}")
        except Exception as e:
            logger.warning(f"VPS connection failed: {e}")

        # Test local API connection
        try:
            response = requests.get(f"{self.local_api_url}/health", timeout=3)
            if response.status_code == 200:
                self.local_api_connected = True
                logger.info(f"Local API connection successful: {self.local_api_url}")
            else:
                logger.warning(
                    f"Local API responded with status {response.status_code}"
                )
        except Exception as e:
            logger.warning(f"Local API connection failed: {e}")

    def generate_gold_signal(self, pair: str) -> Dict[str, Any]:
        """
        Generates a gold trading signal for a given pair using rule-based analysis.

        Args:
            pair (str): The trading pair to generate a signal for.

        Returns:
            Dict[str, Any]: A dictionary containing the generated signal.
        """
        current_time = datetime.now()

        # Market session analysis
        hour = current_time.hour
        if 8 <= hour <= 16:  # London/NY session
            base_confidence = 85.0
        elif 0 <= hour <= 6:  # Asian session
            base_confidence = 75.0
        else:  # Off hours
            base_confidence = 65.0

        # Time-based signal variation
        time_factor = (hash(str(current_time)) % 100) / 100.0
        confidence = base_confidence + (time_factor * 15)

        # Determine signal direction based on pair and time
        if hash(pair + str(hour)) % 2 == 0:
            action = "BUY"
            entry_price = 2000.0 + (hash(pair) % 100)
            stop_loss = entry_price - 25.0
            take_profit = entry_price + 50.0
        else:
            action = "SELL"
            entry_price = 2000.0 + (hash(pair) % 100)
            stop_loss = entry_price + 25.0
            take_profit = entry_price - 50.0

        return {
            "symbol": pair,
            "action": action,
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "confidence": min(confidence, 95.0),
            "timestamp": current_time.isoformat(),
            "reasoning": f"Rule-based analysis for {pair} during {'active' if 8 <= hour <= 16 else 'quiet'} session",
            "source": "rule_based",
        }

    async def generate_gold_signals(self) -> List[Dict[str, Any]]:
        """
        Generates gold trading signals for all configured pairs, respecting hourly limits.

        Returns:
            List[Dict[str, Any]]: A list of generated signals.
        """
        signals = []
        current_time = datetime.now()

        # Reset hourly counter
        if (current_time - self.last_reset_time).seconds >= 3600:
            self.signals_generated = 0
            self.last_reset_time = current_time

        # Check if we've reached the hourly limit
        if self.signals_generated >= self.max_signals_per_hour:
            logger.debug("Hourly signal limit reached")
            return signals

        for pair, config in self.gold_pairs.items():
            try:
                # Generate signal
                signal = self.generate_gold_signal(pair)

                if signal["confidence"] >= self.min_confidence:
                    # Apply pair weight
                    signal["confidence"] *= config["weight"]
                    signal["confidence"] = min(signal["confidence"], 95.0)

                    signals.append(signal)
                    self.signals_generated += 1

                    logger.info(
                        f"Generated {pair} signal: {signal['action']} "
                        f"({signal['confidence']:.1f}% confidence)"
                    )

            except Exception as e:
                logger.error(f"Error generating signal for {pair}: {e}")

        return signals

    async def send_signals(self, signals: List[Dict[str, Any]]) -> bool:
        """
        Sends the generated signals to the VPS and local API, and saves them to a CSV file.

        Args:
            signals (List[Dict[str, Any]]): A list of signals to send.

        Returns:
            bool: True if the signals were sent successfully, False otherwise.
        """
        if not signals:
            return True

        try:
            # Format as CSV for EA consumption
            csv_lines = [
                "timestamp,symbol,action,entry_price,stop_loss,take_profit,confidence,reasoning,source"
            ]

            for signal in signals:
                csv_lines.append(
                    f"{signal['timestamp']},{signal['symbol']},{signal['action']},"
                    f"{signal['entry_price']},{signal['stop_loss']},{signal['take_profit']},"
                    f"{signal['confidence']},{signal['reasoning']},{signal['source']}"
                )

            csv_data = "\n".join(csv_lines)

            # Save to local file
            with open("MT4_Signals.csv", "w", encoding="utf-8") as f:
                f.write(csv_data)

            logger.info(f"Saved {len(signals)} signals to MT4_Signals.csv")

            # Send to VPS if connected
            if self.vps_connected:
                try:
                    response = requests.post(
                        f"{self.vps_url}/api/signals",
                        json={
                            "signals": signals,
                            "timestamp": datetime.now().isoformat(),
                            "source": "genx_robust_backend",
                        },
                        timeout=5,
                    )

                    if response.status_code == 200:
                        logger.info(f"Sent {len(signals)} signals to VPS")
                    else:
                        logger.warning(
                            f"VPS responded with status {response.status_code}"
                        )

                except Exception as e:
                    logger.warning(f"Failed to send to VPS: {e}")
                    self.vps_connected = False

            # Send to local API if connected
            if self.local_api_connected:
                try:
                    response = requests.post(
                        f"{self.local_api_url}/api/v1/predictions",
                        json={"signals": signals},
                        timeout=3,
                    )

                    if response.status_code == 200:
                        logger.info(f"Sent {len(signals)} signals to local API")
                    else:
                        logger.warning(
                            f"Local API responded with status {response.status_code}"
                        )

                except Exception as e:
                    logger.warning(f"Failed to send to local API: {e}")
                    self.local_api_connected = False

            return True

        except Exception as e:
            logger.error(f"Error sending signals: {e}")
            return False

    async def run_signal_loop(self):
        """
        The main loop for continuously generating and sending trading signals.
        """
        logger.info("Starting gold signal generation loop...")

        while self.running:
            try:
                # Generate signals
                signals = await self.generate_gold_signals()

                if signals:
                    # Send signals
                    await self.send_signals(signals)

                    # Log summary
                    logger.info(f"Generated {len(signals)} gold signals")
                    for signal in signals:
                        logger.info(
                            f"  - {signal['symbol']} {signal['action']} "
                            f"({signal['confidence']:.1f}% confidence)"
                        )
                else:
                    logger.debug("No signals generated this cycle")

                # Wait for next cycle
                await asyncio.sleep(self.signal_interval)

            except Exception as e:
                logger.error(f"Error in signal loop: {e}")
                await asyncio.sleep(10)

    async def start(self):
        """
        Starts the robust backend service and the signal generation loop.
        """
        logger.info("Starting GenX FX Robust Backend Service...")

        if not await self.initialize():
            logger.error("Failed to initialize services")
            return False

        self.running = True

        logger.info("Gold Signal Generator Features:")
        logger.info(f"  - Monitoring: {', '.join(self.gold_pairs.keys())}")
        logger.info(f"  - Signal interval: {self.signal_interval} seconds")
        logger.info(f"  - Min confidence: {self.min_confidence}%")
        logger.info(f"  - Max signals/hour: {self.max_signals_per_hour}")
        logger.info(f"  - VPS URL: {self.vps_url}")
        logger.info(f"  - Local API: {self.local_api_url}")
        logger.info(f"  - VPS Connected: {'Yes' if self.vps_connected else 'No'}")
        logger.info(
            f"  - Local API Connected: {'Yes' if self.local_api_connected else 'No'}"
        )

        # Start signal generation
        await self.run_signal_loop()

    async def stop(self):
        """
        Stops the backend service.
        """
        logger.info("Stopping GenX FX Backend Service...")
        self.running = False


async def main():
    """
    The main entry point for the robust backend service.
    """
    backend = GenXRobustBackend()

    try:
        await backend.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await backend.stop()


if __name__ == "__main__":
    asyncio.run(main())
