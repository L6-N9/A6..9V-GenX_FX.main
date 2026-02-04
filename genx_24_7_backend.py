#!/usr/bin/env python3
"""
GenX FX 24/7 Backend Service
Runs the trading backend continuously with gold signal generation and VPS communication
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import requests

# Add the api directory to Python path
sys.path.append(str(Path(__file__).parent / "api"))

import uvicorn

from api.main import app
from api.services.ea_communication import EAServer, TradingSignal
from api.services.gemini_service import GeminiService
from api.services.trading_service import TradingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("genx-24-7.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class GenX24_7Backend:
    """
    The main class for the GenX FX 24/7 backend service, responsible for
    running the trading backend continuously, generating gold signals, and
    communicating with the VPS and EAs.
    """

    def __init__(self):
        """
        Initializes the GenX24_7Backend service.
        """
        self.running = False
        self.vps_url = os.environ.get("VPS_URL", "http://34.71.143.222:8080")
        self.gemini_service = None
        self.trading_service = None
        self.ea_server = None
        self.monitor_process = None
        self.signal_interval = 30  # Generate signals every 30 seconds
        self.last_signal_time = None

        # Gold pairs to monitor
        self.gold_pairs = ["XAUUSD", "XAUEUR", "XAUGBP", "XAUAUD"]

        # Signal generation settings
        self.min_confidence = 75.0
        self.max_signals_per_hour = 10

    async def initialize(self) -> bool:
        """
        Initializes all necessary services for the backend, including the
        Gemini AI service, trading service, and EA communication server.

        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            logger.info("🚀 Initializing GenX 24/7 Backend Service...")

            # Initialize Gemini AI service
            try:
                self.gemini_service = GeminiService()
                await self.gemini_service.initialize()
                logger.info("✅ Gemini AI service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini service: {e}")
                self.gemini_service = None

            # Initialize trading service
            self.trading_service = TradingService()
            await self.trading_service.initialize()
            logger.info("✅ Trading service initialized")

            # Initialize EA communication server
            self.ea_server = EAServer(host="0.0.0.0", port=9090)
            await self.ea_server.start()
            logger.info("✅ EA communication server started on port 9090")

            # Test VPS connection
            await self.test_vps_connection()

            logger.info("🎉 GenX 24/7 Backend Service initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize backend service: {e}")
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

    async def generate_gold_signals(self) -> List[Dict[str, Any]]:
        """
        Generates gold trading signals using the Gemini AI service.
        Falls back to mock signals if the AI service is unavailable.

        Returns:
            List[Dict[str, Any]]: A list of generated signals.
        """
        signals = []

        if not self.gemini_service:
            logger.warning("⚠️ Gemini service not available, using mock signals")
            return self.generate_mock_signals()

        try:
            for pair in self.gold_pairs:
                # Get market data (mock for now)
                market_data = {
                    "symbol": pair,
                    "price": 2000.0 + (hash(pair) % 100),  # Mock price
                    "volume": 1000,
                    "indicators": {
                        "rsi": 50 + (hash(pair) % 20),
                        "macd": 0.1,
                        "ma_20": 2000.0,
                    },
                }

                # Mock news data
                news_data = [
                    f"Gold market analysis for {pair}",
                    "Federal Reserve interest rate decision",
                    "Inflation data release",
                    "Geopolitical tensions affecting precious metals",
                ]

                # Generate signal using Gemini AI
                signal_analysis = await self.gemini_service.analyze_trading_signals(
                    market_data, news_data
                )

                if signal_analysis.get("signal_strength", 0) > 0.5:
                    signal = {
                        "symbol": pair,
                        "action": signal_analysis.get("direction", "HOLD").upper(),
                        "entry_price": signal_analysis.get(
                            "entry_price", market_data["price"]
                        ),
                        "stop_loss": signal_analysis.get("stop_loss", 0),
                        "take_profit": signal_analysis.get("take_profit", 0),
                        "confidence": signal_analysis.get("signal_strength", 0) * 100,
                        "timestamp": datetime.now().isoformat(),
                        "reasoning": signal_analysis.get("reasoning", ""),
                    }

                    if signal["confidence"] >= self.min_confidence:
                        signals.append(signal)
                        logger.info(
                            f"📊 Generated signal: {pair} {signal['action']} "
                            f"Confidence: {signal['confidence']:.1f}%"
                        )

        except Exception as e:
            logger.error(f"❌ Error generating signals: {e}")
            return self.generate_mock_signals()

        return signals

    def generate_mock_signals(self) -> List[Dict[str, Any]]:
        """
        Generates mock signals when the AI service is unavailable.

        Returns:
            List[Dict[str, Any]]: A list containing a single mock signal.
        """
        signals = []
        current_time = datetime.now()

        # Generate a mock signal every few minutes
        if (
            not self.last_signal_time
            or (current_time - self.last_signal_time).seconds > 300
        ):

            pair = self.gold_pairs[hash(str(current_time)) % len(self.gold_pairs)]
            action = "BUY" if hash(str(current_time)) % 2 == 0 else "SELL"

            signal = {
                "symbol": pair,
                "action": action,
                "entry_price": 2000.0 + (hash(str(current_time)) % 100),
                "stop_loss": 1990.0 + (hash(str(current_time)) % 50),
                "take_profit": 2010.0 + (hash(str(current_time)) % 100),
                "confidence": 80.0 + (hash(str(current_time)) % 15),
                "timestamp": current_time.isoformat(),
                "reasoning": "Mock signal for testing",
            }

            signals.append(signal)
            self.last_signal_time = current_time
            logger.info(f"📊 Generated mock signal: {pair} {action}")

        return signals

    async def send_signals_to_vps(self, signals: List[Dict[str, Any]]) -> bool:
        """
        Sends generated signals to the VPS and broadcasts them to connected EAs.

        Args:
            signals (List[Dict[str, Any]]): A list of signals to send.

        Returns:
            bool: True if the signals were sent successfully, False otherwise.
        """
        if not signals:
            return True

        try:
            # Format signals for CSV output
            csv_data = "timestamp,symbol,action,entry_price,stop_loss,take_profit,confidence,reasoning\n"

            for signal in signals:
                csv_data += (
                    f"{signal['timestamp']},{signal['symbol']},{signal['action']},"
                )
                csv_data += f"{signal['entry_price']},{signal['stop_loss']},{signal['take_profit']},"
                csv_data += f"{signal['confidence']},{signal['reasoning']}\n"

            # Save to local file (for EA to read)
            with open("MT4_Signals.csv", "w") as f:
                f.write(csv_data)

            # Send to VPS (if available)
            try:
                response = requests.post(
                    f"{self.vps_url}/api/signals", json={"signals": signals}, timeout=10
                )
                if response.status_code == 200:
                    logger.info(f"✅ Sent {len(signals)} signals to VPS")
                else:
                    logger.warning(
                        f"⚠️ VPS responded with status {response.status_code}"
                    )
            except Exception as e:
                logger.warning(f"⚠️ Failed to send to VPS: {e}")

            # Send to local EA server
            for signal in signals:
                trading_signal = TradingSignal(
                    signal_id=f"genx_{int(time.time())}_{signal['symbol']}",
                    instrument=signal["symbol"],
                    action=signal["action"],
                    volume=0.01,  # Default lot size
                    stop_loss=signal["stop_loss"],
                    take_profit=signal["take_profit"],
                    comment=f"GenX AI {signal['confidence']:.1f}%",
                    confidence=signal["confidence"],
                )

                await self.ea_server.broadcast_signal(trading_signal)

            logger.info(f"📡 Broadcasted {len(signals)} signals to EAs")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending signals: {e}")
            return False

    async def run_signal_generation_loop(self):
        """
        The main loop for continuously generating and sending trading signals.
        """
        logger.info("🔄 Starting signal generation loop...")

        while self.running:
            try:
                # Generate signals
                signals = await self.generate_gold_signals()

                if signals:
                    # Send signals to VPS and EAs
                    await self.send_signals_to_vps(signals)

                    # Log signal summary
                    logger.info(f"📊 Generated {len(signals)} gold signals")
                    for signal in signals:
                        logger.info(
                            f"  • {signal['symbol']} {signal['action']} "
                            f"({signal['confidence']:.1f}% confidence)"
                        )
                else:
                    logger.debug("No signals generated this cycle")

                # Wait for next cycle
                await asyncio.sleep(self.signal_interval)

            except Exception as e:
                logger.error(f"❌ Error in signal generation loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying

    async def start(self):
        """
        Starts the 24/7 backend service, including the signal generation loop
        and the FastAPI server.
        """
        logger.info("🚀 Starting GenX 24/7 Backend Service...")

        # Initialize services
        if not await self.initialize():
            logger.error("❌ Failed to initialize services")
            return False

        self.running = True

        # Start monitor
        monitor_path = (
            Path(__file__).parent / "scripts" / "maintenance" / "system_monitor.py"
        )
        if not monitor_path.exists():
            # Fallback for different execution contexts
            monitor_path = Path("scripts/maintenance/system_monitor.py")

        self.monitor_process = subprocess.Popen([sys.executable, str(monitor_path)])
        logger.info(
            f"📊 Monitoring process started with PID: {self.monitor_process.pid}"
        )

        # Start signal generation in background
        signal_task = asyncio.create_task(self.run_signal_generation_loop())

        # Start FastAPI server
        config = uvicorn.Config(
            app=app, host="0.0.0.0", port=8080, log_level="info", access_log=True
        )
        server = uvicorn.Server(config)

        logger.info("🌐 Starting FastAPI server on http://0.0.0.0:8080")
        logger.info("📊 Signal generation active")
        logger.info("🔗 EA communication server on port 9090")
        logger.info(f"📡 VPS communication: {self.vps_url}")

        try:
            # Run both the server and signal generation
            await asyncio.gather(server.serve(), signal_task)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested")
        finally:
            await self.stop()

    async def stop(self):
        """
        Stops the 24/7 backend service gracefully, shutting down all running services.
        """
        logger.info("🛑 Stopping GenX 24/7 Backend Service...")

        self.running = False

        if self.monitor_process:
            self.monitor_process.terminate()
            logger.info("📊 Monitoring process terminated")

        if self.ea_server:
            await self.ea_server.stop()

        if self.gemini_service:
            await self.gemini_service.shutdown()

        logger.info("✅ GenX 24/7 Backend Service stopped")


def signal_handler(signum, frame):
    """
    Handles shutdown signals (SIGINT, SIGTERM) to ensure graceful shutdown.
    """
    logger.info(f"🛑 Received signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """
    The main entry point for the backend service.
    """
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start the backend service
    backend = GenX24_7Backend()
    await backend.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
