"""
Technical Indicators Module
"""

from .macd import MACD
from .moving_average import MovingAverage
from .rsi import RSI


class TechnicalIndicators:
    """Technical indicators wrapper"""

    def __init__(self):
        self.rsi = RSI()
        self.macd = MACD()
        self.ma = MovingAverage()

    def add_all_indicators(self, data):
        """Add all technical indicators to dataframe"""

        # Add RSI
        data["rsi"] = self.rsi.calculate(data["close"])

        # Add MACD
        macd_data = self.macd.calculate(data["close"])
        data["macd"] = macd_data.get("macd", 0)
        data["macd_signal"] = macd_data.get("signal", 0)
        data["macd_histogram"] = macd_data.get("histogram", 0)

        # Add Moving Averages
        data["sma_20"] = self.ma.sma(data["close"], 20)
        data["ema_20"] = self.ma.ema(data["close"], 20)

        return data


__all__ = ["TechnicalIndicators", "RSI", "MACD", "MovingAverage"]
