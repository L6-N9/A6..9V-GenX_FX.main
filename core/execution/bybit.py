import os

from pybit.unified_trading import HTTP


class BybitAPI:
    """
    A wrapper for the pybit library to interact with the Bybit V5 API.

    This class simplifies the process of connecting to Bybit, fetching market
    data, and executing orders.

    Attributes:
        session (HTTP): An authenticated pybit HTTP session object.
    """

    def __init__(self):
        """
        Initializes the BybitAPI wrapper.

        Retrieves API keys from environment variables and establishes a session.

        Raises:
            ValueError: If the required API keys are not set in the environment.
        """
        api_key = os.environ.get("BYBIT_API_KEY")
        api_secret = os.environ.get("BYBIT_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError(
                "BYBIT_API_KEY and BYBIT_API_SECRET environment variables must be set."
            )

        # For testnet, set testnet=True
        self.session = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret,
        )

    def get_market_data(self, symbol: str, interval: str, limit: int = 200):
        """
        Fetches k-line (candlestick) market data from the Bybit V5 API.

        Args:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            interval (str): The candle interval (e.g., '1', '60', 'D').
            limit (int): The number of data points to retrieve, up to 1000.

        Returns:
            Optional[Dict]: The API response dictionary, or None on failure.
        """
        try:
            response = self.session.get_kline(
                category="spot", symbol=symbol, interval=interval, limit=limit
            )
            return response
        except Exception as e:
            print(f"Error fetching data from Bybit: {e}")
            return None

    def execute_order(self, symbol: str, side: str, order_type: str, qty: float):
        """
        Places an order on the Bybit V5 API.

        Args:
            symbol (str): The trading symbol (e.g., 'BTCUSDT').
            side (str): The order side ('Buy' or 'Sell').
            order_type (str): The order type ('Market' or 'Limit').
            qty (float): The quantity to be ordered.

        Returns:
            Optional[Dict]: The API response dictionary, or None on failure.
        """
        try:
            response = self.session.place_order(
                category="spot",
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=str(qty),
            )
            return response
        except Exception as e:
            print(f"Error executing order on Bybit: {e}")
            return None
