"""
FXCM ForexConnect Provider - Real-time and historical forex data using ForexConnect API
Direct integration with FXCM's ForexConnect trading platform
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import numpy as np
import pandas as pd

# Import ForexConnect (ensure virtual environment is activated)
try:
    import forexconnect as fx

    FOREXCONNECT_AVAILABLE = True
except ImportError:
    FOREXCONNECT_AVAILABLE = False
    logging.warning(
        "ForexConnect module not available. Install with: pip install forexconnect"
    )

logger = logging.getLogger(__name__)

# List of potential server URLs
SERVER_URLS = [
    "http://www.fxcorporate.com/Hosts.jsp",
    "https://www.fxcorporate.com/Hosts.jsp",
    "http://www.fxcm.com/Hosts.jsp",
    "https://www.fxcm.com/Hosts.jsp",
    "http://www.fxcm.co.uk/Hosts.jsp",
    "https://www.fxcm.co.uk/Hosts.jsp",
    "http://www.fxcm.com.au/Hosts.jsp",
    "https://www.fxcm.com.au/Hosts.jsp",
    "http://www.fxcm.fr/Hosts.jsp",
    "https://www.fxcm.fr/Hosts.jsp",
    "http://www.fxcm.de/Hosts.jsp",
    "https://www.fxcm.de/Hosts.jsp",
    "http://www.fxcm.it/Hosts.jsp",
    "https://www.fxcm.it/Hosts.jsp",
    "http://www.fxcm.gr/Hosts.jsp",
    "https://www.fxcm.gr/Hosts.jsp",
    "http://www.fxcm.jp/Hosts.jsp",
    "https://www.fxcm.jp/Hosts.jsp",
]


@dataclass
class FXCMForexConnectConfig:
    """
    Configuration settings for the FXCM ForexConnect API connection.

    Attributes:
        username (str): The login username.
        password (str): The login password.
        connection_type (str): The connection type, "Demo" or "Real".
        url (str): The URL for the connection host list.
        session_id (Optional[str]): An existing session ID to reconnect to.
        pin (Optional[str]): The PIN for the account, if required.
        timeout (int): The connection timeout in seconds.
        retry_attempts (int): The number of times to retry connecting.
        auto_reconnect (bool): Whether to attempt automatic reconnection.
    """

    username: str
    password: str
    connection_type: str = "Demo"
    url: str = "http://fxcorporate.com/Hosts.jsp"
    session_id: Optional[str] = None
    pin: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    auto_reconnect: bool = True
    auto_select_server: bool = False


class FXCMForexConnectProvider:
    """
    Provides real-time and historical market data using the FXCM ForexConnect API.

    This class handles the direct connection to the FXCM platform, data retrieval,
    and account information management.

    Attributes:
        config (FXCMForexConnectConfig): The configuration for the connection.
        forex_connect: The main ForexConnect API object.
        session: The active login session object.
        is_connected (bool): True if the provider is connected.
        last_error (Optional[str]): The last error message encountered.
        price_cache (Dict): A cache for the latest prices.
        historical_cache (Dict): A cache for historical data requests.
        account_info (Optional[Dict]): Information about the connected account.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the FXCMForexConnectProvider.

        Args:
            config (Dict[str, Any]): A dictionary of configuration settings.

        Raises:
            ImportError: If the 'forexconnect' module is not installed.
        """
        if not FOREXCONNECT_AVAILABLE:
            raise ImportError(
                "ForexConnect module not available. Please install it first."
            )

        self.config = FXCMForexConnectConfig(**config)
        self.forex_connect: Optional[fx.ForexConnect] = None
        self.session: Optional[Any] = (
            None  # The type depends on the forexconnect library
        )
        self.is_connected = False
        self.last_error: Optional[str] = None

        # Data caching
        self.price_cache = {}
        self.historical_cache = {}
        self.account_info = None

        # Symbol mapping (standard to FXCM format)
        self.symbol_map = {
            "EURUSD": "EUR/USD",
            "GBPUSD": "GBP/USD",
            "USDJPY": "USD/JPY",
            "USDCHF": "USD/CHF",
            "AUDUSD": "AUD/USD",
            "USDCAD": "USD/CAD",
            "NZDUSD": "NZD/USD",
            "EURGBP": "EUR/GBP",
            "EURJPY": "EUR/JPY",
            "GBPJPY": "GBP/JPY",
        }

        # Timeframe mapping for historical data
        self.timeframe_map = {
            "M1": "m1",
            "M5": "m5",
            "M15": "m15",
            "M30": "m30",
            "H1": "H1",
            "H4": "H4",
            "D1": "D1",
            "W1": "W1",
        }

        logger.info(
            f"FXCM ForexConnect Provider initialized for {self.config.connection_type} environment"
        )

    async def _measure_latency(self, session: aiohttp.ClientSession, url: str) -> float:
        """Measures the latency of a given URL."""
        try:
            start_time = time.monotonic()
            async with session.get(url, timeout=5) as response:
                await response.text()
                end_time = time.monotonic()
                latency = end_time - start_time
                logger.info(
                    f"Successfully connected to {url} with latency: {latency:.4f}s"
                )
                return latency
        except Exception as e:
            logger.warning(f"Failed to connect to {url}: {e}")
            return float("inf")

    async def find_best_server(self) -> str:
        """Finds the best server from a list by measuring latency."""
        async with aiohttp.ClientSession() as session:
            tasks = [self._measure_latency(session, server) for server in SERVER_URLS]
            latencies = await asyncio.gather(*tasks)

        server_latencies = {
            SERVER_URLS[i]: latencies[i] for i in range(len(SERVER_URLS))
        }

        reachable_servers = {
            s: l for s, l in server_latencies.items() if l != float("inf")
        }

        if not reachable_servers:
            logger.error("No reachable servers found.")
            return ""

        best_server = min(reachable_servers, key=reachable_servers.get)
        min_latency = reachable_servers[best_server]
        logger.info(
            f"The best server is {best_server} with a latency of {min_latency:.4f}s"
        )

        return best_server

    async def connect(self) -> bool:
        """
        Establishes a connection to the FXCM platform using the ForexConnect API.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            if not FOREXCONNECT_AVAILABLE:
                logger.error("ForexConnect module not available")
                return False

            logger.info("Connecting to FXCM ForexConnect...")

            connection_url = self.config.url
            if self.config.auto_select_server:
                logger.info("Auto-selecting best server...")
                best_server = await self.find_best_server()
                if best_server:
                    connection_url = best_server
                else:
                    logger.warning(
                        "Could not find best server, falling back to default URL."
                    )

            loop = asyncio.get_event_loop()

            # The forexconnect library is synchronous, so we run it in an executor
            self.forex_connect = await loop.run_in_executor(None, fx.ForexConnect)
            self.session = await loop.run_in_executor(
                None,
                lambda: self.forex_connect.login(
                    user_id=self.config.username,
                    password=self.config.password,
                    url=connection_url,
                    connection=self.config.connection_type,
                    session_id=self.config.session_id,
                    pin=self.config.pin,
                ),
            )

            if self.session:
                self.is_connected = True
                logger.info("Successfully connected to FXCM ForexConnect")
                await self._load_account_info()
                return True
            else:
                logger.error("Failed to connect to FXCM ForexConnect")
                return False

        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error connecting to FXCM ForexConnect: {e}")
            return False

    async def disconnect(self):
        """Disconnects from the FXCM ForexConnect session."""
        try:
            if self.is_connected and self.session:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.session.logout
                )
                logger.info("Disconnected from FXCM ForexConnect")

            self.is_connected = False
            self.session = None
            self.forex_connect = None

        except Exception as e:
            logger.error(f"Error disconnecting from FXCM: {e}")

    async def _load_account_info(self):
        """Loads and caches account information from the trading platform."""
        if not self.is_connected or not self.forex_connect:
            return None
        try:
            accounts_table = await asyncio.get_event_loop().run_in_executor(
                None, self.forex_connect.get_table, self.forex_connect.ACCOUNTS
            )

            if accounts_table and accounts_table.size() > 0:
                account = accounts_table.get_row(0)
                self.account_info = {
                    "account_id": account.account_id,
                    "balance": float(account.balance),
                    "currency": account.account_currency,
                    "equity": float(getattr(account, "equity", account.balance)),
                    "margin": float(getattr(account, "used_margin", 0)),
                    "free_margin": float(
                        getattr(account, "usable_margin", account.balance)
                    ),
                }
                logger.info(
                    f"Account loaded: {self.account_info['account_id']} - "
                    f"Balance: {self.account_info['balance']} {self.account_info['currency']}"
                )
                return self.account_info
            else:
                logger.warning("No account information available")
                return None

        except Exception as e:
            logger.error(f"Error loading account info: {e}")
            return None

    async def get_live_prices(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Gets live prices for a list of specified symbols.

        Args:
            symbols (List[str]): A list of standard symbols (e.g., 'EURUSD').

        Returns:
            Dict[str, Dict[str, float]]: A dictionary mapping each symbol to its
                                         price data (bid, ask, spread, etc.).
        """
        if not self.is_connected or not self.forex_connect:
            logger.warning("Not connected to FXCM")
            return {}
        try:
            prices = {}
            offers_table = await asyncio.get_event_loop().run_in_executor(
                None, self.forex_connect.get_table, self.forex_connect.OFFERS
            )

            if not offers_table:
                logger.warning("No offers table available")
                return {}

            # Create a set of FXCM symbols for efficient lookup
            fxcm_symbols_needed = {self.symbol_map.get(s, s) for s in symbols}
            symbol_reverse_map = {v: k for k, v in self.symbol_map.items()}

            for i in range(offers_table.size()):
                offer = offers_table.get_row(i)
                if offer.instrument in fxcm_symbols_needed:
                    standard_symbol = symbol_reverse_map.get(
                        offer.instrument, offer.instrument
                    )
                    prices[standard_symbol] = {
                        "bid": float(offer.bid),
                        "ask": float(offer.ask),
                        "spread": float(offer.ask - offer.bid),
                        "timestamp": datetime.now(),
                        "symbol": standard_symbol,
                    }

            self.price_cache.update(prices)
            return prices

        except Exception as e:
            logger.error(f"Error getting live prices: {e}")
            return {}

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        count: int = 1000,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Gets historical price data for a symbol and timeframe.

        Args:
            symbol (str): The standard symbol.
            timeframe (str): The timeframe (e.g., 'M15', 'H1').
            count (int): The number of candles to retrieve.
            start_date (Optional[datetime]): The start date of the data range.
            end_date (Optional[datetime]): The end date of the data range.

        Returns:
            pd.DataFrame: A DataFrame containing the historical OHLCV data.
        """
        if not self.is_connected or not self.forex_connect:
            logger.warning("Not connected to FXCM")
            return pd.DataFrame()
        try:
            fxcm_symbol = self.symbol_map.get(symbol, symbol)
            fxcm_timeframe = self.timeframe_map.get(timeframe, timeframe)

            history = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.forex_connect.get_history(
                    instrument=fxcm_symbol, timeframe=fxcm_timeframe, count=count
                ),
            )

            if not history or len(history) == 0:
                logger.warning(f"No historical data for {symbol} {timeframe}")
                return pd.DataFrame()

            data = [
                {
                    "timestamp": bar.date,
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": int(getattr(bar, "volume", 0)),
                }
                for bar in history
            ]

            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp").sort_index()

            cache_key = f"{symbol}_{timeframe}_{count}"
            self.historical_cache[cache_key] = df
            logger.info(f"Retrieved {len(df)} historical bars for {symbol} {timeframe}")
            return df

        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()

    async def get_account_summary(self) -> Dict[str, Any]:
        """
        Gets a summary of the account, including balance and open positions.

        Returns:
            Dict[str, Any]: A dictionary containing the account summary.
        """
        if not self.is_connected or not self.forex_connect:
            return {}
        try:
            if not self.account_info:
                await self._load_account_info()

            trades_table = await asyncio.get_event_loop().run_in_executor(
                None, self.forex_connect.get_table, self.forex_connect.TRADES
            )
            positions = []

            if trades_table:
                for i in range(trades_table.size()):
                    trade = trades_table.get_row(i)
                    positions.append(
                        {
                            "symbol": trade.instrument,
                            "side": "buy" if trade.buy_sell == "B" else "sell",
                            "amount": float(trade.amount),
                            "open_price": float(trade.open_rate),
                            "current_price": float(trade.close),
                            "pl": float(trade.pl),
                            "trade_id": trade.trade_id,
                        }
                    )

            return {
                "account_info": self.account_info or {},
                "positions": positions,
                "total_positions": len(positions),
                "total_pl": sum(pos["pl"] for pos in positions),
                "connection_status": (
                    "connected" if self.is_connected else "disconnected"
                ),
                "last_update": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}

    async def health_check(self) -> bool:
        """
        Checks if the connection to the FXCM server is healthy.

        Returns:
            bool: True if the connection is active and responsive, False otherwise.
        """
        if not self.is_connected or not self.forex_connect:
            return False
        try:
            # A simple test to see if we can still get data
            offers_table = await asyncio.get_event_loop().run_in_executor(
                None, self.forex_connect.get_table, self.forex_connect.OFFERS
            )
            return offers_table is not None

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_supported_symbols(self) -> List[str]:
        """Gets the list of standard symbols supported by this provider."""
        return list(self.symbol_map.keys())

    def get_supported_timeframes(self) -> List[str]:
        """Gets the list of standard timeframes supported by this provider."""
        return list(self.timeframe_map.keys())


