from typing import Dict, Tuple

import numpy as np
import pandas as pd

from .moving_average import MovingAverage


class MACD:
    """
    Calculates the MACD (Moving Average Convergence Divergence) indicator.

    Attributes:
        fast_period (int): The time period for the fast EMA.
        slow_period (int): The time period for the slow EMA.
        signal_period (int): The time period for the signal line EMA.
        ma (MovingAverage): An instance of the MovingAverage calculator.
    """

    def __init__(
        self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9
    ):
        """
        Initializes the MACD calculator with specified periods.

        Args:
            fast_period (int): The period for the fast EMA.
            slow_period (int): The period for the slow EMA.
            signal_period (int): The period for the signal line EMA.
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.ma = MovingAverage()

    def calculate(self, prices: pd.Series) -> Dict[str, float]:
        """
        Calculates the MACD line, signal line, and histogram.

        Args:
            prices (pd.Series): A pandas Series of closing prices.

        Returns:
            Dict[str, float]: A dictionary containing the latest 'macd', 'signal',
                              and 'histogram' values.
        """
        if not isinstance(prices, pd.Series):
            prices = pd.Series(prices)

        fast_ema = self.ma.ema(prices, self.fast_period)
        slow_ema = self.ma.ema(prices, self.slow_period)

        macd_line = fast_ema - slow_ema
        signal_line = self.ma.ema(macd_line, self.signal_period)
        histogram = macd_line - signal_line

        return {
            "macd": macd_line.iloc[-1] if not macd_line.empty else 0,
            "signal": signal_line.iloc[-1] if not signal_line.empty else 0,
            "histogram": histogram.iloc[-1] if not histogram.empty else 0,
        }


def calculate_macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    A convenience function to calculate MACD values.
    This function is provided for backward compatibility or simpler use cases.
    Args:
        prices (pd.Series): A pandas Series of closing prices.
        fast_period (int): The period for the fast EMA.
        slow_period (int): The period for the slow EMA.
        signal_period (int): The period for the signal line EMA.
    Returns:
        Tuple[pd.Series, pd.Series, pd.Series]: A tuple containing the MACD line,
                                    signal line, and histogram as pandas Series.
    """
    if not isinstance(prices, pd.Series):
        prices = pd.Series(prices)

    ma = MovingAverage()
    fast_ema = ma.ema(prices, fast_period)
    slow_ema = ma.ema(prices, slow_period)
    macd_line = fast_ema - slow_ema
    signal_line = ma.ema(macd_line, signal_period)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram
