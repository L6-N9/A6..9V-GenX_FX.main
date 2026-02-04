"""
Pattern Detection for Trading
"""

from typing import Any, Dict

import numpy as np
import pandas as pd


class PatternDetector:
    """
    A class for detecting common candlestick patterns in market data.
    """

    def __init__(self):
        """Initializes the PatternDetector."""
        pass

    def detect_patterns(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Detects a variety of candlestick patterns in the given market data.

        Args:
            data (pd.DataFrame): A DataFrame with 'open', 'high', 'low', 'close' columns.

        Returns:
            Dict[str, pd.Series]: A dictionary where keys are pattern names and
                                  values are boolean Series indicating where the
                                  patterns occur.
        """
        patterns = {
            "bullish_engulfing": self._detect_bullish_engulfing(data),
            "bearish_engulfing": self._detect_bearish_engulfing(data),
            "doji": self._detect_doji(data),
        }
        return patterns

    def _detect_bullish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """
        Detects the Bullish Engulfing candlestick pattern.

        Args:
            data (pd.DataFrame): The input market data.

        Returns:
            pd.Series: A boolean Series that is True where the pattern is detected.
        """
        if len(data) < 2:
            return pd.Series(False, index=data.index)

        prev_is_bearish = data["close"].shift(1) < data["open"].shift(1)
        curr_is_bullish = data["close"] > data["open"]
        engulfs = (data["open"] < data["close"].shift(1)) & (
            data["close"] > data["open"].shift(1)
        )

        pattern = prev_is_bearish & curr_is_bullish & engulfs
        return pattern.astype(int)

    def _detect_bearish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """
        Detects the Bearish Engulfing candlestick pattern.

        Args:
            data (pd.DataFrame): The input market data.

        Returns:
            pd.Series: A boolean Series that is True where the pattern is detected.
        """
        if len(data) < 2:
            return pd.Series(False, index=data.index)

        prev_is_bullish = data["close"].shift(1) > data["open"].shift(1)
        curr_is_bearish = data["close"] < data["open"]
        engulfs = (data["open"] > data["close"].shift(1)) & (
            data["close"] < data["open"].shift(1)
        )

        pattern = prev_is_bullish & curr_is_bearish & engulfs
        return pattern.astype(int)

    def _detect_doji(self, data: pd.DataFrame) -> pd.Series:
        """
        Detects a Doji candlestick pattern.

        A Doji is characterized by a very small body, indicating indecision.

        Args:
            data (pd.DataFrame): The input market data.

        Returns:
            pd.Series: A boolean Series that is True where a Doji is detected.
        """
        body_size = abs(data["close"] - data["open"])
        candle_range = data["high"] - data["low"]

        # A Doji's body is typically less than 10% of its total range
        is_doji = body_size < (candle_range * 0.1)

        return is_doji.astype(int)
