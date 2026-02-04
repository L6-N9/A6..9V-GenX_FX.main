import sys
import unittest

import numpy as np
import pandas as pd
import talib

# Set PYTHONPATH
sys.path.append(".")
from ai_models.feature_engineer import FeatureEngineer


class TestFeatureEngineerOptimized(unittest.TestCase):
    def setUp(self):
        self.fe = FeatureEngineer()
        self.sequence_length = 30
        self.df = pd.DataFrame(
            np.random.random((100, 5)),
            columns=["open", "high", "low", "close", "volume"],
        )

    def test_create_price_sequences_matching(self):
        """Test that vectorized price sequences match the loop-based ones."""
        price_data = self.df[["open", "high", "low", "close", "volume"]].values
        scaled_data = self.fe.price_scaler.fit_transform(price_data)
        expected_sequences = []
        for i in range(len(scaled_data) - self.sequence_length + 1):
            expected_sequences.append(scaled_data[i : i + self.sequence_length])
        expected = np.array(expected_sequences)

        actual = self.fe._create_price_sequences(
            self.df, self.sequence_length, only_last=False
        )
        np.testing.assert_array_almost_equal(actual, expected)

    def test_create_price_sequences_only_last(self):
        """Test the only_last optimization for price sequences."""
        full = self.fe._create_price_sequences(
            self.df, self.sequence_length, only_last=False
        )
        last_only = self.fe._create_price_sequences(
            self.df, self.sequence_length, only_last=True
        )

        self.assertEqual(last_only.shape, (1, self.sequence_length, 5))
        np.testing.assert_array_almost_equal(last_only[0], full[-1])

    def test_create_chart_images_matching(self):
        """Test that vectorized chart images match the loop-based ones."""
        rsi = talib.RSI(self.df["close"], timeperiod=14)
        macd_line, _, macd_hist = talib.MACD(self.df["close"])

        expected_images = []
        for i in range(self.sequence_length, len(self.df)):
            window_data = self.df.iloc[i - self.sequence_length : i]
            price_norm = (window_data["close"] - window_data["close"].min()) / (
                window_data["close"].max() - window_data["close"].min() + 1e-8
            )

            rsi_win = rsi.iloc[i - self.sequence_length : i].fillna(0.5).values
            macd_l_win = macd_line.iloc[i - self.sequence_length : i].fillna(0).values
            macd_h_win = macd_hist.iloc[i - self.sequence_length : i].fillna(0).values

            channels = [
                price_norm.values,
                rsi_win,
                macd_l_win,
                macd_h_win,
            ]
            expected_images.append(np.column_stack(channels))

        expected = np.array(expected_images)
        actual = self.fe._create_chart_images(
            self.df, self.sequence_length, only_last=False
        )

        self.assertEqual(actual.shape, expected.shape)
        np.testing.assert_array_almost_equal(actual, expected)

    def test_create_chart_images_only_last(self):
        """Test the only_last optimization for chart images."""
        full = self.fe._create_chart_images(
            self.df, self.sequence_length, only_last=False
        )
        last_only = self.fe._create_chart_images(
            self.df, self.sequence_length, only_last=True
        )

        self.assertEqual(last_only.shape, (1, self.sequence_length, 4))
        np.testing.assert_array_almost_equal(last_only[0], full[-1])

    def test_edge_cases(self):
        """Test edge cases like short data."""
        short_df = self.df.iloc[:5]  # Length 5, sequence_length 30

        res_price = self.fe._create_price_sequences(short_df, self.sequence_length)
        self.assertEqual(res_price.shape, (0, self.sequence_length, 5))

        res_chart = self.fe._create_chart_images(short_df, self.sequence_length)
        self.assertEqual(res_chart.shape, (0, self.sequence_length, 4))


if __name__ == "__main__":
    unittest.main()
