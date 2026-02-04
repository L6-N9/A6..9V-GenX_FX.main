"""
GenX FX Trading Engine - Core Trading System
Focuses on generating reliable trading signals for MT4/5 Expert Advisors
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from core.ai_models.ensemble_predictor import EnsemblePredictor
from core.data_sources.fxcm_provider import FXCMDataProvider
from core.risk_management.position_sizer import PositionSizer
from core.signal_validators.multi_timeframe_validator import MultiTimeframeValidator
from core.spreadsheet_manager import SpreadsheetManager
from utils.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE_BUY = "CLOSE_BUY"
    CLOSE_SELL = "CLOSE_SELL"


class SignalStrength(Enum):
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class TradingSignal:
    """
    Represents a fully formed trading signal, optimized for MT4/5 EA consumption.

    Attributes:
        timestamp (datetime): The time the signal was generated.
        symbol (str): The trading symbol.
        signal_type (SignalType): The type of signal (e.g., BUY, SELL).
        strength (SignalStrength): The calculated strength of the signal.
        entry_price (float): The recommended entry price.
        stop_loss (float): The recommended stop-loss price.
        take_profit (float): The recommended take-profit price.
        confidence (float): The confidence score from the AI model.
        risk_reward_ratio (float): The calculated risk/reward ratio.
        timeframe (str): The primary timeframe the signal was based on.
        model_predictions (Dict[str, float]): Scores from individual models.
        technical_confluence (int): A score for technical indicator agreement.
        fundamental_score (float): A score representing fundamental analysis.
        market_condition (str): The perceived market condition (e.g., "UPTREND").
        position_size_pct (float): The recommended position size as a percentage.
        max_risk_pct (float): The maximum risk for this trade as a percentage.
        expiry_time (datetime): The time at which the signal should be considered expired.
    """

    timestamp: datetime
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_reward_ratio: float
    timeframe: str
    model_predictions: Dict[str, float]
    technical_confluence: int
    fundamental_score: float
    market_condition: str
    position_size_pct: float
    max_risk_pct: float
    expiry_time: datetime

    def to_mt4_format(self) -> Dict[str, Any]:
        """
        Converts the signal to a dictionary format suitable for an MT4/5 EA.

        Returns:
            Dict[str, Any]: A dictionary with formatted signal data.
        """
        return {
            "Magic": hash(f"{self.symbol}_{self.timestamp.isoformat()}") % 2147483647,
            "Symbol": self.symbol,
            "Signal": self.signal_type.value,
            "Strength": self.strength.value,
            "EntryPrice": round(self.entry_price, 5),
            "StopLoss": round(self.stop_loss, 5),
            "TakeProfit": round(self.take_profit, 5),
            "Confidence": round(self.confidence, 4),
            "RiskReward": round(self.risk_reward_ratio, 2),
            "PositionSize": round(self.position_size_pct, 4),
            "MaxRisk": round(self.max_risk_pct, 4),
            "Timeframe": self.timeframe,
            "Timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "ExpiryTime": self.expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
            "MarketCondition": self.market_condition,
            "TechnicalConfluence": self.technical_confluence,
            "FundamentalScore": round(self.fundamental_score, 4),
        }


class TradingEngine:
    """
    The core trading engine responsible for orchestrating the signal generation process.

    This engine integrates data providers, AI predictors, risk management, and
    signal validation to produce high-quality trading signals for consumption
    by EAs.

    Attributes:
        config (Dict): The configuration for the engine and its components.
        is_running (bool): A flag indicating if the engine's main loop is active.
        data_provider (FXCMDataProvider): The data source provider.
        ensemble_predictor (EnsemblePredictor): The AI prediction model.
        position_sizer (PositionSizer): The risk and position sizing manager.
        signal_validator (MultiTimeframeValidator): The signal validation utility.
        spreadsheet_manager (SpreadsheetManager): The manager for signal output.
    """

    def __init__(self, config_path: str = "config/trading_config.json"):
        """
        Initializes the TradingEngine.

        Args:
            config_path (str): The path to the main trading configuration file.
        """
        self.config = self._load_config(config_path)

        # Flatten 'trading' config if it exists
        if "trading" in self.config:
            for key, value in self.config["trading"].items():
                if key not in self.config:
                    self.config[key] = value

        self.is_running = False
        self.last_signals: Dict[str, datetime] = {}

        # Initialize core components
        self.data_provider = FXCMDataProvider(self.config["fxcm"])
        self.ensemble_predictor = EnsemblePredictor(self.config["ai_models"])

        rm_config = self.config.get("risk_management", {})
        self.position_sizer = PositionSizer(
            account_balance=self.config.get("account_balance", 100000),
            max_risk_per_trade=rm_config.get("max_risk_per_trade", 0.02),
            max_portfolio_risk=rm_config.get("max_total_risk", 0.06),
        )

        self.signal_validator = MultiTimeframeValidator(self.config["validation"])
        self.spreadsheet_manager = SpreadsheetManager(self.config["spreadsheet"])
        self.technical_indicators = TechnicalIndicators()

        # Performance tracking
        self.signal_history = []
        self.performance_metrics = {}

        logger.info("Trading Engine initialized successfully")

    def _load_config(self, config_path: str) -> Dict:
        """
        Loads the trading configuration from a JSON file.

        Args:
            config_path (str): The path to the configuration file.

        Returns:
            Dict: The loaded configuration dictionary.
        """
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults.")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Provides a default configuration if the config file is not found."""
        return {
            "symbols": [
                "EURUSD",
                "GBPUSD",
                "USDJPY",
                "USDCHF",
                "AUDUSD",
                "USDCAD",
                "NZDUSD",
            ],
            "timeframes": ["M15", "H1", "H4", "D1"],
            "primary_timeframe": "H1",
            "signal_generation_interval": 300,  # 5 minutes
            "max_concurrent_signals": 3,
            "min_confidence_threshold": 0.65,
            "risk_management": {
                "max_risk_per_trade": 0.02,
                "max_total_risk": 0.06,
                "position_sizing_method": "fixed_fractional",
                "stop_loss_method": "atr_based",
                "take_profit_ratio": 2.0,
            },
            "ai_models": {
                "ensemble_size": 5,
                "retrain_interval_hours": 24,
                "lookback_periods": 100,
                "feature_engineering": True,
                "cross_validation_folds": 5,
            },
            "validation": {
                "timeframe_confluence_required": 2,
                "technical_confluence_threshold": 3,
                "fundamental_weight": 0.3,
                "sentiment_weight": 0.2,
            },
            "fxcm": {"environment": "demo", "refresh_interval": 60},
            "spreadsheet": {
                "update_interval": 30,
                "max_signals": 50,
                "backup_enabled": True,
            },
        }

    async def start(self):
        """
        Starts the trading engine and its components.

        This method initializes all services and begins the main trading loop.
        """
        if self.is_running:
            logger.warning("Trading engine is already running.")
            return

        self.is_running = True
        logger.info("Starting Trading Engine...")

        try:
            # Initialize connections and services
            await self.data_provider.connect()
            await self.ensemble_predictor.initialize()
            await self.spreadsheet_manager.initialize()

            # Start main trading loop
            await self._run_trading_loop()

        except Exception as e:
            logger.error(f"Fatal error during engine startup: {e}")
            await self.stop()

    async def stop(self):
        """Stops the trading engine gracefully."""
        if not self.is_running:
            return
        logger.info("Stopping Trading Engine...")
        self.is_running = False

        try:
            await self.data_provider.disconnect()
            await self.spreadsheet_manager.save_final_state()
            logger.info("Trading Engine stopped successfully.")
        except Exception as e:
            logger.error(f"Error during trading engine shutdown: {e}")

    async def _run_trading_loop(self):
        """The main trading loop that periodically generates and processes signals."""
        logger.info("Trading loop started.")
        while self.is_running:
            try:
                start_time = datetime.now()

                signals = await self._generate_signals()
                validated_signals = await self._validate_signals(signals)

                if validated_signals:
                    await self.spreadsheet_manager.update_signals(validated_signals)
                    logger.info(
                        f"Generated and exported {len(validated_signals)} validated signals."
                    )

                await self._update_performance_metrics()

                # Wait for the next cycle
                execution_time = (datetime.now() - start_time).total_seconds()
                sleep_time = max(
                    0, self.config["signal_generation_interval"] - execution_time
                )
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait before retrying on error

    async def _generate_signals(self) -> List[TradingSignal]:
        """
        Generates trading signals for all configured symbols.

        Returns:
            List[TradingSignal]: A list of generated TradingSignal objects.
        """
        tasks = [
            self._process_symbol_for_signal(symbol) for symbol in self.config["symbols"]
        ]
        results = await asyncio.gather(*tasks)
        return [signal for signal in results if signal is not None]

    async def _process_symbol_for_signal(self, symbol: str) -> Optional[TradingSignal]:
        """Processes a single symbol to generate a trading signal."""
        try:
            market_data = await self._get_multi_timeframe_data(symbol)
            if not self._is_data_valid(market_data):
                return None

            prediction = await self.ensemble_predictor.predict(
                symbol=symbol,
                data=market_data[self.config["primary_timeframe"]],
                multi_timeframe_data=market_data,
            )

            if prediction["confidence"] < self.config["min_confidence_threshold"]:
                return None

            market_condition = self._analyze_market_condition(market_data)

            return await self._create_trading_signal(
                symbol=symbol,
                prediction=prediction,
                market_data=market_data,
                market_condition=market_condition,
            )
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None

    async def _get_multi_timeframe_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Get market data for multiple timeframes concurrently.

        Optimization: Fetches data for all configured timeframes in parallel
        using asyncio.gather instead of sequentially. This significantly reduces
        the data collection time for each symbol, making the signal generation
        process faster, especially with more timeframes or higher latency.
        """

        async def fetch_and_process(timeframe: str):
            """
            Asynchronously fetches data and then runs the CPU-bound indicator
            calculations in a separate thread to avoid blocking the event loop.
            """
            try:
                # 1. Asynchronously fetch I/O-bound data
                df = await self.data_provider.get_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    periods=self.config["ai_models"]["lookback_periods"],
                )

                if df is None or df.empty:
                    return timeframe, None

                # 2. Run CPU-bound calculations in a thread pool
                # This prevents blocking the asyncio event loop.
                df_with_indicators = await asyncio.to_thread(
                    self.technical_indicators.add_all_indicators, df
                )
                return timeframe, df_with_indicators

            except Exception as e:
                logger.error(f"Error getting data for {symbol} {timeframe}: {e}")
                return timeframe, None

        # Schedule all fetch/process tasks to run concurrently
        tasks = [fetch_and_process(tf) for tf in self.config["timeframes"]]
        results = await asyncio.gather(*tasks)

        # Filter out any tasks that failed
        return {tf: df for tf, df in results if df is not None and not df.empty}

    def _is_data_valid(self, market_data: Dict[str, pd.DataFrame]) -> bool:
        """Validate market data quality"""
        if not market_data:
            return False

        primary_data = market_data.get(self.config["primary_timeframe"])
        if primary_data is None or len(primary_data) < 50:
            return False

        # Check for recent data (within last hour)
        latest_timestamp = primary_data.index[-1]
        if datetime.now() - latest_timestamp > timedelta(hours=1):
            return False

        # ⚡ Bolt Addition: Ensure critical 'atr' column is present
        # This check prevents runtime errors in `_calculate_levels` and
        # ensures data integrity before processing.
        if "atr" not in primary_data.columns:
            logger.warning(
                f"Data for {self.config['primary_timeframe']} is missing 'atr' column."
            )
            return False

        return True

    def _analyze_market_condition(self, market_data: Dict[str, pd.DataFrame]) -> str:
        """
        Analyze overall market condition using pre-calculated indicators.

        ---
        ⚡ Bolt Optimization:
        - Replaced redundant calculations for volatility, SMA20, and SMA50.
        - The function now uses the `volatility_20`, `volatility_100`, `sma_20`,
          and `sma_50` columns that are already pre-calculated in the
          technical indicators utility.
        - Impact: Reduces CPU load by avoiding re-computation of several
          rolling window functions on every signal analysis, making the
          trading loop more efficient.
        ---
        """
        primary_data = market_data[self.config["primary_timeframe"]]

        # --- Use pre-calculated volatility ---
        # The 'volatility_20' and 'volatility_100' indicators are already calculated.
        volatility = primary_data["volatility_20"].iloc[-1]
        avg_volatility = primary_data["volatility_100"].mean()

        # --- Use pre-calculated trend strength ---
        # The 'sma_20' and 'sma_50' indicators are already calculated.
        sma_20 = primary_data["sma_20"].iloc[-1]
        sma_50 = primary_data["sma_50"].iloc[-1]
        current_price = primary_data["close"].iloc[-1]

        if volatility > avg_volatility * 1.5:
            return "HIGH_VOLATILITY"
        elif current_price > sma_20 > sma_50:
            return "UPTREND"
        elif current_price < sma_20 < sma_50:
            return "DOWNTREND"
        elif abs(current_price - sma_20) / current_price < 0.001:
            return "SIDEWAYS"
        else:
            return "MIXED"

    async def _create_trading_signal(
        self,
        symbol: str,
        prediction: Dict,
        market_data: Dict[str, pd.DataFrame],
        market_condition: str,
    ) -> Optional[TradingSignal]:
        """Create a validated trading signal"""

        primary_data = market_data[self.config["primary_timeframe"]]
        current_price = primary_data["close"].iloc[-1]

        # Determine signal type based on prediction
        signal_type = self._get_signal_type(
            prediction["direction"], prediction["confidence"]
        )

        if signal_type == SignalType.HOLD:
            return None

        # Calculate entry, stop loss, and take profit
        entry_price = current_price
        stop_loss, take_profit = self._calculate_levels(
            symbol=symbol,
            signal_type=signal_type,
            entry_price=entry_price,
            data=primary_data,
            market_condition=market_condition,
        )

        # Calculate risk-reward ratio
        if signal_type == SignalType.BUY:
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:
            risk = stop_loss - entry_price
            reward = entry_price - take_profit

        risk_reward_ratio = reward / risk if risk > 0 else 0

        # Skip signals with poor risk-reward
        if risk_reward_ratio < 1.5:
            return None

        # Calculate position size
        position_info = self.position_sizer.calculate_position_size(
            symbol=symbol,
            entry_price=entry_price,
            stop_loss=stop_loss,
            confidence=prediction["confidence"],
        )
        position_size_pct = position_info.position_size

        # Determine signal strength
        strength = self._calculate_signal_strength(
            prediction["confidence"], risk_reward_ratio
        )

        # Calculate technical confluence
        technical_confluence = self._calculate_technical_confluence(
            primary_data, signal_type
        )

        return TradingSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=prediction["confidence"],
            risk_reward_ratio=risk_reward_ratio,
            timeframe=self.config["primary_timeframe"],
            model_predictions=prediction.get("model_scores", {}),
            technical_confluence=technical_confluence,
            fundamental_score=prediction.get("fundamental_score", 0.5),
            market_condition=market_condition,
            position_size_pct=position_size_pct,
            max_risk_pct=self.config["risk_management"]["max_risk_per_trade"],
            expiry_time=datetime.now() + timedelta(hours=4),  # 4-hour expiry
        )

    def _get_signal_type(self, direction: float, confidence: float) -> SignalType:
        """Determine signal type from prediction"""
        if confidence < self.config["min_confidence_threshold"]:
            return SignalType.HOLD

        if direction > 0.6:
            return SignalType.BUY
        elif direction < -0.6:
            return SignalType.SELL
        else:
            return SignalType.HOLD

    def _calculate_levels(
        self,
        symbol: str,
        signal_type: SignalType,
        entry_price: float,
        data: pd.DataFrame,
        market_condition: str,
    ) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels"""

        # ---
        # ⚡ Bolt Optimization:
        # - Removed the fallback ATR calculation. The 'atr' column is now
        #   guaranteed to exist by the `_is_data_valid` check.
        # - Impact: Prevents a redundant, CPU-intensive rolling window
        #   calculation in the hot path of signal generation, improving
        #   efficiency.
        # ---
        atr = data["atr"].iloc[-1]

        # Adjust multipliers based on market condition
        if market_condition == "HIGH_VOLATILITY":
            sl_multiplier, tp_multiplier = 2.5, 4.0
        elif market_condition in ["UPTREND", "DOWNTREND"]:
            sl_multiplier, tp_multiplier = 2.0, 3.5
        else:
            sl_multiplier, tp_multiplier = 1.5, 3.0

        if signal_type == SignalType.BUY:
            stop_loss = entry_price - (atr * sl_multiplier)
            take_profit = entry_price + (atr * tp_multiplier)
        else:  # SELL
            stop_loss = entry_price + (atr * sl_multiplier)
            take_profit = entry_price - (atr * tp_multiplier)

        return round(stop_loss, 5), round(take_profit, 5)

    def _calculate_signal_strength(
        self, confidence: float, risk_reward: float
    ) -> SignalStrength:
        """Calculate signal strength based on confidence and risk-reward"""
        strength_score = (confidence * 0.7) + (min(risk_reward / 3.0, 1.0) * 0.3)

        if strength_score >= 0.9:
            return SignalStrength.VERY_STRONG
        elif strength_score >= 0.8:
            return SignalStrength.STRONG
        elif strength_score >= 0.7:
            return SignalStrength.MODERATE
        else:
            return SignalStrength.WEAK

    def _calculate_technical_confluence(
        self, data: pd.DataFrame, signal_type: SignalType
    ) -> int:
        """Calculate how many technical indicators agree with the signal"""
        confluence = 0
        current_price = data["close"].iloc[-1]

        # Moving averages
        if "sma_20" in data.columns and "sma_50" in data.columns:
            sma_20 = data["sma_20"].iloc[-1]
            sma_50 = data["sma_50"].iloc[-1]

            if signal_type == SignalType.BUY and current_price > sma_20 > sma_50:
                confluence += 1
            elif signal_type == SignalType.SELL and current_price < sma_20 < sma_50:
                confluence += 1

        # RSI
        if "rsi" in data.columns:
            rsi = data["rsi"].iloc[-1]
            if signal_type == SignalType.BUY and rsi < 70:
                confluence += 1
            elif signal_type == SignalType.SELL and rsi > 30:
                confluence += 1

        # MACD
        if "macd" in data.columns and "macd_signal" in data.columns:
            macd = data["macd"].iloc[-1]
            macd_signal = data["macd_signal"].iloc[-1]

            if signal_type == SignalType.BUY and macd > macd_signal:
                confluence += 1
            elif signal_type == SignalType.SELL and macd < macd_signal:
                confluence += 1

        return confluence

    async def _validate_signals(
        self, signals: List[TradingSignal]
    ) -> List[TradingSignal]:
        """Validate signals using multi-timeframe analysis"""
        validated_signals = []

        for signal in signals:
            try:
                # Check if we already have a recent signal for this symbol
                if self._has_recent_signal(signal.symbol):
                    continue

                # Multi-timeframe validation
                if await self.signal_validator.validate(signal):
                    validated_signals.append(signal)
                    self.last_signals[signal.symbol] = signal.timestamp

            except Exception as e:
                logger.error(f"Error validating signal for {signal.symbol}: {e}")

        # Limit concurrent signals
        max_signals = self.config["max_concurrent_signals"]
        if len(validated_signals) > max_signals:
            # Sort by strength and confidence, take the best ones
            validated_signals.sort(
                key=lambda x: (x.strength.value, x.confidence), reverse=True
            )
            validated_signals = validated_signals[:max_signals]

        return validated_signals

    def _has_recent_signal(self, symbol: str, hours: int = 2) -> bool:
        """Check if we have a recent signal for this symbol"""
        if symbol not in self.last_signals:
            return False

        time_diff = datetime.now() - self.last_signals[symbol]
        return time_diff < timedelta(hours=hours)

    async def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        # This would analyze signal performance, accuracy, etc.
        # Implementation depends on how you want to track performance
        pass

    async def force_signal_generation(
        self, symbols: List[str] = None
    ) -> List[TradingSignal]:
        """Force signal generation for testing purposes"""
        if symbols is None:
            symbols = self.config["symbols"]

        logger.info(f"Force generating signals for: {symbols}")

        signals = []
        for symbol in symbols:
            try:
                market_data = await self._get_multi_timeframe_data(symbol)
                if not self._is_data_valid(market_data):
                    continue

                prediction = await self.ensemble_predictor.predict(
                    symbol=symbol,
                    data=market_data[self.config["primary_timeframe"]],
                    multi_timeframe_data=market_data,
                )

                market_condition = self._analyze_market_condition(market_data)

                signal = await self._create_trading_signal(
                    symbol=symbol,
                    prediction=prediction,
                    market_data=market_data,
                    market_condition=market_condition,
                )

                if signal:
                    signals.append(signal)

            except Exception as e:
                logger.error(f"Error force generating signal for {symbol}: {e}")

        return signals

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "total_signals_generated": len(self.signal_history),
            "signals_by_symbol": {},
            "average_confidence": 0.0,
            "win_rate": 0.0,
            "average_risk_reward": 0.0,
            "uptime": datetime.now() - getattr(self, "start_time", datetime.now()),
            "last_signal_time": (
                max(self.last_signals.values()) if self.last_signals else None
            ),
        }
