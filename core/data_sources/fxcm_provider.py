"""
FXCM Data Provider - Real-time and historical forex data
Handles connection to FXCM's REST API and WebSocket feeds
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import numpy as np
import pandas as pd
import websockets

logger = logging.getLogger(__name__)


@dataclass
class FXCMConfig:
    """
    Configuration settings for the FXCM REST API and WebSocket connection.

    Attributes:
        access_token (str): The bearer token for authentication.
        environment (str): The trading environment, "demo" or "real".
        server_url (str): The base URL for the REST API.
        socket_url (str): The URL for the WebSocket connection.
        timeout (int): The request timeout in seconds.
        retry_attempts (int): The number of times to retry a failed connection.
        rate_limit_delay (float): The delay in seconds between requests to respect rate limits.
    """

    access_token: str
    environment: str = "demo"
    server_url: str = "https://api-fxpractice.fxcm.com"
    socket_url: str = "wss://api-fxpractice.fxcm.com/socket.io/"
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit_delay: float = 0.1
    use_mock: bool = False
    refresh_interval: int = 60
    reconnect_on_failure: bool = True
    max_reconnect_attempts: int = 5


class FXCMDataProvider:
    """
    Provides real-time and historical market data from FXCM via REST and WebSocket APIs.

    This class handles connection, authentication, data fetching, and subscription
    management for the FXCM platform.

    Attributes:
        config (FXCMConfig): The configuration for the provider.
        session (Optional[aiohttp.ClientSession]): The aiohttp session for REST requests.
        websocket (Optional[websockets.WebSocketClientProtocol]): The WebSocket connection.
        is_connected (bool): True if the provider is connected and authenticated.
        subscriptions (Dict): A dictionary of active symbol subscriptions.
        data_cache (Dict): A cache for historical data.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the FXCMDataProvider.

        Args:
            config (Dict[str, Any]): A dictionary of configuration settings.
        """
        self.config = FXCMConfig(**config)
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.client.WebSocketClientProtocol] = None
        self.is_connected = False
        self.subscriptions: Dict[str, Any] = {}
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.last_request_time: float = 0

        # Symbol mapping (FXCM format to standard format)
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

        # Timeframe mapping
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
            f"FXCM Data Provider initialized for {self.config.environment} environment"
        )

    async def connect(self) -> bool:
        """
        Establishes and authenticates the connection to the FXCM API.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )

            if await self._authenticate():
                self.is_connected = True
                logger.info("Successfully connected to FXCM API")
                return True
            else:
                logger.error("Failed to authenticate with FXCM API")
                await self.session.close()
                return False

        except Exception as e:
            logger.error(f"Error connecting to FXCM: {e}")
            if self.session:
                await self.session.close()
            return False

    async def disconnect(self):
        """Disconnects from the FXCM API by closing the session and WebSocket."""
        try:
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()

            if self.session and not self.session.closed:
                await self.session.close()

            self.is_connected = False
            logger.info("Disconnected from FXCM API")

        except Exception as e:
            logger.error(f"Error disconnecting from FXCM: {e}")

    async def _authenticate(self) -> bool:
        """
        Authenticates with the FXCM API by making a test request.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        if not self.session:
            return False
        try:
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }
            url = f"{self.config.server_url}/trading/get_model"

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    logger.info("FXCM authentication successful")
                    return True
                else:
                    logger.error(f"FXCM authentication failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error during FXCM authentication: {e}")
            return False

    async def _rate_limit(self):
        """Implements a simple rate-limiting mechanism to avoid API request limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.config.rate_limit_delay:
            await asyncio.sleep(self.config.rate_limit_delay - time_since_last)

        self.last_request_time = time.time()

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        periods: int = 100,
        end_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Gets historical market data from FXCM.

        Args:
            symbol (str): The standard currency pair (e.g., 'EURUSD').
            timeframe (str): The candle timeframe (e.g., 'H1', 'M15').
            periods (int): The number of historical periods to retrieve.
            end_time (Optional[datetime]): The end time for the historical data.

        Returns:
            pd.DataFrame: A DataFrame containing the OHLCV data.

        Raises:
            ConnectionError: If the service is not connected.
            Exception: If the API request fails.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        await self._rate_limit()

        try:
            # Convert symbol and timeframe to FXCM format
            fxcm_symbol = self.symbol_map.get(symbol, symbol)
            fxcm_timeframe = self.timeframe_map.get(timeframe, timeframe)

            # Prepare parameters
            params = {
                "instrument": fxcm_symbol,
                "periodicity": fxcm_timeframe,
                "num": periods,
            }

            if end_time:
                params["end"] = end_time.strftime("%Y-%m-%d %H:%M:%S")

            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }

            url = f"{self.config.server_url}/candles"

            async with self.session.get(
                url, headers=headers, params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_historical_data(data, symbol)
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Error getting historical data for {symbol}: {response.status} - {error_text}"
                    )
                    raise Exception(f"API error: {response.status}")

        except Exception as e:
            logger.error(f"Error getting historical data for {symbol} {timeframe}: {e}")

            # Return cached data if available
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.data_cache:
                logger.warning(f"Returning cached data for {symbol} {timeframe}")
                return self.data_cache[cache_key]

            # Return empty DataFrame if no cached data
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

    def _process_historical_data(self, raw_data: Dict, symbol: str) -> pd.DataFrame:
        """
        Processes raw historical data from FXCM into a standardized DataFrame.

        Args:
            raw_data (Dict): The raw JSON response from the API.
            symbol (str): The symbol for which the data was fetched.

        Returns:
            pd.DataFrame: A formatted DataFrame with a timestamp index.
        """
        try:
            if "candles" not in raw_data or not raw_data["candles"]:
                logger.warning(f"No candle data received for {symbol}")
                return pd.DataFrame(
                    columns=["timestamp", "open", "high", "low", "close", "volume"]
                )

            candles = raw_data["candles"]

            # Extract data
            data = []
            for candle in candles:
                data.append(
                    {
                        "timestamp": pd.to_datetime(candle["timestamp"]),
                        "open": float(candle["bidopen"]),
                        "high": float(candle["bidhigh"]),
                        "low": float(candle["bidlow"]),
                        "close": float(candle["bidclose"]),
                        "volume": float(candle.get("tickqty", 0)),
                    }
                )

            # Create DataFrame
            df = pd.DataFrame(data)
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)

            # Cache the data
            cache_key = f"{symbol}_{len(df)}"
            self.data_cache[cache_key] = df.copy()

            logger.debug(f"Processed {len(df)} candles for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Error processing historical data for {symbol}: {e}")
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

    async def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Gets the current bid/ask price for a single symbol.

        Args:
            symbol (str): The standard symbol to fetch the price for.

        Returns:
            Optional[Dict[str, float]]: A dictionary with price data or None if not found.

        Raises:
            ConnectionError: If the service is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        await self._rate_limit()

        try:
            fxcm_symbol = self.symbol_map.get(symbol, symbol)

            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }

            url = f"{self.config.server_url}/trading/get_instruments"

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Find the symbol in the instruments list
                    for instrument in data.get("instruments", []):
                        if instrument.get("instrument") == fxcm_symbol:
                            return {
                                "bid": float(instrument.get("bid", 0)),
                                "ask": float(instrument.get("ask", 0)),
                                "spread": float(instrument.get("spread", 0)),
                                "timestamp": datetime.now(),
                            }

                    logger.warning(f"Symbol {symbol} not found in instruments")
                    return None
                else:
                    logger.error(
                        f"Error getting current price for {symbol}: {response.status}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

    async def get_market_status(self) -> Dict[str, Any]:
        """
        Gets the current market status and account-related information.

        Returns:
            Dict[str, Any]: A dictionary containing market and account status.

        Raises:
            ConnectionError: If the service is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        try:
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }

            url = f"{self.config.server_url}/trading/get_model"

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "market_open": data.get("isTradingAllowed", False),
                        "server_time": data.get(
                            "serverTime", datetime.now().isoformat()
                        ),
                        "equity": data.get("equity", 0),
                        "balance": data.get("balance", 0),
                        "margin_available": data.get("marginAvailable", 0),
                    }
                else:
                    logger.error(f"Error getting market status: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {}

    async def get_available_symbols(self) -> List[str]:
        """
        Gets a list of all available trading symbols from the platform.

        Returns:
            List[str]: A list of standard-format symbols.

        Raises:
            ConnectionError: If the service is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        try:
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }

            url = f"{self.config.server_url}/trading/get_instruments"

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    symbols = []

                    for instrument in data.get("instruments", []):
                        fxcm_symbol = instrument.get("instrument", "")
                        # Convert back to standard format
                        standard_symbol = None
                        for std, fxcm in self.symbol_map.items():
                            if fxcm == fxcm_symbol:
                                standard_symbol = std
                                break

                        if standard_symbol:
                            symbols.append(standard_symbol)
                        else:
                            symbols.append(fxcm_symbol.replace("/", ""))

                    return symbols
                else:
                    logger.error(f"Error getting available symbols: {response.status}")
                    return list(self.symbol_map.keys())

        except Exception as e:
            logger.error(f"Error getting available symbols: {e}")
            return list(self.symbol_map.keys())

    async def subscribe_to_price_updates(
        self, symbols: List[str], callback: Optional[Callable] = None
    ):
        """
        Subscribes to real-time price updates for a list of symbols.

        Note: This is a placeholder for a full WebSocket implementation.

        Args:
            symbols (List[str]): The symbols to subscribe to.
            callback (Optional[Callable]): A function to call with price updates.

        Raises:
            ConnectionError: If the service is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        try:
            # This would implement WebSocket subscription for real-time data
            # FXCM's WebSocket implementation varies, so this is a simplified version
            logger.info(f"Subscribing to price updates for: {symbols}")

            for symbol in symbols:
                self.subscriptions[symbol] = {
                    "callback": callback,
                    "last_update": datetime.now(),
                }

            logger.info(f"Subscribed to {len(symbols)} symbols")

        except Exception as e:
            logger.error(f"Error subscribing to price updates: {e}")

    async def unsubscribe_from_price_updates(self, symbols: List[str]):
        """
        Unsubscribes from real-time price updates for a list of symbols.

        Args:
            symbols (List[str]): The symbols to unsubscribe from.
        """
        try:
            for symbol in symbols:
                if symbol in self.subscriptions:
                    del self.subscriptions[symbol]

            logger.info(f"Unsubscribed from {len(symbols)} symbols")

        except Exception as e:
            logger.error(f"Error unsubscribing from price updates: {e}")

    async def get_account_summary(self) -> Dict[str, Any]:
        """
        Gets a summary of the trading account.

        Returns:
            Dict[str, Any]: A dictionary with account summary details.

        Raises:
            ConnectionError: If the service is not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        try:
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }

            url = f"{self.config.server_url}/trading/get_model"

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "account_id": data.get("accountId", ""),
                        "balance": float(data.get("balance", 0)),
                        "equity": float(data.get("equity", 0)),
                        "margin_used": float(data.get("usableMargin", 0)),
                        "margin_available": float(data.get("marginAvailable", 0)),
                        "currency": data.get("accountCurrency", "USD"),
                        "leverage": data.get("leverage", 1),
                        "is_trading_allowed": data.get("isTradingAllowed", False),
                    }
                else:
                    logger.error(f"Error getting account summary: {response.status}")
                    return {}

        except Exception as e:
            logger.error(f"Error getting account summary: {e}")
            return {}

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Gets the current status of the connection and provider.

        Returns:
            Dict[str, Any]: A dictionary containing connection status details.
        """
        return {
            "connected": self.is_connected,
            "environment": self.config.environment,
            "server_url": self.config.server_url,
            "last_request_time": self.last_request_time,
            "cached_symbols": len(self.data_cache),
            "active_subscriptions": len(self.subscriptions),
        }

    async def test_connection(self) -> bool:
        """
        Tests the connection to the FXCM API by fetching account summary.

        Returns:
            bool: True if the connection is responsive, False otherwise.
        """
        try:
            if not self.is_connected:
                return False

            # Try to get account summary as a connection test
            account_data = await self.get_account_summary()
            return bool(account_data)

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Alternative data provider for when FXCM is not available
class MockFXCMProvider(FXCMDataProvider):
    """A mock version of the FXCMDataProvider for testing and development."""

    def __init__(self, config: Dict[str, Any]):
        """Initializes the MockFXCMProvider."""
        super().__init__(config)
        self.is_connected = True
        logger.info("Mock FXCM Provider initialized")

    async def connect(self) -> bool:
        """Simulates a successful connection."""
        self.is_connected = True
        logger.info("Mock FXCM connection established")
        return True

    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str,
        periods: int = 100,
        end_time: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Generates a DataFrame with mock historical data.

        Args:
            symbol (str): The symbol for which to generate data.
            timeframe (str): The data timeframe.
            periods (int): The number of periods to generate.
            end_time (Optional[datetime]): The end time for the data series.

        Returns:
            pd.DataFrame: A DataFrame containing mock OHLCV data.
        """

        # Generate realistic forex data
        np.random.seed(42)  # For reproducible data

        end_time = end_time or datetime.now()

        # Calculate time intervals based on timeframe
        if timeframe == "M1":
            delta = timedelta(minutes=1)
        elif timeframe == "M5":
            delta = timedelta(minutes=5)
        elif timeframe == "M15":
            delta = timedelta(minutes=15)
        elif timeframe == "H1":
            delta = timedelta(hours=1)
        elif timeframe == "H4":
            delta = timedelta(hours=4)
        else:  # D1
            delta = timedelta(days=1)

        # Generate timestamps
        timestamps = [end_time - delta * i for i in range(periods)]
        timestamps.reverse()

        # Generate price data (starting around typical forex rates)
        base_prices = {
            "EURUSD": 1.1000,
            "GBPUSD": 1.3000,
            "USDJPY": 110.00,
            "USDCHF": 0.9200,
            "AUDUSD": 0.7500,
            "USDCAD": 1.2500,
            "NZDUSD": 0.7000,
        }

        base_price = base_prices.get(symbol, 1.0000)

        # Generate realistic price movements
        returns = np.random.normal(0, 0.001, periods)  # 0.1% daily volatility
        prices = [base_price]

        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)

        # Generate OHLC data
        data = []
        for i, timestamp in enumerate(timestamps):
            price = prices[i]
            volatility = abs(np.random.normal(0, 0.0005))  # Random volatility

            high = price * (1 + volatility)
            low = price * (1 - volatility)
            open_price = price * (1 + np.random.normal(0, 0.0002))

            data.append(
                {
                    "timestamp": timestamp,
                    "open": round(open_price, 5),
                    "high": round(high, 5),
                    "low": round(low, 5),
                    "close": round(price, 5),
                    "volume": np.random.randint(100, 1000),
                }
            )

        df = pd.DataFrame(data)
        df.set_index("timestamp", inplace=True)

        return df

    async def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Generates a mock current price for a symbol.

        Args:
            symbol (str): The symbol to get a price for.

        Returns:
            Optional[Dict[str, float]]: A dictionary with mock price data.
        """
        base_prices = {
            "EURUSD": 1.1000,
            "GBPUSD": 1.3000,
            "USDJPY": 110.00,
            "USDCHF": 0.9200,
            "AUDUSD": 0.7500,
            "USDCAD": 1.2500,
            "NZDUSD": 0.7000,
        }

        base_price = base_prices.get(symbol, 1.0000)
        spread = base_price * 0.00002  # 2 pip spread

        return {
            "bid": round(base_price - spread / 2, 5),
            "ask": round(base_price + spread / 2, 5),
            "spread": round(spread, 5),
            "timestamp": datetime.now(),
        }
