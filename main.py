#!/usr/bin/env python3
"""
GenX FX Trading System - Main Entry Point
Advanced AI-powered Forex trading signal generator for MT4/5 EAs
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.ai_models.ensemble_predictor import EnsemblePredictor
from core.backtester import Backtester
from core.data_sources.fxcm_provider import FXCMDataProvider, MockFXCMProvider
from core.model_trainer import ModelTrainer
from core.trading_engine import TradingEngine
from utils.config_manager import ConfigManager
from utils.logger_setup import setup_logging

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """
    A simple HTTP request handler for responding to health checks,
    primarily for use with services like Cloud Run.
    """

    def do_GET(self):
        """
        Handles GET requests. Responds with a 200 OK status for the /health path.
        """
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "genx-trading-system"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """
        Suppresses the default logging of HTTP requests.
        """
        # Suppress default HTTP server logs
        pass


class GenXTradingSystem:
    """
    The main controller for the GenX Trading System. This class orchestrates
    the different modes of operation, including live trading, model training,
    backtesting, and system tests.
    """

    def __init__(self, config_path: str = "config/trading_config.json"):
        """
        Initializes the GenXTradingSystem.

        Args:
            config_path (str, optional): The path to the configuration file.
                                         Defaults to "config/trading_config.json".
        """
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        self.trading_engine = None
        self.is_running = False
        self.health_server = None

        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("GenX Trading System initialized")

    def _signal_handler(self, signum, frame):
        """
        Handles shutdown signals gracefully to ensure a clean exit.
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.is_running = False
        if self.health_server:
            self.health_server.shutdown()

    def start_health_server(self, port=8080):
        """
        Starts a simple health check server in a separate thread.

        Args:
            port (int, optional): The port for the health check server. Defaults to 8080.
        """
        try:
            self.health_server = HTTPServer(("", port), HealthCheckHandler)
            health_thread = Thread(target=self.health_server.serve_forever, daemon=True)
            health_thread.start()
            logger.info(f"Health check server started on port {port}")
        except Exception as e:
            logger.warning(f"Could not start health server: {e}")

    async def run_live_trading(self):
        """
        Runs the system in live trading mode, generating signals continuously.
        """
        logger.info("🚀 Starting Live Trading Mode")

        try:
            # Initialize trading engine
            self.trading_engine = TradingEngine(self.config)

            # Start the engine
            await self.trading_engine.start()
            self.is_running = True

            logger.info("✅ Live trading started successfully")
            logger.info("📊 Signals will be output to: signal_output/")
            logger.info("📈 MT4 signals: signal_output/MT4_Signals.csv")
            logger.info("📈 MT5 signals: signal_output/MT5_Signals.csv")
            logger.info("📊 Excel dashboard: signal_output/genx_signals.xlsx")

            # Keep running until shutdown
            while self.is_running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Error in live trading mode: {e}")
        finally:
            if self.trading_engine:
                await self.trading_engine.stop()
            logger.info("Live trading stopped")

    async def run_training_mode(self, symbols: list = None, timeframes: list = None):
        """
        Runs the system in AI model training mode.

        Args:
            symbols (list, optional): A list of symbols to train models for. Defaults to None.
            timeframes (list, optional): A list of timeframes to use for training. Defaults to None.
        """
        logger.info("🎯 Starting Training Mode")

        try:
            trainer = ModelTrainer(self.config)
            await trainer.initialize()

            symbols = symbols or self.config.get("symbols", ["EURUSD", "GBPUSD"])
            timeframes = timeframes or self.config.get("timeframes", ["H1", "H4"])

            logger.info(f"Training models for symbols: {symbols}")
            logger.info(f"Training timeframes: {timeframes}")

            results = await trainer.train_all_models(symbols, timeframes)

            # Display training results
            logger.info("🎓 Training Results:")
            for symbol, result in results.items():
                if result.get("status") == "success":
                    logger.info(
                        f"  ✅ {symbol}: {result['models_trained']} models trained"
                    )
                    for model_name, scores in result.get("model_scores", {}).items():
                        if "cv_mean" in scores:
                            logger.info(
                                f"    📊 {model_name}: {scores['cv_mean']:.3f} ± {scores['cv_std']:.3f}"
                            )
                else:
                    logger.error(
                        f"  ❌ {symbol}: {result.get('error', 'Unknown error')}"
                    )

            logger.info("✅ Training completed")

        except Exception as e:
            logger.error(f"Error in training mode: {e}")

    async def run_backtesting(self, start_date: str = None, end_date: str = None):
        """
        Runs the system in backtesting mode.

        Args:
            start_date (str, optional): The start date for the backtest (YYYY-MM-DD). Defaults to None.
            end_date (str, optional): The end date for the backtest (YYYY-MM-DD). Defaults to None.
        """
        logger.info("📈 Starting Backtesting Mode")

        try:
            backtester = Backtester(self.config)
            await backtester.initialize()

            start_date = start_date or "2023-01-01"
            end_date = end_date or datetime.now().strftime("%Y-%m-%d")

            logger.info(f"Backtesting period: {start_date} to {end_date}")

            results = await backtester.run_backtest(
                start_date=start_date,
                end_date=end_date,
                symbols=self.config.get("symbols", ["EURUSD"]),
            )

            # Display backtest results
            logger.info("📊 Backtest Results:")
            for symbol, result in results.items():
                stats = result.get("statistics", {})
                logger.info(f"  📈 {symbol}:")
                logger.info(f"    Total Trades: {stats.get('total_trades', 0)}")
                logger.info(f"    Win Rate: {stats.get('win_rate', 0):.2%}")
                logger.info(f"    Total Return: {stats.get('total_return', 0):.2%}")
                logger.info(f"    Sharpe Ratio: {stats.get('sharpe_ratio', 0):.3f}")
                logger.info(f"    Max Drawdown: {stats.get('max_drawdown', 0):.2%}")

            logger.info("✅ Backtesting completed")

        except Exception as e:
            logger.error(f"Error in backtesting mode: {e}")

    async def run_test_mode(self):
        """
        Runs a series of system tests to verify component functionality.
        """
        logger.info("🧪 Starting Test Mode")

        try:
            # Test data provider connection
            logger.info("Testing data provider...")
            if self.config.get("fxcm", {}).get("use_mock", True):
                data_provider = MockFXCMProvider(self.config["fxcm"])
            else:
                data_provider = FXCMDataProvider(self.config["fxcm"])

            connected = await data_provider.connect()
            if connected:
                logger.info("✅ Data provider connection successful")

                # Test data retrieval
                test_data = await data_provider.get_historical_data("EURUSD", "H1", 100)
                logger.info(f"✅ Retrieved {len(test_data)} data points for EURUSD")

                await data_provider.disconnect()
            else:
                logger.error("❌ Data provider connection failed")
                return

            # Test AI predictor
            logger.info("Testing AI predictor...")
            predictor = EnsemblePredictor(self.config["ai_models"])
            await predictor.initialize()

            if len(test_data) > 50:
                prediction = await predictor.predict("EURUSD", test_data)
                logger.info(
                    f"✅ AI prediction generated: confidence={prediction['confidence']:.3f}"
                )

            # Test signal generation
            logger.info("Testing signal generation...")
            self.trading_engine = TradingEngine(self.config)
            test_signals = await self.trading_engine.force_signal_generation(["EURUSD"])

            if test_signals:
                logger.info(f"✅ Generated {len(test_signals)} test signals")
                for signal in test_signals:
                    logger.info(
                        f"  📊 {signal.symbol}: {signal.signal_type.value} @ {signal.confidence:.3f}"
                    )
            else:
                logger.warning("⚠️  No test signals generated")

            logger.info("✅ All tests completed successfully")

        except Exception as e:
            logger.error(f"Error in test mode: {e}")

    async def generate_sample_signals(self, count: int = 5):
        """
        Generates a specified number of sample signals for testing MT4/5 integration.

        Args:
            count (int, optional): The number of sample signals to generate. Defaults to 5.
        """
        logger.info(f"🎲 Generating {count} sample signals")

        try:
            self.trading_engine = TradingEngine(self.config)
            await self.trading_engine.data_provider.connect()
            await self.trading_engine.ensemble_predictor.initialize()
            await self.trading_engine.spreadsheet_manager.initialize()

            signals = await self.trading_engine.force_signal_generation(
                self.config.get("symbols", ["EURUSD", "GBPUSD"])[:count]
            )

            if signals:
                await self.trading_engine.spreadsheet_manager.update_signals(signals)

                logger.info(f"✅ Generated {len(signals)} sample signals")
                logger.info("📁 Output files created:")
                logger.info("  📊 signal_output/genx_signals.xlsx")
                logger.info("  📈 signal_output/MT4_Signals.csv")
                logger.info("  📈 signal_output/MT5_Signals.csv")

                # Display signal summary
                for signal in signals:
                    logger.info(
                        f"  🎯 {signal.symbol}: {signal.signal_type.value} "
                        f"@ {signal.entry_price:.5f} (confidence: {signal.confidence:.3f})"
                    )
            else:
                logger.warning("⚠️  No signals could be generated")

            await self.trading_engine.data_provider.disconnect()

        except Exception as e:
            logger.error(f"Error generating sample signals: {e}")

    def print_system_info(self):
        """
        Prints key information about the system configuration.
        """
        logger.info("=" * 60)
        logger.info("🚀 GenX FX Trading System")
        logger.info("   Advanced AI-Powered Forex Signal Generator")
        logger.info("=" * 60)
        logger.info(f"📊 Symbols: {', '.join(self.config.get('symbols', []))}")
        logger.info(f"⏰ Timeframes: {', '.join(self.config.get('timeframes', []))}")
        logger.info(
            f"🎯 Primary Timeframe: {self.config.get('primary_timeframe', 'H1')}"
        )
        logger.info(
            f"🤖 AI Models: {self.config.get('ai_models', {}).get('ensemble_size', 5)} ensemble models"
        )
        logger.info(
            f"📈 Max Risk per Trade: {self.config.get('risk_management', {}).get('max_risk_per_trade', 0.02):.1%}"
        )
        logger.info(
            f"⚡ Signal Generation: Every {self.config.get('signal_generation_interval', 300)} seconds"
        )
        logger.info(f"💾 Output Directory: signal_output/")
        logger.info("=" * 60)


