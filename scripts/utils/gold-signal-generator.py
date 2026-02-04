#!/usr/bin/env python3
"""
GenX FX Gold Signal Generator
Specialized service for generating gold trading signals and sending to VPS
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import requests

# Add the api directory to Python path
sys.path.append(str(Path(__file__).parent / "api"))

try:
    from api.services.gemini_service import GeminiService

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("gold-signals.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class GoldSignalGenerator:
    """
    A specialized service for generating gold trading signals, with integration
    for sending them to a VPS. It can use either AI-based or rule-based analysis.
    """

    def __init__(self):
        """
        Initializes the GoldSignalGenerator, setting up configuration for VPS,
        API, gold pairs, and signal generation.
        """
        self.vps_url = "http://34.71.143.222:8080"
        self.local_api_url = "http://localhost:8080"
        self.gemini_service = None
        self.running = False

        # Gold pairs configuration
        self.gold_pairs = {
            "XAUUSD": {"name": "Gold/USD", "weight": 1.0},
            "XAUEUR": {"name": "Gold/EUR", "weight": 0.8},
            "XAUGBP": {"name": "Gold/GBP", "weight": 0.7},
            "XAUAUD": {"name": "Gold/AUD", "weight": 0.6},
        }

        # Signal generation settings
        self.signal_interval = 30  # seconds
        self.min_confidence = 75.0
        self.max_signals_per_hour = 8
        self.signals_generated = 0
        self.last_reset_time = datetime.now()

        # Initialize Gemini AI if available
        if GEMINI_AVAILABLE:
            try:
                self.gemini_service = GeminiService()
                logger.info("✅ Gemini AI service initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini AI not available: {e}")
                self.gemini_service = None
        else:
            logger.warning("⚠️ Gemini AI not available, using rule-based signals")

    async def initialize(self) -> bool:
        """
        Initializes the signal generator, including the Gemini service and
        connections to the VPS and local API.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            if self.gemini_service:
                await self.gemini_service.initialize()
                logger.info("✅ Gemini AI service ready")

            # Test VPS connection
            await self.test_vps_connection()

            # Test local API
            await self.test_local_api()

            logger.info("🎉 Gold Signal Generator initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize: {e}")
            return False

    async def test_vps_connection(self) -> bool:
        """
        Tests the connection to the VPS.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            response = requests.get(f"{self.vps_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ VPS connection successful: {self.vps_url}")
                return True
            else:
                logger.warning(f"⚠️ VPS responded with status {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ VPS connection failed: {e}")
            return False

    async def test_local_api(self) -> bool:
        """
        Tests the connection to the local API.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            response = requests.get(f"{self.local_api_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Local API connection successful: {self.local_api_url}")
                return True
            else:
                logger.warning(
                    f"⚠️ Local API responded with status {response.status_code}"
                )
                return False
        except Exception as e:
            logger.warning(f"⚠️ Local API connection failed: {e}")
            return False

    def generate_rule_based_signal(self, pair: str) -> Dict[str, Any]:
        """
        Generates a signal using rule-based analysis.

        Args:
            pair (str): The trading pair to generate a signal for.

        Returns:
            Dict[str, Any]: A dictionary containing the generated signal.
        """
        current_time = datetime.now()

        # Simple rule-based logic
        hour = current_time.hour
        minute = current_time.minute

        # Market session analysis
        if 8 <= hour <= 16:  # London/NY session
            base_confidence = 80.0
        elif 0 <= hour <= 6:  # Asian session
            base_confidence = 70.0
        else:  # Off hours
            base_confidence = 60.0

        # Time-based signal variation
        time_factor = (hash(str(current_time)) % 100) / 100.0
        confidence = base_confidence + (time_factor * 20)

        # Determine signal direction
        if hash(pair + str(hour)) % 2 == 0:
            action = "BUY"
            entry_price = 2000.0 + (hash(pair) % 100)
            stop_loss = entry_price - 20.0
            take_profit = entry_price + 40.0
        else:
            action = "SELL"
            entry_price = 2000.0 + (hash(pair) % 100)
            stop_loss = entry_price + 20.0
            take_profit = entry_price - 40.0

        return {
            "symbol": pair,
            "action": action,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "confidence": min(confidence, 95.0),
            "timestamp": current_time.isoformat(),
            "reasoning": f"Rule-based analysis for {pair} during {'active' if 8 <= hour <= 16 else 'quiet'} session",
            "source": "rule_based",
        }

    async def generate_ai_signal(self, pair: str) -> Dict[str, Any]:
        """
        Generates a signal using AI analysis from the Gemini service.

        Args:
            pair (str): The trading pair to generate a signal for.

        Returns:
            Dict[str, Any]: A dictionary containing the AI-generated signal,
                           or a rule-based signal as a fallback.
        """
        if not self.gemini_service:
            return self.generate_rule_based_signal(pair)

        try:
            # Mock market data
            market_data = {
                "symbol": pair,
                "price": 2000.0 + (hash(pair) % 100),
                "volume": 1000 + (hash(pair) % 500),
                "indicators": {
                    "rsi": 30 + (hash(pair) % 40),
                    "macd": -0.5 + (hash(pair) % 10) / 10,
                    "ma_20": 2000.0 + (hash(pair) % 50),
                    "ma_50": 1995.0 + (hash(pair) % 30),
                },
            }

            # Mock news data
            news_data = [
                f"Gold market analysis for {pair}",
                "Federal Reserve monetary policy update",
                "Inflation data shows mixed signals",
                "Geopolitical tensions affecting precious metals",
                "Dollar strength impacting gold prices",
            ]

            # Generate signal using Gemini AI
            signal_analysis = await self.gemini_service.analyze_trading_signals(
                market_data, news_data
            )

            if signal_analysis.get("signal_strength", 0) > 0.5:
                return {
                    "symbol": pair,
                    "action": signal_analysis.get("direction", "HOLD").upper(),
                    "entry_price": signal_analysis.get(
                        "entry_price", market_data["price"]
                    ),
                    "stop_loss": signal_analysis.get("stop_loss", 0),
                    "take_profit": signal_analysis.get("take_profit", 0),
                    "confidence": signal_analysis.get("signal_strength", 0) * 100,
                    "timestamp": datetime.now().isoformat(),
                    "reasoning": signal_analysis.get("reasoning", "AI analysis"),
                    "source": "ai_gemini",
                }
            else:
                return None

        except Exception as e:
            logger.error(f"❌ AI signal generation failed for {pair}: {e}")
            return self.generate_rule_based_signal(pair)

    async def generate_gold_signals(self) -> List[Dict[str, Any]]:
        """
        Generates gold trading signals, respecting hourly limits and using a mix
        of AI and rule-based methods.

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
            logger.debug("⚠️ Hourly signal limit reached")
            return signals

        for pair, config in self.gold_pairs.items():
            try:
                # Generate signal using AI or rule-based method
                if self.gemini_service and hash(pair + str(current_time)) % 3 == 0:
                    signal = await self.generate_ai_signal(pair)
                else:
                    signal = self.generate_rule_based_signal(pair)

                if signal and signal["confidence"] >= self.min_confidence:
                    # Apply pair weight
                    signal["confidence"] *= config["weight"]
                    signal["confidence"] = min(signal["confidence"], 95.0)

                    signals.append(signal)
                    self.signals_generated += 1

                    logger.info(
                        f"📊 Generated {pair} signal: {signal['action']} "
                        f"({signal['confidence']:.1f}% confidence)"
                    )

            except Exception as e:
                logger.error(f"❌ Error generating signal for {pair}: {e}")

        return signals

    async def send_to_vps(self, signals: List[Dict[str, Any]]) -> bool:
        """
        Sends generated signals to the VPS and local API, and saves them to a CSV file.

        Args:
            signals (List[Dict[str, Any]]): A list of signals to send.

        Returns:
            bool: True if the signals were sent successfully, False otherwise.
        """
        if not signals:
            return True

        try:
            # Format as CSV for EA consumption (Standardized GenX Format - 9 Columns)
            csv_lines = [
                "Magic,Symbol,Signal,EntryPrice,StopLoss,TakeProfit,LotSize,Confidence,Timestamp"
            ]

            for signal in signals:
                magic = hash(f"{signal['symbol']}_{signal['timestamp']}") % 2147483647
                # Use confidence as a proxy for lot size if not specified
                lot_size = round(
                    signal.get("lot_size", signal["confidence"] / 1000.0), 2
                )
                if lot_size < 0.01:
                    lot_size = 0.01

                confidence = round(signal["confidence"], 2)

                csv_lines.append(
                    f"{magic},{signal['symbol']},{signal['action']},"
                    f"{signal['entry_price']},{signal['stop_loss']},{signal['take_profit']},"
                    f"{lot_size},{confidence},{signal['timestamp']}"
                )

            csv_data = "\n".join(csv_lines)

            # Save to local file
            with open("MT4_Signals.csv", "w") as f:
                f.write(csv_data)

            # Send to VPS
            try:
                response = requests.post(
                    f"{self.vps_url}/api/signals",
                    json={
                        "signals": signals,
                        "timestamp": datetime.now().isoformat(),
                        "source": "genx_gold_generator",
                    },
                    timeout=10,
                )

                if response.status_code == 200:
                    logger.info(f"✅ Sent {len(signals)} signals to VPS")
                    return True
                else:
                    logger.warning(
                        f"⚠️ VPS responded with status {response.status_code}"
                    )

            except Exception as e:
                logger.warning(f"⚠️ Failed to send to VPS: {e}")

            # Send to local API
            try:
                response = requests.post(
                    f"{self.local_api_url}/api/v1/predictions",
                    json={"signals": signals},
                    timeout=5,
                )

                if response.status_code == 200:
                    logger.info(f"✅ Sent {len(signals)} signals to local API")
                else:
                    logger.warning(
                        f"⚠️ Local API responded with status {response.status_code}"
                    )

            except Exception as e:
                logger.warning(f"⚠️ Failed to send to local API: {e}")

            return True

        except Exception as e:
            logger.error(f"❌ Error sending signals: {e}")
            return False

    async def run_signal_loop(self):
        """
        The main loop for continuously generating and sending trading signals.
        """
        logger.info("🔄 Starting gold signal generation loop...")

        while self.running:
            try:
                # Generate signals
                signals = await self.generate_gold_signals()

                if signals:
                    # Send to VPS and local API
                    await self.send_to_vps(signals)

                    # Log summary
                    logger.info(f"📊 Generated {len(signals)} gold signals")
                    for signal in signals:
                        logger.info(
                            f"  • {signal['symbol']} {signal['action']} "
                            f"({signal['confidence']:.1f}% confidence) - {signal['source']}"
                        )
                else:
                    logger.debug("No signals generated this cycle")

                # Wait for next cycle
                await asyncio.sleep(self.signal_interval)

            except Exception as e:
                logger.error(f"❌ Error in signal loop: {e}")
                await asyncio.sleep(10)

    async def start(self):
        """
        Starts the gold signal generator and its main loop.
        """
        logger.info("🚀 Starting GenX Gold Signal Generator...")

        if not await self.initialize():
            logger.error("❌ Failed to initialize")
            return False

        self.running = True

        logger.info("📊 Gold Signal Generator Features:")
        logger.info(f"  • Monitoring: {', '.join(self.gold_pairs.keys())}")
        logger.info(f"  • Signal interval: {self.signal_interval} seconds")
        logger.info(f"  • Min confidence: {self.min_confidence}%")
        logger.info(f"  • Max signals/hour: {self.max_signals_per_hour}")
        logger.info(f"  • VPS URL: {self.vps_url}")
        logger.info(f"  • Local API: {self.local_api_url}")
        logger.info(
            "  • AI Analysis: "
            + ("✅ Available" if self.gemini_service else "❌ Not available")
        )

        # Start signal generation
        await self.run_signal_loop()

    async def stop(self):
        """
        Stops the signal generator and shuts down its services.
        """
        logger.info("🛑 Stopping Gold Signal Generator...")
        self.running = False

        if self.gemini_service:
            await self.gemini_service.shutdown()


async def main():
    """
    The main entry point for the gold signal generator service.
    """
    generator = GoldSignalGenerator()

    try:
        await generator.start()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        await generator.stop()


if __name__ == "__main__":
    asyncio.run(main())
