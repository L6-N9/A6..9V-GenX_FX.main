#!/usr/bin/env python3
"""
FXCM ForexConnect to Spreadsheet Integration Test
Comprehensive test of the FXCM ForexConnect API integration with spreadsheet output
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("test_integration.log")],
)
logger = logging.getLogger(__name__)


class FXCMSpreadsheetIntegrationTest:
    """
    A test suite for the integration between the FXCM ForexConnect API and
    spreadsheet output functionality.
    """

    def __init__(self):
        """
        Initializes the test suite.
        """
        self.config = self._load_config()
        self.data_provider = None
        self.spreadsheet_manager = None

    def _load_config(self) -> Dict[str, Any]:
        """
        Loads the configuration for the test, with environment variable substitution.

        Returns:
            Dict[str, Any]: The configuration dictionary.
        """
        config = {
            "fxcm_forexconnect": {
                "enabled": True,
                "use_mock": True,  # Default to mock for testing
                "username": os.getenv("FXCM_USERNAME", "D27739526"),
                "password": os.getenv("FXCM_PASSWORD", "cpsj1"),
                "connection_type": os.getenv("FXCM_CONNECTION_TYPE", "Demo"),
                "url": os.getenv("FXCM_URL", "http://fxcorporate.com/Hosts.jsp"),
                "timeout": 30,
                "retry_attempts": 3,
                "auto_reconnect": True,
            },
            "data_provider": {
                "symbols": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD"],
                "timeframes": ["M15", "H1", "H4", "D1"],
                "refresh_interval": 30,
            },
            "spreadsheet": {
                "output_directory": "signal_output",
                "update_interval": 30,
                "max_signals": 50,
                "formats": {
                    "excel": True,
                    "csv": True,
                    "json": True,
                    "mt4_csv": True,
                    "mt5_csv": True,
                },
                "include_account_info": True,
                "include_market_data": True,
            },
        }

        logger.info("Configuration loaded")
        return config

    async def setup_data_provider(self, use_mock: bool = None):
        """
        Sets up the FXCM data provider, either real or mock.

        Args:
            use_mock (bool, optional): Whether to use the mock provider.
                                       Defaults to the value in the config.

        Returns:
            bool: True if the setup is successful, False otherwise.
        """
        try:
            if use_mock is None:
                use_mock = self.config["fxcm_forexconnect"]["use_mock"]

            # Import the appropriate provider
            if use_mock:
                from core.data_sources.fxcm_forexconnect_provider import (
                    MockFXCMForexConnectProvider,
                )

                self.data_provider = MockFXCMForexConnectProvider(
                    self.config["fxcm_forexconnect"]
                )
                logger.info("Using Mock FXCM ForexConnect Provider")
            else:
                from core.data_sources.fxcm_forexconnect_provider import (
                    FXCMForexConnectProvider,
                )

                self.data_provider = FXCMForexConnectProvider(
                    self.config["fxcm_forexconnect"]
                )
                logger.info("Using Real FXCM ForexConnect Provider")

            # Connect to the provider
            connected = await self.data_provider.connect()
            if connected:
                logger.info("✓ Data provider connected successfully")
                return True
            else:
                logger.error("✗ Failed to connect to data provider")
                return False

        except Exception as e:
            logger.error(f"Error setting up data provider: {e}")
            return False

    async def setup_spreadsheet_manager(self):
        """
        Sets up the spreadsheet manager.

        Returns:
            bool: True if the setup is successful, False otherwise.
        """
        try:
            from core.spreadsheet_manager import SpreadsheetManager

            self.spreadsheet_manager = SpreadsheetManager(self.config["spreadsheet"])
            await self.spreadsheet_manager.initialize()

            logger.info("✓ Spreadsheet manager initialized")
            return True

        except Exception as e:
            logger.error(f"Error setting up spreadsheet manager: {e}")
            return False

    async def test_live_data_retrieval(self) -> bool:
        """
        Tests the retrieval of live market data.

        Returns:
            bool: True if data is retrieved successfully, False otherwise.
        """
        try:
            logger.info("\n--- Testing Live Data Retrieval ---")

            symbols = self.config["data_provider"]["symbols"]
            prices = await self.data_provider.get_live_prices(symbols)

            if prices:
                logger.info(f"✓ Retrieved live prices for {len(prices)} symbols")
                for symbol, price_data in prices.items():
                    logger.info(
                        f"  {symbol}: Bid={price_data['bid']}, Ask={price_data['ask']}, Spread={price_data['spread']:.5f}"
                    )
                return True
            else:
                logger.error("✗ No live prices retrieved")
                return False

        except Exception as e:
            logger.error(f"Error testing live data retrieval: {e}")
            return False

    async def test_historical_data_retrieval(self) -> bool:
        """
        Tests the retrieval of historical market data.

        Returns:
            bool: True if data is retrieved successfully, False otherwise.
        """
        try:
            logger.info("\n--- Testing Historical Data Retrieval ---")

            symbol = "EURUSD"
            timeframe = "H1"
            count = 100

            df = await self.data_provider.get_historical_data(symbol, timeframe, count)

            if not df.empty:
                logger.info(
                    f"✓ Retrieved {len(df)} historical bars for {symbol} {timeframe}"
                )
                logger.info(f"  Date range: {df.index[0]} to {df.index[-1]}")
                logger.info(f"  Latest close: {df['close'].iloc[-1]}")
                return True
            else:
                logger.error(f"✗ No historical data retrieved for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error testing historical data retrieval: {e}")
            return False

    async def test_account_summary(self) -> bool:
        """
        Tests the retrieval of the account summary.

        Returns:
            bool: True if the summary is retrieved successfully, False otherwise.
        """
        try:
            logger.info("\n--- Testing Account Summary ---")

            account_summary = await self.data_provider.get_account_summary()

            if account_summary:
                logger.info("✓ Account summary retrieved")
                if "account_info" in account_summary:
                    account_info = account_summary["account_info"]
                    logger.info(
                        f"  Account ID: {account_info.get('account_id', 'N/A')}"
                    )
                    logger.info(
                        f"  Balance: {account_info.get('balance', 0)} {account_info.get('currency', 'USD')}"
                    )
                    logger.info(f"  Equity: {account_info.get('equity', 0)}")

                logger.info(
                    f"  Total Positions: {account_summary.get('total_positions', 0)}"
                )
                logger.info(f"  Total P&L: {account_summary.get('total_pl', 0)}")
                return True
            else:
                logger.error("✗ No account summary retrieved")
                return False

        except Exception as e:
            logger.error(f"Error testing account summary: {e}")
            return False

    async def generate_mock_signals(self) -> List[Dict[str, Any]]:
        """
        Generates a list of mock trading signals for testing purposes.

        Returns:
            List[Dict[str, Any]]: A list of mock signals.
        """
        signals = []
        symbols = self.config["data_provider"]["symbols"]

        # Get current prices
        prices = await self.data_provider.get_live_prices(symbols)

        for i, symbol in enumerate(symbols[:3]):  # Generate signals for first 3 symbols
            if symbol in prices:
                price_data = prices[symbol]

                signal = {
                    "Magic": 1000 + i,
                    "Symbol": symbol,
                    "Action": "BUY" if i % 2 == 0 else "SELL",
                    "Lots": round(0.1 + (i * 0.05), 2),
                    "OpenPrice": price_data["ask"] if i % 2 == 0 else price_data["bid"],
                    "StopLoss": (
                        price_data["ask"] - 0.005
                        if i % 2 == 0
                        else price_data["bid"] + 0.005
                    ),
                    "TakeProfit": (
                        price_data["ask"] + 0.010
                        if i % 2 == 0
                        else price_data["bid"] - 0.010
                    ),
                    "Comment": f"GenX Signal {i+1}",
                    "Confidence": round(0.75 + (i * 0.05), 2),
                    "RiskReward": "1:2",
                    "Timeframe": "H1",
                    "Strategy": "ML_Ensemble",
                    "SignalTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                signals.append(signal)

        logger.info(f"Generated {len(signals)} mock trading signals")
        return signals

    async def test_spreadsheet_output(self) -> bool:
        """
        Tests the generation of spreadsheet output files.

        Returns:
            bool: True if at least one output file is created, False otherwise.
        """
        try:
            logger.info("\n--- Testing Spreadsheet Output ---")

            # Generate mock signals
            signals = await self.generate_mock_signals()

            if not signals:
                logger.error("No signals generated for testing")
                return False

            # Update spreadsheet with signals
            await self.spreadsheet_manager.update_signals(signals)
            logger.info("✓ Signals updated in spreadsheet manager")

            # Check if files were created
            output_dir = Path(self.config["spreadsheet"]["output_directory"])

            expected_files = []
            if self.config["spreadsheet"]["formats"]["excel"]:
                expected_files.append("genx_signals.xlsx")
            if self.config["spreadsheet"]["formats"]["csv"]:
                expected_files.append("genx_signals.csv")
            if self.config["spreadsheet"]["formats"]["json"]:
                expected_files.append("genx_signals.json")
            if self.config["spreadsheet"]["formats"]["mt4_csv"]:
                expected_files.append("MT4_Signals.csv")
            if self.config["spreadsheet"]["formats"]["mt5_csv"]:
                expected_files.append("MT5_Signals.csv")

            created_files = []
            missing_files = []

            for filename in expected_files:
                filepath = output_dir / filename
                if filepath.exists():
                    created_files.append(filename)
                    file_size = filepath.stat().st_size
                    logger.info(f"  ✓ {filename} created ({file_size} bytes)")
                else:
                    missing_files.append(filename)
                    logger.warning(f"  ✗ {filename} not created")

            if created_files:
                logger.info(
                    f"✓ Spreadsheet output test successful - {len(created_files)} files created"
                )
                return True
            else:
                logger.error("✗ No output files created")
                return False

        except Exception as e:
            logger.error(f"Error testing spreadsheet output: {e}")
            return False

    async def test_market_data_to_spreadsheet_flow(self) -> bool:
        """
        Tests the complete flow from retrieving market data to updating the spreadsheet.

        Returns:
            bool: True if the flow completes successfully, False otherwise.
        """
        try:
            logger.info("\n--- Testing Complete Market Data to Spreadsheet Flow ---")

            # Get account summary
            account_summary = await self.data_provider.get_account_summary()

            # Get live market data
            symbols = self.config["data_provider"]["symbols"]
            market_data = await self.data_provider.get_live_prices(symbols)

            # Create market data spreadsheet update
            if self.config["spreadsheet"]["include_market_data"]:
                market_data_signals = []

                for symbol, price_data in market_data.items():
                    market_signal = {
                        "Magic": f"MKT_{symbol}",
                        "Symbol": symbol,
                        "Action": "MARKET_DATA",
                        "Bid": price_data["bid"],
                        "Ask": price_data["ask"],
                        "Spread": price_data["spread"],
                        "Timestamp": price_data["timestamp"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Status": "LIVE",
                    }
                    market_data_signals.append(market_signal)

                # Update spreadsheet with market data
                await self.spreadsheet_manager.update_signals(market_data_signals)
                logger.info(
                    f"✓ Market data updated in spreadsheet ({len(market_data_signals)} symbols)"
                )

            # Add account information if enabled
            if self.config["spreadsheet"]["include_account_info"] and account_summary:
                account_signal = {
                    "Magic": "ACCOUNT_INFO",
                    "Symbol": "ACCOUNT",
                    "Action": "INFO",
                    "Balance": account_summary.get("account_info", {}).get(
                        "balance", 0
                    ),
                    "Equity": account_summary.get("account_info", {}).get("equity", 0),
                    "Margin": account_summary.get("account_info", {}).get("margin", 0),
                    "Positions": account_summary.get("total_positions", 0),
                    "TotalPL": account_summary.get("total_pl", 0),
                    "Status": account_summary.get("connection_status", "unknown"),
                    "LastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                await self.spreadsheet_manager.update_signals([account_signal])
                logger.info("✓ Account information updated in spreadsheet")

            logger.info("✓ Complete market data to spreadsheet flow test successful")
            return True

        except Exception as e:
            logger.error(f"Error testing complete flow: {e}")
            return False

    async def run_comprehensive_test(self, use_mock: bool = True) -> bool:
        """
        Runs a comprehensive integration test of the entire system.

        Args:
            use_mock (bool, optional): Whether to use the mock provider. Defaults to True.

        Returns:
            bool: True if the test is successful, False otherwise.
        """
        logger.info("=== FXCM ForexConnect to Spreadsheet Integration Test ===")
        logger.info(f"Test mode: {'Mock' if use_mock else 'Real'} FXCM connection")
        logger.info(f"Test time: {datetime.now()}")
        print()

        results = []

        # Setup phase
        logger.info("=== SETUP PHASE ===")

        # Setup data provider
        setup_provider = await self.setup_data_provider(use_mock)
        results.append(("Data Provider Setup", setup_provider))

        if not setup_provider:
            logger.error("❌ Data provider setup failed - aborting test")
            return False

        # Setup spreadsheet manager
        setup_spreadsheet = await self.setup_spreadsheet_manager()
        results.append(("Spreadsheet Manager Setup", setup_spreadsheet))

        if not setup_spreadsheet:
            logger.error("❌ Spreadsheet manager setup failed - aborting test")
            return False

        # Testing phase
        logger.info("\n=== TESTING PHASE ===")

        # Test individual components
        live_data_test = await self.test_live_data_retrieval()
        results.append(("Live Data Retrieval", live_data_test))

        historical_data_test = await self.test_historical_data_retrieval()
        results.append(("Historical Data Retrieval", historical_data_test))

        account_test = await self.test_account_summary()
        results.append(("Account Summary", account_test))

        spreadsheet_test = await self.test_spreadsheet_output()
        results.append(("Spreadsheet Output", spreadsheet_test))

        # Test complete flow
        flow_test = await self.test_market_data_to_spreadsheet_flow()
        results.append(("Complete Flow", flow_test))

        # Cleanup
        if self.data_provider:
            await self.data_provider.disconnect()

        # Results summary
        logger.info("\n=== TEST RESULTS SUMMARY ===")
        total_tests = len(results)
        passed_tests = sum(1 for _, result in results if result)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"{test_name}: {status}")

        success_rate = (passed_tests / total_tests) * 100
        logger.info(
            f"\nOverall: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)"
        )

        if success_rate >= 80:
            logger.info("🎉 Integration test SUCCESSFUL!")
            return True
        else:
            logger.error("❌ Integration test FAILED!")
            return False


async def main():
    """
    The main function for the integration test script.
    """
    parser = argparse.ArgumentParser(
        description="FXCM ForexConnect Spreadsheet Integration Test"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use real FXCM connection (requires valid credentials)",
    )
    parser.add_argument(
        "--mock", action="store_true", help="Use mock FXCM connection (default)"
    )

    args = parser.parse_args()

    # Determine test mode
    use_mock = True
    if args.real:
        use_mock = False
        logger.info("Real FXCM connection mode selected")
    elif args.mock:
        use_mock = True
        logger.info("Mock FXCM connection mode selected")
    else:
        # Default to mock if no argument provided
        use_mock = True
        logger.info("Default mock connection mode selected")

    # Run the test
    test_suite = FXCMSpreadsheetIntegrationTest()
    success = await test_suite.run_comprehensive_test(use_mock)

    return 0 if success else 1


if __name__ == "__main__":
    import argparse

    sys.exit(asyncio.run(main()))
