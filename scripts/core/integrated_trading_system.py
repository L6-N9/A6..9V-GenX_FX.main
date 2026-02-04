#!/usr/bin/env python3
"""
Integrated Trading System - GenX AI Trading Platform
Orchestrates all components: FXCM API, AI models, EA communication, and asset management.
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd

# Import all our custom services
sys.path.append("/opt/genx")
from ai_models.ensemble_predictor import create_ensemble_predictor
from api.services.asset_manager import (
    AccountSummary,
    ClosedTrade,
    Position,
    create_asset_manager,
)
from api.services.ea_communication import TradingSignal, create_ea_server
from api.services.enhanced_gemini_service import create_enhanced_gemini_service
from api.services.fxcm_service import TradeSignal, create_fxcm_service
from api.services.news_service import NewsService
from api.services.reddit_service import RedditService
from core.config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/opt/genx/logs/integrated_system.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

settings = get_settings()


class IntegratedTradingSystem:
    """Main orchestrator for the GenX AI Trading Platform"""

    def __init__(self):
        self.running = False
        self.services = {}
        self.models = {}
        self.last_prediction_time = {}
        self.active_positions = {}

        # Performance tracking
        self.signals_generated = 0
        self.signals_executed = 0
        self.total_pnl = 0.0

    async def initialize(self):
        """Initialize all services and models"""
        try:
            logger.info("Initializing GenX Integrated Trading System...")

            # Initialize FXCM service
            logger.info("Connecting to FXCM API...")
            self.services["fxcm"] = await create_fxcm_service()

            # Initialize asset manager
            logger.info("Setting up asset management...")
            self.services["asset_manager"] = await create_asset_manager(
                use_google_sheets=True
            )

            # Initialize EA server
            logger.info("Starting EA communication server...")
            self.services["ea_server"] = await create_ea_server(
                host=settings.EA_SERVER_HOST, port=settings.EA_SERVER_PORT
            )

            # Initialize enhanced Gemini AI
            logger.info("Connecting to Gemini AI...")
            self.services["gemini"] = create_enhanced_gemini_service()

            # Initialize news and social media services
            logger.info("Setting up news and social media feeds...")
            self.services["news"] = NewsService()
            self.services["reddit"] = RedditService()

            # Initialize AI ensemble model
            logger.info("Loading AI ensemble models...")
            self.models["ensemble"] = create_ensemble_predictor()

            # Try to load pre-trained models
            try:
                self.models["ensemble"].load_models("/opt/genx/models/ensemble")
                logger.info("Loaded pre-trained ensemble models")
            except Exception as e:
                logger.warning(f"Could not load pre-trained models: {e}")
                logger.info("Will train models with historical data")
                await self._train_models()

            # Setup event subscriptions
            self._setup_event_handlers()

            logger.info("GenX Integrated Trading System initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize trading system: {e}")
            return False

    async def _train_models(self):
        """Train AI models with historical data"""
        try:
            logger.info("Training AI models with historical data...")

            # Fetch historical data for major pairs
            instruments = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"]

            for instrument in instruments:
                logger.info(f"Fetching historical data for {instrument}...")

                # Get 6 months of 15-minute data
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=180)

                candles = await self.services["fxcm"].get_historical_data(
                    instrument=instrument,
                    timeframe="M15",
                    start_time=start_time,
                    end_time=end_time,
                    count=17280,  # 6 months of 15-min data
                )

                if candles:
                    # Convert to DataFrame
                    df = self.services["fxcm"].to_dataframe(candles)

                    # Train ensemble model
                    training_results = self.models["ensemble"].train(df)
                    logger.info(
                        f"Training results for {instrument}: {training_results}"
                    )

            # Save trained models
            self.models["ensemble"].save_models("/opt/genx/models/ensemble")
            logger.info("AI models trained and saved successfully")

        except Exception as e:
            logger.error(f"Error training models: {e}")

    def _setup_event_handlers(self):
        """Setup event handlers for various services"""

        # EA server event handlers
        self.services["ea_server"].subscribe_to_trade_results(self._handle_trade_result)
        self.services["ea_server"].subscribe_to_account_status(
            self._handle_account_status
        )
        self.services["ea_server"].subscribe_to_heartbeat(self._handle_ea_heartbeat)
        self.services["ea_server"].subscribe_to_errors(self._handle_ea_error)

        # FXCM price update handler
        self.services["fxcm"].subscribe_to_prices(self._handle_price_update)

    async def _handle_trade_result(self, trade_result, connection):
        """Handle trade execution results from EA"""
        try:
            logger.info(f"Trade result received: {trade_result}")

            if trade_result.success:
                self.signals_executed += 1
                logger.info(
                    f"Trade executed successfully: Ticket {trade_result.ticket}"
                )
            else:
                logger.warning(f"Trade execution failed: {trade_result.error_message}")

            # Update performance tracking
            # This would typically involve more sophisticated P&L calculation

        except Exception as e:
            logger.error(f"Error handling trade result: {e}")

    async def _handle_account_status(self, account_status, connection):
        """Handle account status updates from EA"""
        try:
            logger.info(
                f"Account status update: Balance={account_status.balance}, "
                f"Equity={account_status.equity}, Open Positions={account_status.open_positions}"
            )

            # Create account summary for asset manager
            summary = AccountSummary(
                balance=account_status.balance,
                equity=account_status.equity,
                margin=account_status.margin,
                free_margin=account_status.free_margin,
                margin_level=account_status.margin_level,
                total_open_positions=account_status.open_positions,
                total_unrealized_pnl=account_status.profit,
                daily_pnl=0.0,  # Would calculate from trades
                weekly_pnl=0.0,
                monthly_pnl=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                profit_factor=1.0,
                last_updated=account_status.timestamp,
            )

            # Update asset management sheet
            await self.services["asset_manager"].update_portfolio(summary, [])

        except Exception as e:
            logger.error(f"Error handling account status: {e}")

    async def _handle_ea_heartbeat(self, heartbeat_data, connection):
        """Handle EA heartbeat messages"""
        logger.debug(f"EA heartbeat from {connection.address}: {heartbeat_data}")

    async def _handle_ea_error(self, error_data, connection):
        """Handle EA error messages"""
        logger.error(f"EA error from {connection.address}: {error_data}")

    async def _handle_price_update(self, market_data):
        """Handle real-time price updates from FXCM"""
        try:
            instrument = market_data.instrument
            current_time = datetime.utcnow()

            # Check if we should generate a new prediction (every 15 minutes)
            last_prediction = self.last_prediction_time.get(instrument, datetime.min)

            if current_time - last_prediction >= timedelta(minutes=15):
                await self._generate_trading_signal(instrument, market_data)
                self.last_prediction_time[instrument] = current_time

        except Exception as e:
            logger.error(f"Error handling price update: {e}")

    async def _generate_trading_signal(self, instrument: str, market_data):
        """Generate and validate trading signals"""
        try:
            current_time = datetime.utcnow()
            logger.info(f"Generating trading signal for {instrument}")

            # Get recent historical data for prediction
            candles = await self.services["fxcm"].get_historical_data(
                instrument=instrument,
                timeframe="M15",
                count=200,  # Last 200 15-minute candles
            )

            if not candles:
                logger.warning(f"No historical data available for {instrument}")
                return

            # Convert to DataFrame
            df = self.services["fxcm"].to_dataframe(candles)

            # Generate AI prediction
            prediction = self.models["ensemble"].predict(df)

            if prediction.signal == "HOLD":
                logger.info(f"AI recommends HOLD for {instrument}")
                return

            # Get news and social sentiment
            news_articles = await self.services["news"].get_recent_news(
                keywords=[instrument.replace("_", "/"), "forex"], hours_back=24
            )

            social_posts = await self.services["reddit"].get_recent_posts(
                subreddits=["forex", "trading"],
                keywords=[instrument.replace("_", "/")],
                hours_back=24,
            )

            # Analyze sentiment with Gemini AI
            sentiment = await self.services["gemini"].analyze_market_sentiment(
                news_articles=[
                    article.get("content", "") for article in news_articles[:10]
                ],
                social_media_posts=[
                    post.get("content", "") for post in social_posts[:20]
                ],
                instrument=instrument,
            )

            # Validate signal with Gemini AI
            validation = await self.services["gemini"].validate_trading_signal(
                signal_data={
                    "instrument": instrument,
                    "action": prediction.signal,
                    "confidence": prediction.confidence,
                    "model_type": "AI Ensemble",
                },
                market_context=prediction.market_conditions,
                current_sentiment=sentiment,
                recent_news=[article.get("title", "") for article in news_articles[:5]],
            )

            if not validation.is_valid:
                logger.warning(
                    f"Signal validation failed for {instrument}: {validation.reasoning}"
                )
                return

            # Adjust confidence based on Gemini validation
            adjusted_confidence = (
                prediction.confidence * validation.confidence_adjustment
            )

            if adjusted_confidence < 0.6:  # Minimum confidence threshold
                logger.info(
                    f"Adjusted confidence too low for {instrument}: {adjusted_confidence}"
                )
                return

            # Calculate position size based on risk parameters
            risk_params = self.services["asset_manager"].get_risk_parameters()
            account_info = await self.services["fxcm"].get_account_info()

            base_volume = (
                risk_params.max_risk_per_trade
                * account_info.get("equity", 10000)
                / 10000
            )
            adjusted_volume = base_volume * validation.recommended_position_size
            adjusted_volume = min(adjusted_volume, risk_params.max_lot_size)

            # Create trading signal
            trading_signal = TradingSignal(
                signal_id=f"{instrument}_{int(current_time.timestamp())}",
                instrument=instrument,
                action=prediction.signal,
                volume=adjusted_volume,
                stop_loss=self._calculate_stop_loss(market_data, prediction.signal),
                take_profit=self._calculate_take_profit(market_data, prediction.signal),
                confidence=adjusted_confidence,
                comment=f"GenX AI - Conf: {adjusted_confidence:.2f}",
            )

            # Validate with risk management
            open_positions = await self.services["fxcm"].get_open_positions()
            positions = [
                Position(
                    ticket=str(pos.get("id", "")),
                    symbol=pos.get("instrument", ""),
                    type="BUY" if float(pos.get("units", 0)) > 0 else "SELL",
                    lots=abs(float(pos.get("units", 0))) / 10000,
                    open_price=float(pos.get("price", 0)),
                    current_price=market_data.mid_price,
                    stop_loss=None,
                    take_profit=None,
                    open_time=datetime.now(),
                    current_pnl=float(pos.get("unrealizedPL", 0)),
                )
                for pos in open_positions
            ]

            if not self.services["asset_manager"].validate_trade_risk(
                trading_signal, account_info.get("equity", 10000), positions
            ):
                logger.warning(f"Risk validation failed for {instrument}")
                return

            # Send signal to EA
            success = await self.services["ea_server"].broadcast_signal(trading_signal)

            if success:
                self.signals_generated += 1
                logger.info(
                    f"Trading signal sent for {instrument}: {prediction.signal} "
                    f"with confidence {adjusted_confidence:.2f}"
                )
            else:
                logger.error(f"Failed to send trading signal for {instrument}")

        except Exception as e:
            logger.error(f"Error generating trading signal for {instrument}: {e}")

    def _calculate_stop_loss(self, market_data, action: str) -> float:
        """Calculate stop loss based on ATR or fixed percentage"""
        # Simple implementation - 2% stop loss
        if action == "BUY":
            return market_data.bid * 0.98  # 2% below current price
        else:
            return market_data.ask * 1.02  # 2% above current price

    def _calculate_take_profit(self, market_data, action: str) -> float:
        """Calculate take profit based on risk-reward ratio"""
        # Simple implementation - 1.5:1 risk-reward
        if action == "BUY":
            return market_data.bid * 1.03  # 3% above current price
        else:
            return market_data.ask * 0.97  # 3% below current price

    async def start(self):
        """Start the integrated trading system"""
        try:
            self.running = True
            logger.info("Starting GenX Integrated Trading System...")

            # Start price streaming for major pairs
            instruments = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CHF"]

            # Start FXCM price streaming
            await self.services["fxcm"].start_price_stream(instruments)

            logger.info("GenX Trading System is now running!")

            # Main loop
            while self.running:
                try:
                    # Periodic tasks
                    await self._periodic_maintenance()
                    await asyncio.sleep(60)  # Check every minute

                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"Error starting trading system: {e}")
            await self.stop()

    async def _periodic_maintenance(self):
        """Perform periodic maintenance tasks"""
        try:
            current_time = datetime.utcnow()

            # Log system status every 5 minutes
            if current_time.minute % 5 == 0:
                connected_eas = self.services["ea_server"].get_connected_eas()
                logger.info(
                    f"System Status - Signals Generated: {self.signals_generated}, "
                    f"Signals Executed: {self.signals_executed}, "
                    f"Connected EAs: {len(connected_eas)}"
                )

            # Retrain models daily at 00:00 UTC
            if current_time.hour == 0 and current_time.minute == 0:
                logger.info("Starting daily model retraining...")
                await self._train_models()
                logger.info("Daily model retraining completed")

        except Exception as e:
            logger.error(f"Error in periodic maintenance: {e}")

    async def stop(self):
        """Stop the integrated trading system"""
        try:
            logger.info("Stopping GenX Integrated Trading System...")
            self.running = False

            # Stop all services
            if "fxcm" in self.services:
                await self.services["fxcm"].disconnect()

            if "ea_server" in self.services:
                await self.services["ea_server"].stop()

            logger.info("GenX Trading System stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping trading system: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())


async def main():
    """Main entry point"""
    system = IntegratedTradingSystem()

    # Setup signal handlers
    signal.signal(signal.SIGINT, system._signal_handler)
    signal.signal(signal.SIGTERM, system._signal_handler)

    try:
        # Initialize system
        if not await system.initialize():
            logger.error("Failed to initialize system")
            return 1

        # Start trading
        await system.start()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        await system.stop()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
