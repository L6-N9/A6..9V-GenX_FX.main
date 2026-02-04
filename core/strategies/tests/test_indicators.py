import unittest

import numpy as np

from core.indicators.macd import calculate_macd
from core.indicators.moving_average import calculate_ema, calculate_sma
from core.indicators.rsi import calculate_rsi


class TestIndicators(unittest.TestCase):

    def setUp(self):
        self.prices = np.array(
            [
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                19,
                18,
                17,
                16,
                15,
                14,
                13,
                12,
                11,
                10,
            ]
        )

    def test_calculate_rsi(self):
        rsi = calculate_rsi(self.prices)
        self.assertEqual(len(rsi), len(self.prices))
        # Add more specific assertions based on expected RSI values

    def test_calculate_macd(self):
        macd_line, signal_line, histogram = calculate_macd(self.prices)
        # Add assertions to check the output shapes and values
        # Note: calculate_macd currently returns pandas Series, so we check for that
        import pandas as pd

        self.assertTrue(isinstance(macd_line, (np.ndarray, pd.Series)))
        self.assertTrue(isinstance(signal_line, (np.ndarray, pd.Series)))
        self.assertTrue(isinstance(histogram, (np.ndarray, pd.Series)))

    def test_calculate_sma(self):
        sma = calculate_sma(self.prices, period=5)
        self.assertEqual(
            len(sma), len(self.prices)
        )  # Fixed: Pandas returns same length
        # Add more specific assertions based on expected SMA values

    def test_calculate_ema(self):
        ema = calculate_ema(self.prices, period=5)
        self.assertEqual(
            len(ema), len(self.prices)
        )  # Fixed: Pandas returns same length
        # Add more specific assertions based on expected EMA values


if __name__ == "__main__":
    unittest.main()