async def main():
    """
    The main entry point for the application. Parses command-line arguments
    and runs the system in the specified mode.
    """
    parser = argparse.ArgumentParser(description="GenX FX Trading System")
    parser.add_argument(
        "mode",
        choices=["live", "train", "backtest", "test", "sample"],
        help="System mode to run",
    )
    parser.add_argument(
        "--config", default="config/trading_config.json", help="Configuration file path"
    )
    parser.add_argument(
        "--symbols", nargs="+", help="Symbols to trade (for training/backtesting)"
    )
    parser.add_argument(
        "--timeframes", nargs="+", help="Timeframes to use (for training)"
    )
    parser.add_argument(
        "--start-date", type=str, help="Start date for backtesting (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", type=str, help="End date for backtesting (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--count", type=int, default=5, help="Number of sample signals to generate"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(level=args.log_level)

    # Initialize system
    system = GenXTradingSystem(args.config)
    system.print_system_info()

    # Start health check server for Cloud Run
    system.start_health_server(port=int(os.environ.get("PORT", 8080)))

    try:
        if args.mode == "live":
            await system.run_live_trading()
        elif args.mode == "train":
            await system.run_training_mode(args.symbols, args.timeframes)
        elif args.mode == "backtest":
            await system.run_backtesting(args.start_date, args.end_date)
        elif args.mode == "test":
            await system.run_test_mode()
        elif args.mode == "sample":
            await system.generate_sample_signals(args.count)

    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 System error: {e}")
        sys.exit(1)

    logger.info("🏁 GenX Trading System stopped")


if __name__ == "__main__":
    asyncio.run(main())
