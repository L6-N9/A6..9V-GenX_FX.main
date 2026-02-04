import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append(os.getcwd())

from unittest.mock import MagicMock, patch

from core.data_sources.fxcm_provider import MockFXCMProvider
from core.trading_engine import TradingEngine


async def dry_run():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DryRun")

    logger.info("Starting Trading Engine Dry Run...")

    # Initialize engine
    engine = TradingEngine()

    # Inject Mock Data Provider
    mock_provider = MockFXCMProvider(engine.config["fxcm"])
    engine.data_provider = mock_provider

    # Mock EnsemblePredictor to avoid training/loading issues and return a consistent signal
    mock_predictor = MagicMock()

    # Ensure it returns an awaitable
    async def mock_predict(*args, **kwargs):
        return {
            "direction": 0.8,  # Strong Buy
            "confidence": 0.85,
            "signal_strength": "STRONG",
            "model_agreement": 0.9,
            "fundamental_score": 0.7,
            "model_scores": {"random_forest": 0.8, "xgboost": 0.75},
        }

    engine.ensemble_predictor.predict = mock_predict

    # Mock Signal Validator to always approve
    async def mock_validate(*args, **kwargs):
        return True

    engine.signal_validator.validate = mock_validate

    logger.info("Injecting mock components complete.")

    # Generate signals for a few symbols
    symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    logger.info(f"Generating signals for {symbols}...")

    signals = await engine.force_signal_generation(symbols)

    logger.info(f"Generated {len(signals)} signals.")

    for signal in signals:
        mt4_format = signal.to_mt4_format()
        logger.info(f"Signal for {signal.symbol}: {signal.signal_type.value}")
        logger.info(f"  Entry: {signal.entry_price}")
        logger.info(f"  Stop Loss: {signal.stop_loss}")
        logger.info(f"  Take Profit: {signal.take_profit}")
        logger.info(f"  Confidence: {signal.confidence}")
        logger.info(f"  MT4 Format: {mt4_format}")

        # Verify SL/TP logic
        if signal.signal_type.value == "BUY":
            assert signal.stop_loss < signal.entry_price
            assert signal.take_profit > signal.entry_price
        elif signal.signal_type.value == "SELL":
            assert signal.stop_loss > signal.entry_price
            assert signal.take_profit < signal.entry_price

    logger.info("Dry run successful!")

    # Now check if it updates the spreadsheet
    await engine.spreadsheet_manager.initialize()
    await engine.spreadsheet_manager.update_signals(signals)

    logger.info("Spreadsheet updated.")

    # Verify CSV content
    mt4_csv = "signal_output/MT4_Signals.csv"
    if os.path.exists(mt4_csv):
        with open(mt4_csv, "r") as f:
            lines = f.readlines()
            logger.info(f"CSV Headers: {lines[0].strip()}")
            for line in lines[1:]:
                logger.info(f"CSV Row: {line.strip()}")
                assert len(line.split(",")) == 9
    else:
        logger.error("MT4_Signals.csv not found!")


if __name__ == "__main__":
    asyncio.run(dry_run())
