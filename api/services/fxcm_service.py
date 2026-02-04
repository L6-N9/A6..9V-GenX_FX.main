"""
FXCM REST API Service for real-time market data and trading operations.
Provides WebSocket connections for live data streaming and REST API for historical data.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import pandas as pd
import websockets

from ..config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class FXCMCredentials:
    """
    Holds the credentials and configuration for connecting to the FXCM API.

    Attributes:
        api_key (str): The API key for authentication.
        access_token (str): The access token for the session.
        account_id (str): The ID of the trading account.
        environment (str): The trading environment, "demo" or "real".
    """

    api_key: str
    access_token: str
    account_id: str
    environment: str = "demo"  # "demo" or "real"

    @property
    def base_url(self) -> str:
        """
        Gets the base REST API URL based on the environment.

        Note: The URLs provided seem to be for OANDA, not FXCM. This might be a bug.
        """
        if self.environment == "demo":
            return "https://api-fxpractice.oanda.com"  # This is an OANDA URL
        return "https://api-fxtrade.oanda.com"  # This is an OANDA URL

    @property
    def websocket_url(self) -> str:
        """
        Gets the WebSocket URL for streaming data based on the environment.

        Note: The URLs provided seem to be for OANDA, not FXCM. This might be a bug.
        """
        if self.environment == "demo":
            return "wss://stream-fxpractice.oanda.com"  # This is an OANDA URL
        return "wss://stream-fxtrade.oanda.com"  # This is an OANDA URL


@dataclass
class MarketData:
    """
    Represents a snapshot of market data for an instrument.

    Attributes:
        instrument (str): The trading instrument.
        bid (float): The current bid price.
        ask (float): The current ask price.
        spread (float): The difference between ask and bid.
        timestamp (datetime): The timestamp of the data point.
        volume (Optional[int]): The trading volume, if available.
    """

    instrument: str
    bid: float
    ask: float
    spread: float
    timestamp: datetime
    volume: Optional[int] = None

    @property
    def mid_price(self) -> float:
        """Calculates the mid-price."""
        return (self.bid + self.ask) / 2


@dataclass
class Candle:
    """
    Represents a single OHLCV (Open, High, Low, Close, Volume) candlestick.

    Attributes:
        instrument (str): The trading instrument.
        timestamp (datetime): The start time of the candle.
        open (float): The opening price.
        high (float): The highest price during the candle's duration.
        low (float): The lowest price during the candle's duration.
        close (float): The closing price.
        volume (int): The trading volume during the candle's duration.
        timeframe (str): The timeframe of the candle (e.g., "M15", "H1").
    """

    instrument: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    timeframe: str


@dataclass
class TradeSignal:
    """
    Represents a trading signal to be executed.

    Attributes:
        instrument (str): The instrument to trade.
        action (str): The action to take ("BUY", "SELL", "CLOSE").
        volume (float): The volume or lot size of the trade.
        stop_loss (Optional[float]): The stop-loss price.
        take_profit (Optional[float]): The take-profit price.
        confidence (float): The confidence level of the signal.
        timestamp (datetime): The time the signal was generated.
    """

    instrument: str
    action: str  # "BUY", "SELL", "CLOSE"
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 0.0
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Sets the timestamp to now if it's not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class FXCMService:
    """
    Service for interacting with the FXCM (or OANDA, based on URLs) API.

    Provides methods for fetching historical data, streaming real-time prices,
    placing orders, and getting account information.

    Attributes:
        credentials (FXCMCredentials): The credentials for API access.
        session (Optional[aiohttp.ClientSession]): The aiohttp session for REST requests.
        websocket (Optional[websockets.WebSocketClientProtocol]): The WebSocket connection.
        is_connected (bool): True if the service is connected.
        subscribers (Dict[str, List[Callable]]): A dictionary of callbacks for events.
    """

    def __init__(self, credentials: FXCMCredentials):
        """
        Initializes the FXCMService.

        Args:
            credentials (FXCMCredentials): The credentials and configuration.
        """
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.client.WebSocketClientProtocol] = None
        self.is_connected = False
        self.subscribers: Dict[str, List[Callable]] = {
            "price": [],
            "candle": [],
            "trade": [],
        }

    async def __aenter__(self):
        """Asynchronous context manager entry to connect the service."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous context manager exit to disconnect the service."""
        await self.disconnect()

    async def connect(self):
        """
        Establishes and tests the connection to the API.

        Initializes an aiohttp session and performs a test connection to
        validate credentials.

        Raises:
            Exception: If the connection fails.
        """
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.credentials.access_token}",
                    "Content-Type": "application/json",
                }
            )

            # Test connection
            await self._test_connection()
            self.is_connected = True
            logger.info("Successfully connected to FXCM API")

        except Exception as e:
            logger.error(f"Failed to connect to FXCM API: {e}")
            raise

    async def disconnect(self):
        """Closes the WebSocket and aiohttp session."""
        try:
            if self.websocket:
                await self.websocket.close()

            if self.session:
                await self.session.close()

            self.is_connected = False
            logger.info("Disconnected from FXCM API")

        except Exception as e:
            logger.error(f"Error disconnecting from FXCM API: {e}")

    async def _test_connection(self):
        """
        Tests the API connection by fetching account details.

        Raises:
            Exception: If the test request fails.
        """
        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}"

        async with self.session.get(url) as response:
            if response.status != 200:
                raise ConnectionError(
                    f"Failed to connect to FXCM API: {response.status}"
                )

            data = await response.json()
            logger.info(f"Connected to account: {data.get('account', {}).get('id')}")

    async def get_historical_data(
        self,
        instrument: str,
        timeframe: str = "M15",
        count: int = 1000,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Candle]:
        """
        Fetches historical candlestick data from the API.

        Args:
            instrument (str): The trading instrument (e.g., "EUR_USD").
            timeframe (str): The candle timeframe (e.g., "M15", "H1", "D").
            count (int): The number of candles to fetch.
            start_time (Optional[datetime]): The start time for the data range.
            end_time (Optional[datetime]): The end time for the data range.

        Returns:
            List[Candle]: A list of Candle objects.

        Raises:
            ConnectionError: If the service is not connected.
            Exception: If the API request fails.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        url = f"{self.credentials.base_url}/v3/instruments/{instrument}/candles"

        params = {"granularity": timeframe, "count": count}

        if start_time:
            params["from"] = start_time.isoformat() + "Z"
        if end_time:
            params["to"] = end_time.isoformat() + "Z"

        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to fetch historical data: {response.status}"
                    )

                data = await response.json()
                candles = []

                for candle_data in data.get("candles", []):
                    if candle_data["complete"]:
                        candles.append(
                            Candle(
                                instrument=instrument,
                                timestamp=datetime.fromisoformat(
                                    candle_data["time"].replace("Z", "+00:00")
                                ),
                                open=float(candle_data["mid"]["o"]),
                                high=float(candle_data["mid"]["h"]),
                                low=float(candle_data["mid"]["l"]),
                                close=float(candle_data["mid"]["c"]),
                                volume=int(candle_data["volume"]),
                                timeframe=timeframe,
                            )
                        )

                logger.info(f"Fetched {len(candles)} candles for {instrument}")
                return candles

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise

    async def get_current_prices(self, instruments: List[str]) -> Dict[str, MarketData]:
        """
        Gets the current bid/ask prices for a list of instruments.

        Args:
            instruments (List[str]): A list of trading instruments.

        Returns:
            Dict[str, MarketData]: A dictionary mapping each instrument to its market data.

        Raises:
            ConnectionError: If the service is not connected.
            Exception: If the API request fails.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}/pricing"

        params = {"instruments": ",".join(instruments)}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to fetch current prices: {response.status}"
                    )

                data = await response.json()
                prices = {}

                for price_data in data.get("prices", []):
                    instrument = price_data["instrument"]
                    prices[instrument] = MarketData(
                        instrument=instrument,
                        bid=float(price_data["bids"][0]["price"]),
                        ask=float(price_data["asks"][0]["price"]),
                        spread=float(price_data["asks"][0]["price"])
                        - float(price_data["bids"][0]["price"]),
                        timestamp=datetime.fromisoformat(
                            price_data["time"].replace("Z", "+00:00")
                        ),
                    )

                return prices

        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            raise

    async def start_price_stream(self, instruments: List[str]):
        """
        Starts a real-time price stream using a WebSocket connection.

        This method connects to the WebSocket and enters a loop to listen for
        and handle incoming price updates.

        Args:
            instruments (List[str]): A list of instruments to subscribe to for streaming.

        Raises:
            Exception: If the WebSocket connection or message handling fails.
        """
        try:
            ws_url = f"{self.credentials.websocket_url}/v3/accounts/{self.credentials.account_id}/pricing/stream"

            headers = {"Authorization": f"Bearer {self.credentials.access_token}"}

            params = f"instruments={','.join(instruments)}"
            full_url = f"{ws_url}?{params}"

            self.websocket = await websockets.connect(full_url, extra_headers=headers)

            logger.info(f"Started price streaming for: {', '.join(instruments)}")

            # Listen for incoming messages
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_price_update(data)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse WebSocket message: {message}")
                except Exception as e:
                    logger.error(f"Error handling price update: {e}")

        except Exception as e:
            logger.error(f"Error in price streaming: {e}")
            raise

    async def _handle_price_update(self, data: Dict[str, Any]):
        """
        Handles an incoming price update from the WebSocket.

        Parses the message and notifies all registered price subscribers.

        Args:
            data (Dict[str, Any]): The decoded JSON data from the WebSocket message.
        """
        if data.get("type") == "PRICE":
            instrument = data.get("instrument")
            bids = data.get("bids", [])
            asks = data.get("asks", [])

            if bids and asks:
                market_data = MarketData(
                    instrument=instrument,
                    bid=float(bids[0]["price"]),
                    ask=float(asks[0]["price"]),
                    spread=float(asks[0]["price"]) - float(bids[0]["price"]),
                    timestamp=datetime.fromisoformat(
                        data["time"].replace("Z", "+00:00")
                    ),
                )

                # Notify all price subscribers
                for callback in self.subscribers["price"]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(market_data)
                        else:
                            callback(market_data)
                    except Exception as e:
                        logger.error(f"Error in price callback: {e}")

    def subscribe_to_prices(self, callback: Callable[[MarketData], Any]):
        """
        Subscribes a callback function to receive real-time price updates.

        Args:
            callback: A function or coroutine to be called with a MarketData object.
        """
        self.subscribers["price"].append(callback)

    def subscribe_to_candles(self, callback: Callable[[Candle], Any]):
        """
        Subscribes a callback function to receive new candle formations.

        Args:
            callback: A function or coroutine to be called with a Candle object.
        """
        self.subscribers["candle"].append(callback)

    def subscribe_to_trades(self, callback: Callable[[Dict], Any]):
        """
        Subscribes a callback function to receive trade execution updates.

        Args:
            callback: A function or coroutine to be called with trade update data.
        """
        self.subscribers["trade"].append(callback)

    async def place_order(self, signal: TradeSignal) -> Dict[str, Any]:
        """
        Places a trading order based on a provided signal.

        Args:
            signal (TradeSignal): An object containing the order details.

        Returns:
            Dict[str, Any]: The JSON response from the API after placing the order.

        Raises:
            ConnectionError: If the service is not connected.
            Exception: If the order placement fails.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}/orders"

        # Convert signal to FXCM order format
        order_data = {
            "order": {
                "instrument": signal.instrument,
                "units": (
                    int(signal.volume * 10000)
                    if signal.action == "BUY"
                    else -int(signal.volume * 10000)
                ),
                "type": "MARKET",
                "timeInForce": "FOK",
            }
        }

        # Add stop loss if specified
        if signal.stop_loss:
            order_data["order"]["stopLossOnFill"] = {"price": str(signal.stop_loss)}

        # Add take profit if specified
        if signal.take_profit:
            order_data["order"]["takeProfitOnFill"] = {"price": str(signal.take_profit)}

        try:
            async with self.session.post(url, json=order_data) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(
                        f"Failed to place order: {response.status} - {error_text}"
                    )

                result = await response.json()
                logger.info(f"Order placed successfully: {result}")

                # Notify trade subscribers
                for callback in self.subscribers["trade"]:
                    try:
                        await callback(result)
                    except Exception as e:
                        logger.error(f"Error in trade callback: {e}")

                return result

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise

    async def get_account_info(self) -> Dict[str, Any]:
        """
        Gets account information, including balance and equity.

        Returns:
            Dict[str, Any]: A dictionary containing account details.

        Raises:
            ConnectionError: If the service is not connected.
            Exception: If the API request fails.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}"

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch account info: {response.status}")

                data = await response.json()
                return data.get("account", {})

        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise

    async def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Gets a list of all open positions for the account.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing an open position.

        Raises:
            ConnectionError: If the service is not connected.
            Exception: If the API request fails.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to FXCM API")

        url = f"{self.credentials.base_url}/v3/accounts/{self.credentials.account_id}/positions"

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch positions: {response.status}")

                data = await response.json()
                return data.get("positions", [])

        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise

    def to_dataframe(self, candles: List[Candle]) -> pd.DataFrame:
        """
        Converts a list of Candle objects to a pandas DataFrame.

        Args:
            candles (List[Candle]): The list of candles to convert.

        Returns:
            pd.DataFrame: A DataFrame with a timestamp index and OHLCV columns.
        """
        data = [
            {
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            }
            for c in candles
        ]

        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index("timestamp", inplace=True)
        return df


# Factory function for creating FXCM service
async def create_fxcm_service() -> FXCMService:
    """
    Factory function to create and initialize an FXCMService instance.

    It retrieves credentials from the global settings.

    Returns:
        FXCMService: An initialized and connected FXCMService instance.
    """
    credentials = FXCMCredentials(
        api_key=settings.FXCM_API_KEY,
        access_token=settings.FXCM_ACCESS_TOKEN,
        account_id=settings.FXCM_ACCOUNT_ID,
        environment=settings.FXCM_ENVIRONMENT,
    )

    service = FXCMService(credentials)
    await service.connect()
    return service
