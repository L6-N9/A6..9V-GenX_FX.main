import numpy as np
import pandas as pd


class MovingAverage:
    """A utility class for calculating different types of moving averages."""

    def __init__(self):
        """Initializes the MovingAverage calculator."""
        pass

    def sma(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculates the Simple Moving Average (SMA).

        Args:
            prices (pd.Series): A pandas Series of prices.
            period (int): The moving average period.

        Returns:
            pd.Series: A pandas Series containing the SMA values.
        """
        if not isinstance(prices, pd.Series):
            prices = pd.Series(prices)
        return prices.rolling(window=period).mean()

    def ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calculates the Exponential Moving Average (EMA).

        Args:
            prices (pd.Series): A pandas Series of prices.
            period (int): The moving average period (span).

        Returns:
            pd.Series: A pandas Series containing the EMA values.
        """
        if not isinstance(prices, pd.Series):
            prices = pd.Series(prices)
        return prices.ewm(span=period, adjust=False).mean()


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """
    A convenience function to calculate the Simple Moving Average (SMA).

    Args:
        prices (pd.Series): A pandas Series of prices.
        period (int): The moving average period.

    Returns:
        pd.Series: A pandas Series containing the SMA values.
    """
    ma = MovingAverage()
    return ma.sma(prices, period)


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    A convenience function to calculate the Exponential Moving Average (EMA).

    Args:
        prices (pd.Series): A pandas Series of prices.
        period (int): The moving average period (span).

    Returns:
        pd.Series: A pandas Series containing the EMA values.
    """
    ma = MovingAverage()
    return ma.ema(prices, period)
