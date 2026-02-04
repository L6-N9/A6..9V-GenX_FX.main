"""
Enhanced WebSocket Service for GenX Trading Platform
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import websockets

logger = logging.getLogger(__name__)


@dataclass
class MarketData:
    """
    Represents a standardized market data object from a WebSocket stream.

    Attributes:
        symbol (str): The trading symbol.
        price (float): The last traded price.
        volume (float): The volume of the last trade.
        timestamp (datetime): The timestamp of the data.
        bid (Optional[float]): The best bid price, if available.
        ask (Optional[float]): The best ask price, if available.
        high_24h (Optional[float]): The 24-hour high price.
        low_24h (Optional[float]): The 24-hour low price.
        change_24h (Optional[float]): The 24-hour price change.
    """

    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    change_24h: Optional[float] = None


class WebSocketService:
    """
    Manages real-time market data streams from multiple exchanges via WebSockets.

    This service handles connecting, subscribing, and parsing data from various
    crypto exchanges like Bybit, Binance, and Coinbase.

    Attributes:
        connections (Dict[str, websockets.WebSocketClientProtocol]): Active connections, keyed by exchange name.
        subscribers (Dict[str, set]): Subscribed symbols, keyed by exchange name.
        running (bool): Flag indicating if the service is running.
        data_callbacks (List[Callable]): A list of callbacks to be invoked with new market data.
    """

    def __init__(self):
        """Initializes the WebSocketService."""
        self.connections: Dict[str, websockets.client.WebSocketClientProtocol] = {}
        self.subscribers: Dict[str, set] = {}
        self.running = False
        self.reconnect_interval = int(os.getenv("WEBSOCKET_RECONNECT_INTERVAL", "5"))
        self.max_retries = int(os.getenv("MAX_WEBSOCKET_RETRIES", "10"))

        # Exchange endpoints
        self.exchanges = {
            "bybit": {
                "url": "wss://stream.bybit.com/v5/public/spot",
                "subscribe_format": self._bybit_subscribe_format,
                "parser": self._parse_bybit_data,
            },
            "binance": {
                "url": "wss://stream.binance.com:9443/ws/",
                "subscribe_format": self._binance_subscribe_format,
                "parser": self._parse_binance_data,
            },
            "coinbase": {
                "url": "wss://ws-feed.pro.coinbase.com",
                "subscribe_format": self._coinbase_subscribe_format,
                "parser": self._parse_coinbase_data,
            },
        }

        # Data callbacks
        self.data_callbacks = []

    async def initialize(self) -> bool:
        """
        Initializes the WebSocket service.

        Sets the service to a running state and creates background tasks to
        maintain connections to each configured exchange.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            logger.info("Initializing WebSocket service...")
            self.running = True

            # Start connection tasks for each exchange
            for exchange_name in self.exchanges.keys():
                asyncio.create_task(self._maintain_connection(exchange_name))

            logger.info("WebSocket service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize WebSocket service: {e}")
            return False

    async def subscribe_to_symbol(
        self, exchange: str, symbol: str, callback: Optional[Callable] = None
    ):
        """
        Subscribes to real-time data for a symbol on a specific exchange.

        Args:
            exchange (str): The name of the exchange (e.g., 'bybit').
            symbol (str): The trading symbol to subscribe to.
            callback (Optional[Callable]): An optional callback to be added for data updates.

        Raises:
            ValueError: If the exchange is not supported.
        """
        try:
            if exchange not in self.exchanges:
                raise ValueError(f"Unsupported exchange: {exchange}")

            if exchange not in self.subscribers:
                self.subscribers[exchange] = set()

            self.subscribers[exchange].add(symbol)

            if callback:
                self.data_callbacks.append(callback)

            # Send subscription message if a connection already exists
            if exchange in self.connections:
                await self._send_subscription(exchange, symbol)

            logger.info(f"Subscribed to {symbol} on {exchange}")

        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol} on {exchange}: {e}")

    async def unsubscribe_from_symbol(self, exchange: str, symbol: str):
        """
        Unsubscribes from real-time data for a symbol.

        Args:
            exchange (str): The name of the exchange.
            symbol (str): The symbol to unsubscribe from.
        """
        try:
            if exchange in self.subscribers:
                self.subscribers[exchange].discard(symbol)

            # Send unsubscription message if a connection exists
            if exchange in self.connections:
                await self._send_unsubscription(exchange, symbol)

            logger.info(f"Unsubscribed from {symbol} on {exchange}")

        except Exception as e:
            logger.error(f"Failed to unsubscribe from {symbol} on {exchange}: {e}")

    def add_data_callback(self, callback: Callable):
        """
        Adds a callback function to be invoked with every market data update.

        Args:
            callback (Callable): The function to call with new MarketData objects.
        """
        self.data_callbacks.append(callback)

    async def _maintain_connection(self, exchange: str):
        """
        Maintains a persistent WebSocket connection to an exchange.

        This method runs in a loop, attempting to connect and reconnect
        after failures, with a specified interval and max retries.

        Args:
            exchange (str): The name of the exchange to connect to.
        """
        retry_count = 0

        while self.running and retry_count < self.max_retries:
            try:
                exchange_config = self.exchanges[exchange]

                async with websockets.connect(exchange_config["url"]) as websocket:
                    self.connections[exchange] = websocket
                    retry_count = 0  # Reset retry count on successful connection
                    logger.info(f"Connected to {exchange} WebSocket")

                    # Subscribe to any symbols that were requested before connection
                    if exchange in self.subscribers:
                        for symbol in self.subscribers[exchange]:
                            await self._send_subscription(exchange, symbol)

                    # Main message listening loop
                    await self._listen_for_messages(websocket, exchange)

            except (websockets.exceptions.ConnectionClosed, ConnectionError) as e:
                logger.warning(f"Connection to {exchange} closed: {e}")
            except Exception as e:
                logger.error(f"Connection error for {exchange}: {e}")

            # Connection lost, prepare for retry
            if exchange in self.connections:
                del self.connections[exchange]

            if self.running:
                retry_count += 1
                if retry_count < self.max_retries:
                    logger.info(
                        f"Reconnecting to {exchange} in {self.reconnect_interval} seconds... (Attempt {retry_count})"
                    )
                    await asyncio.sleep(self.reconnect_interval)

        if retry_count >= self.max_retries:
            logger.error(f"Max retries exceeded for {exchange}. Giving up.")

    async def _listen_for_messages(
        self, websocket: websockets.client.WebSocketClientProtocol, exchange: str
    ):
        """Listens for and processes messages from a websocket connection."""
        async for message in websocket:
            try:
                data = json.loads(message)
                market_data = self.exchanges[exchange]["parser"](data)

                if market_data:
                    # Call all registered callbacks with the new data
                    for callback in self.data_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(market_data)
                            else:
                                callback(market_data)
                        except Exception as e:
                            logger.error(f"Error in data callback: {e}")

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {exchange}: {message}")
            except Exception as e:
                logger.error(f"Message processing error for {exchange}: {e}")

    async def _send_subscription(self, exchange: str, symbol: str):
        """
        Sends a subscription message to the specified exchange's WebSocket.

        Args:
            exchange (str): The name of the exchange.
            symbol (str): The symbol to subscribe to.
        """
        try:
            websocket = self.connections.get(exchange)
            if not websocket:
                return

            exchange_config = self.exchanges[exchange]
            subscribe_msg = exchange_config["subscribe_format"](symbol)

            await websocket.send(json.dumps(subscribe_msg))
            logger.debug(f"Sent subscription for {symbol} to {exchange}")

        except Exception as e:
            logger.error(f"Failed to send subscription for {symbol} to {exchange}: {e}")

    async def _send_unsubscription(self, exchange: str, symbol: str):
        """
        Sends an unsubscription message to the specified exchange.

        Args:
            exchange (str): The name of the exchange.
            symbol (str): The symbol to unsubscribe from.
        """
        try:
            websocket = self.connections.get(exchange)
            if not websocket:
                return

            exchange_config = self.exchanges[exchange]
            # This is a generic approach; specific exchanges might have different
            # formats for unsubscribing.
            unsubscribe_msg = exchange_config["subscribe_format"](symbol)
            if "op" in unsubscribe_msg:  # Bybit style
                unsubscribe_msg["op"] = "unsubscribe"
            elif "method" in unsubscribe_msg:  # Binance style
                unsubscribe_msg["method"] = "UNSUBSCRIBE"

            await websocket.send(json.dumps(unsubscribe_msg))
            logger.debug(f"Sent unsubscription for {symbol} to {exchange}")

        except Exception as e:
            logger.error(
                f"Failed to send unsubscription for {symbol} to {exchange}: {e}"
            )

    def _bybit_subscribe_format(self, symbol: str) -> Dict[str, Any]:
        """Formats a subscription message for the Bybit exchange."""
        return {"op": "subscribe", "args": [f"publicTrade.{symbol}"]}

    def _binance_subscribe_format(self, symbol: str) -> Dict[str, Any]:
        """Formats a subscription message for the Binance exchange."""
        return {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@trade"],
            "id": 1,
        }

    def _coinbase_subscribe_format(self, symbol: str) -> Dict[str, Any]:
        """Formats a subscription message for the Coinbase exchange."""
        return {
            "type": "subscribe",
            "product_ids": [symbol],
            "channels": ["matches"],
        }

    def _parse_bybit_data(self, data: Dict[str, Any]) -> Optional[MarketData]:
        """
        Parses incoming WebSocket data from Bybit.

        Args:
            data (Dict[str, Any]): The raw data dictionary from the WebSocket.

        Returns:
            Optional[MarketData]: A standardized MarketData object, or None if parsing fails.
        """
        try:
            if data.get("topic", "").startswith("publicTrade"):
                trade_data = data.get("data", [])
                if trade_data:
                    trade = trade_data[0]
                    return MarketData(
                        symbol=trade["s"],
                        price=float(trade["p"]),
                        volume=float(trade["v"]),
                        timestamp=datetime.fromtimestamp(int(trade["T"]) / 1000),
                    )
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"Failed to parse Bybit data: {e} | Data: {data}")
        return None

    def _parse_binance_data(self, data: Dict[str, Any]) -> Optional[MarketData]:
        """
        Parses incoming WebSocket data from Binance.

        Args:
            data (Dict[str, Any]): The raw data dictionary from the WebSocket.

        Returns:
            Optional[MarketData]: A standardized MarketData object, or None if parsing fails.
        """
        try:
            if data.get("e") == "trade":
                return MarketData(
                    symbol=data["s"],
                    price=float(data["p"]),
                    volume=float(data["q"]),
                    timestamp=datetime.fromtimestamp(int(data["T"]) / 1000),
                )
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to parse Binance data: {e} | Data: {data}")
        return None

    def _parse_coinbase_data(self, data: Dict[str, Any]) -> Optional[MarketData]:
        """
        Parses incoming WebSocket data from Coinbase.

        Args:
            data (Dict[str, Any]): The raw data dictionary from the WebSocket.

        Returns:
            Optional[MarketData]: A standardized MarketData object, or None if parsing fails.
        """
        try:
            if data.get("type") == "match":
                return MarketData(
                    symbol=data["product_id"],
                    price=float(data["price"]),
                    volume=float(data["size"]),
                    timestamp=datetime.fromisoformat(
                        data["time"].replace("Z", "+00:00")
                    ),
                )
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to parse Coinbase data: {e} | Data: {data}")
        return None

    async def get_connection_status(self) -> Dict[str, Any]:
        """
        Gets the current status of all WebSocket connections.

        Returns:
            Dict[str, Any]: A dictionary summarizing the connection status for each exchange.
        """
        status = {
            exchange: {
                "connected": exchange in self.connections,
                "subscribed_symbols": list(self.subscribers.get(exchange, set())),
                "subscriber_count": len(self.subscribers.get(exchange, set())),
            }
            for exchange in self.exchanges.keys()
        }

        return {
            "exchanges": status,
            "total_connections": len(self.connections),
            "total_callbacks": len(self.data_callbacks),
            "running": self.running,
        }

    async def health_check(self) -> bool:
        """
        Performs a health check on the WebSocket service.

        Returns:
            bool: True if the service is running and has at least one active connection.
        """
        try:
            # A healthy service should be running and have at least one active connection.
            return self.running and len(self.connections) > 0
        except Exception as e:
            logger.error(f"WebSocket health check failed: {e}")
            return False

    async def shutdown(self):
        """Shuts down the WebSocket service and closes all connections."""
        logger.info("Shutting down WebSocket service...")
        self.running = False

        # Close all active connections
        for exchange, websocket in self.connections.items():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing {exchange} connection: {e}")

        self.connections.clear()
        self.subscribers.clear()
        self.data_callbacks.clear()

        logger.info("WebSocket service shutdown complete")