class MockFXCMForexConnectProvider(FXCMForexConnectProvider):
    """
    A mock version of the FXCMForexConnectProvider for testing and development.

    This class simulates the behavior of the real provider without making actual
    network calls or requiring the ForexConnect library.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the MockFXCMForexConnectProvider.

        Args:
            config (Dict[str, Any]): Configuration settings.
        """
        # Intentionally skip the parent's __init__ to avoid ForexConnect dependency
        self.config = FXCMForexConnectConfig(**config)
        self.forex_connect = None
        self.session = None
        self.is_connected = False
        self.last_error = None

        # Mock data
        self.price_cache = {}
        self.historical_cache = {}
        self.account_info = {
            "account_id": "MOCK123456",
            "balance": 50000.0,
            "currency": "USD",
            "equity": 50000.0,
            "margin": 0.0,
            "free_margin": 50000.0,
        }

        # Same mappings as real provider
        self.symbol_map = {
            "EURUSD": "EUR/USD",
            "GBPUSD": "GBP/USD",
            "USDJPY": "USD/JPY",
            "USDCHF": "USD/CHF",
            "AUDUSD": "AUD/USD",
            "USDCAD": "USD/CAD",
            "NZDUSD": "NZD/USD",
        }

        self.timeframe_map = {
            "M1": "m1",
            "M5": "m5",
            "M15": "m15",
            "M30": "m30",
            "H1": "H1",
            "H4": "H4",
            "D1": "D1",
            "W1": "W1",
        }

        logger.info("Mock FXCM ForexConnect Provider initialized")

    async def connect(self) -> bool:
        """Simulates a successful connection."""
        self.is_connected = True
        logger.info("Mock FXCM ForexConnect connected successfully")
        return True

    async def disconnect(self):
        """Simulates a disconnection."""
        self.is_connected = False
        logger.info("Mock FXCM ForexConnect disconnected")

    async def get_live_prices(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Generates mock live prices for a list of symbols.

        Args:
            symbols (List[str]): The symbols to generate prices for.

        Returns:
            Dict[str, Dict[str, float]]: A dictionary of mock price data.
        """
        import random

        prices = {}
        base_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 148.50,
            "USDCHF": 0.8950,
            "AUDUSD": 0.6580,
            "USDCAD": 1.3620,
            "NZDUSD": 0.6120,
        }

        for symbol in symbols:
            if symbol in base_prices:
                base_price = base_prices[symbol]
                spread = 0.0002 if "JPY" not in symbol else 0.02

                # Add some random variation
                variation = random.uniform(-0.001, 0.001)
                mid_price = base_price + variation

                prices[symbol] = {
                    "bid": round(mid_price - spread / 2, 5),
                    "ask": round(mid_price + spread / 2, 5),
                    "spread": spread,
                    "timestamp": datetime.now(),
                    "symbol": symbol,
                }

        self.price_cache.update(prices)
        return prices

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        count: int = 1000,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Generates a DataFrame of mock historical data.

        Args:
            symbol (str): The symbol for which to generate data.
            timeframe (str): The timeframe for the data.
            count (int): The number of candles to generate.
            start_date (Optional[datetime]): The start date (not used in mock).
            end_date (Optional[datetime]): The end date (not used in mock).

        Returns:
            pd.DataFrame: A DataFrame with mock OHLCV data.
        """
        import random

        base_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 148.50,
            "USDCHF": 0.8950,
            "AUDUSD": 0.6580,
            "USDCAD": 1.3620,
            "NZDUSD": 0.6120,
        }

        if symbol not in base_prices:
            return pd.DataFrame()

        # Generate mock data
        data = []
        current_price = base_prices[symbol]
        current_time = datetime.now() - timedelta(minutes=count)

        for i in range(count):
            # Random walk
            change = random.gauss(0, 0.001)
            current_price += change

            # Generate OHLC
            high = current_price + random.uniform(0, 0.002)
            low = current_price - random.uniform(0, 0.002)
            open_price = current_price + random.uniform(-0.001, 0.001)
            close_price = current_price + random.uniform(-0.001, 0.001)

            data.append(
                {
                    "timestamp": current_time + timedelta(minutes=i),
                    "open": round(open_price, 5),
                    "high": round(high, 5),
                    "low": round(low, 5),
                    "close": round(close_price, 5),
                    "volume": random.randint(10, 1000),
                }
            )

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        return df

    async def health_check(self) -> bool:
        """Simulates a health check; returns the connection status."""
        return self.is_connected
