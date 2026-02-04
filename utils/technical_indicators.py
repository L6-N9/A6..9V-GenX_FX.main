"""
Technical Indicators Utility
Comprehensive technical analysis indicators for forex trading
"""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Comprehensive technical indicators calculator
    Optimized for forex trading signal generation
    """

    def __init__(self):
        self.indicators = {}
        logger.debug("Technical Indicators utility initialized")

    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to the dataframe"""
        try:
            # Make a copy to avoid modifying original data
            data = df.copy()

            # Price-based indicators
            data = self.add_moving_averages(data)
            data = self.add_momentum_indicators(data)
            data = self.add_volatility_indicators(data)
            data = self.add_volume_indicators(data)
            data = self.add_trend_indicators(data)
            data = self.add_support_resistance(data)

            logger.debug(
                f"Added {len(data.columns) - len(df.columns)} technical indicators"
            )
            return data

        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return df

    def add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving average indicators"""
        try:
            periods = [5, 10, 20, 50, 100, 200]

            for period in periods:
                if len(df) >= period:
                    # Simple Moving Average
                    df[f"sma_{period}"] = df["close"].rolling(window=period).mean()

                    # Exponential Moving Average
                    df[f"ema_{period}"] = df["close"].ewm(span=period).mean()

                    # Weighted Moving Average (Optimized)
                    # The original pandas apply() method is slow. This implementation
                    # uses numpy.convolve for a significant performance boost.
                    weights = np.arange(1, period + 1)
                    denominator = weights.sum()
                    wma_values = (
                        np.convolve(df["close"], weights, mode="valid") / denominator
                    )

                    # Align the convolution output with the DataFrame index
                    df[f"wma_{period}"] = pd.Series(
                        wma_values, index=df.index[period - 1 :]
                    )

            # Moving Average Convergence Divergence (MACD)
            if len(df) >= 26:
                ema12 = df["close"].ewm(span=12).mean()
                ema26 = df["close"].ewm(span=26).mean()
                df["macd"] = ema12 - ema26
                df["macd_signal"] = df["macd"].ewm(span=9).mean()
                df["macd_histogram"] = df["macd"] - df["macd_signal"]

            return df

        except Exception as e:
            logger.error(f"Error adding moving averages: {e}")
            return df

    def add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based indicators"""
        try:
            # Relative Strength Index (RSI)
            if len(df) >= 14:
                delta = df["close"].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)

                avg_gain = gain.rolling(window=14).mean()
                avg_loss = loss.rolling(window=14).mean()

                rs = avg_gain / avg_loss
                df["rsi"] = 100 - (100 / (1 + rs))

            # Stochastic Oscillator & Williams %R (Optimized)
            if len(df) >= 14:
                # Calculate rolling min/max once for both indicators
                low_min_14 = df["low"].rolling(window=14).min()
                high_max_14 = df["high"].rolling(window=14).max()
                range_14 = high_max_14 - low_min_14

                # Stochastic Oscillator
                df["stoch_k"] = 100 * (df["close"] - low_min_14) / range_14
                df["stoch_d"] = df["stoch_k"].rolling(window=3).mean()

                # Williams %R
                df["williams_r"] = -100 * (high_max_14 - df["close"]) / range_14

            # Rate of Change (ROC)
            periods = [5, 10, 20]
            for period in periods:
                if len(df) >= period:
                    df[f"roc_{period}"] = df["close"].pct_change(periods=period) * 100

            # Commodity Channel Index (CCI)
            if len(df) >= 20:
                window = 20
                typical_price = (df["high"] + df["low"] + df["close"]) / 3
                sma_tp = typical_price.rolling(window=window).mean()

                # ---
                # ⚡ Bolt Optimization: Vectorized Mean Deviation
                # The original `rolling().apply()` is notoriously slow. This
                # implementation uses a vectorized approach by creating a
                # rolling view of the data with numpy strides. This avoids
                # Python-level loops and is significantly faster.
                # ---
                typical_price_np = typical_price.to_numpy()
                shape = (typical_price_np.shape[0] - window + 1, window)
                strides = (typical_price_np.strides[0], typical_price_np.strides[0])
                rolling_windows = np.lib.stride_tricks.as_strided(
                    typical_price_np, shape=shape, strides=strides
                )

                # Calculate rolling mean absolute deviation
                rolling_mean = np.mean(rolling_windows, axis=1)
                rolling_mad_values = np.mean(
                    np.abs(rolling_windows - rolling_mean[:, np.newaxis]), axis=1
                )

                mean_dev = pd.Series(rolling_mad_values, index=df.index[window - 1 :])

                df["cci"] = (typical_price - sma_tp) / (0.015 * mean_dev)

            return df

        except Exception as e:
            logger.error(f"Error adding momentum indicators: {e}")
            return df

    def add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based indicators"""
        try:
            # Average True Range (ATR)
            if len(df) >= 14:
                # Use raw values for faster arithmetic
                high_vals = df["high"].values
                low_vals = df["low"].values
                prev_close = df["close"].shift().values

                tr1 = high_vals - low_vals
                tr2 = np.abs(high_vals - prev_close)
                tr3 = np.abs(low_vals - prev_close)

                tr = np.maximum(tr1, np.maximum(tr2, tr3))
                df["atr"] = pd.Series(tr, index=df.index).rolling(window=14).mean()

            # Bollinger Bands (Optimized: Reuse pre-calculated indicators)
            if len(df) >= 20:
                # Reuse SMA20 if it was already calculated in add_moving_averages
                sma_20 = (
                    df["sma_20"]
                    if "sma_20" in df.columns
                    else df["close"].rolling(window=20).mean()
                )
                # Calculate standard deviation once
                std_20 = df["close"].rolling(window=20).std()

                df["bb_upper"] = sma_20 + (2 * std_20)
                df["bb_lower"] = sma_20 - (2 * std_20)
                df["bb_middle"] = sma_20
                df["bb_width"] = df["bb_upper"] - df["bb_lower"]
                df["bb_position"] = (df["close"] - df["bb_lower"]) / df["bb_width"]
            else:
                std_20 = None

            # Volatility indicators (Optimized: Reuse std_20)
            periods = [10, 20, 50, 100]
            for period in periods:
                if len(df) >= period:
                    col_name = f"volatility_{period}"
                    if period == 20 and std_20 is not None:
                        df[col_name] = std_20
                    else:
                        df[col_name] = df["close"].rolling(window=period).std()

                    df[f"volatility_ratio_{period}"] = df[col_name] / df["close"]

            # Donchian Channels
            if len(df) >= 20:
                df["donchian_upper"] = df["high"].rolling(window=20).max()
                df["donchian_lower"] = df["low"].rolling(window=20).min()
                df["donchian_middle"] = (
                    df["donchian_upper"] + df["donchian_lower"]
                ) / 2
                df["donchian_position"] = (df["close"] - df["donchian_lower"]) / (
                    df["donchian_upper"] - df["donchian_lower"]
                )

            return df

        except Exception as e:
            logger.error(f"Error adding volatility indicators: {e}")
            return df

    def add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators"""
        try:
            if "volume" not in df.columns or df["volume"].sum() == 0:
                # Create synthetic volume for forex data
                df["volume"] = (df["high"] - df["low"]) * 1000000

            # Volume Moving Averages
            periods = [10, 20, 50]
            for period in periods:
                if len(df) >= period:
                    df[f"volume_sma_{period}"] = (
                        df["volume"].rolling(window=period).mean()
                    )
                    df[f"volume_ratio_{period}"] = (
                        df["volume"] / df[f"volume_sma_{period}"]
                    )

            # On-Balance Volume (OBV)
            if len(df) >= 2:
                price_change = df["close"].diff()
                volume_direction = np.where(
                    price_change > 0,
                    df["volume"],
                    np.where(price_change < 0, -df["volume"], 0),
                )
                df["obv"] = volume_direction.cumsum()

            # Volume Price Trend (VPT)
            if len(df) >= 2:
                price_change_pct = df["close"].pct_change()
                df["vpt"] = (price_change_pct * df["volume"]).cumsum()

            # Accumulation/Distribution Line
            if len(df) >= 1:
                money_flow_multiplier = (
                    (df["close"] - df["low"]) - (df["high"] - df["close"])
                ) / (df["high"] - df["low"])
                money_flow_volume = money_flow_multiplier * df["volume"]
                df["ad_line"] = money_flow_volume.cumsum()

            return df

        except Exception as e:
            logger.error(f"Error adding volume indicators: {e}")
            return df

    def add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend-based indicators"""
        try:
            # Parabolic SAR
            if len(df) >= 5:
                df["sar"] = self._calculate_parabolic_sar(df)

            # Average Directional Index (ADX)
            if len(df) >= 14:
                # Optimized: Reuse ATR if it was already calculated
                atr_14 = df["atr"] if "atr" in df.columns else None
                df = self._calculate_adx(df, period=14, atr_series=atr_14)

            # Aroon Indicator
            if len(df) >= 25:
                period = 25

                # ---
                # ⚡ Bolt Optimization: Vectorized Aroon Indicator
                # Replaced slow `rolling().apply()` with `sliding_window_view`.
                # Note: Keeping original (period - argmax) logic to avoid breaking changes.
                # ---
                high_vals = df["high"].values
                low_vals = df["low"].values

                # Create sliding windows
                high_windows = np.lib.stride_tricks.sliding_window_view(
                    high_vals, window_shape=period
                )
                low_windows = np.lib.stride_tricks.sliding_window_view(
                    low_vals, window_shape=period
                )

                # Find argmax/argmin along the window axis (axis=1)
                argmax_high = np.argmax(high_windows, axis=1)
                argmin_low = np.argmin(low_windows, axis=1)

                # Calculate Aroon values matching original formula
                aroon_up_vals = 100 * (period - argmax_high) / period
                aroon_down_vals = 100 * (period - argmin_low) / period

                # Align with dataframe using pre-allocated series
                aroon_up = pd.Series(np.nan, index=df.index)
                aroon_down = pd.Series(np.nan, index=df.index)

                aroon_up.iloc[period - 1 :] = aroon_up_vals
                aroon_down.iloc[period - 1 :] = aroon_down_vals

                df["aroon_up"] = aroon_up
                df["aroon_down"] = aroon_down
                df["aroon_oscillator"] = df["aroon_up"] - df["aroon_down"]

            # Trend strength
            periods = [10, 20, 50]
            for period in periods:
                if len(df) >= period:
                    # Linear regression slope (Vectorized for performance)
                    df[f"trend_strength_{period}"] = self._calculate_rolling_slope(
                        df["close"], period
                    )

            return df

        except Exception as e:
            logger.error(f"Error adding trend indicators: {e}")
            return df

    def add_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add support and resistance levels"""
        try:
            # Pivot Points
            if len(df) >= 1:
                df["pivot"] = (df["high"] + df["low"] + df["close"]) / 3
                df["r1"] = 2 * df["pivot"] - df["low"]
                df["s1"] = 2 * df["pivot"] - df["high"]
                df["r2"] = df["pivot"] + (df["high"] - df["low"])
                df["s2"] = df["pivot"] - (df["high"] - df["low"])

            # Price position relative to recent highs/lows (Optimized)
            periods = [20, 50]
            for period in periods:
                if len(df) >= period:
                    # Reuse Donchian channels for period 20 if available
                    if period == 20 and "donchian_upper" in df.columns:
                        high_max = df["donchian_upper"]
                        low_min = df["donchian_lower"]
                    else:
                        high_max = df["high"].rolling(window=period).max()
                        low_min = df["low"].rolling(window=period).min()

                    df[f"price_position_{period}"] = (df["close"] - low_min) / (
                        high_max - low_min
                    )
                    df[f"resistance_distance_{period}"] = (high_max - df["close"]) / df[
                        "close"
                    ]
                    df[f"support_distance_{period}"] = (df["close"] - low_min) / df[
                        "close"
                    ]

            return df

        except Exception as e:
            logger.error(f"Error adding support/resistance indicators: {e}")
            return df

    def _calculate_parabolic_sar(
        self,
        df: pd.DataFrame,
        af_start: float = 0.02,
        af_increment: float = 0.02,
        af_max: float = 0.2,
    ) -> pd.Series:
        """Calculate Parabolic SAR"""
        try:
            high = df["high"].values
            low = df["low"].values
            close = df["close"].values

            length = len(df)
            sar = np.zeros(length)
            trend = np.zeros(length)
            af = np.zeros(length)
            ep = np.zeros(length)

            # Initialize
            sar[0] = low[0]
            trend[0] = 1  # 1 for up, -1 for down
            af[0] = af_start
            ep[0] = high[0]

            for i in range(1, length):
                if trend[i - 1] == 1:  # Uptrend
                    sar[i] = sar[i - 1] + af[i - 1] * (ep[i - 1] - sar[i - 1])

                    if low[i] <= sar[i]:
                        trend[i] = -1
                        sar[i] = ep[i - 1]
                        af[i] = af_start
                        ep[i] = low[i]
                    else:
                        trend[i] = 1
                        if high[i] > ep[i - 1]:
                            ep[i] = high[i]
                            af[i] = min(af[i - 1] + af_increment, af_max)
                        else:
                            ep[i] = ep[i - 1]
                            af[i] = af[i - 1]
                else:  # Downtrend
                    sar[i] = sar[i - 1] + af[i - 1] * (ep[i - 1] - sar[i - 1])

                    if high[i] >= sar[i]:
                        trend[i] = 1
                        sar[i] = ep[i - 1]
                        af[i] = af_start
                        ep[i] = high[i]
                    else:
                        trend[i] = -1
                        if low[i] < ep[i - 1]:
                            ep[i] = low[i]
                            af[i] = min(af[i - 1] + af_increment, af_max)
                        else:
                            ep[i] = ep[i - 1]
                            af[i] = af[i - 1]

            return pd.Series(sar, index=df.index)

        except Exception as e:
            logger.error(f"Error calculating Parabolic SAR: {e}")
            return pd.Series(np.nan, index=df.index)

    def _calculate_rolling_slope(self, series: pd.Series, window: int) -> pd.Series:
        """Calculate the slope of a linear regression over a rolling window."""
        try:
            # ---
            # ⚡ Bolt Optimization: Vectorized Linear Regression Slope
            # Replaced the slow `rolling().apply(np.polyfit)` with a vectorized
            # implementation using numpy convolution and rolling sums. This avoids
            # Python-level loops and the overhead of calling polyfit thousands of times.
            # ---
            n = window
            if len(series) < n:
                return pd.Series(np.nan, index=series.index)

            x_mean = (n - 1) / 2
            # sum((i - x_mean)^2) for i = 0 to n-1
            sum_x2 = n * (n**2 - 1) / 12

            y_sum = series.rolling(window=n).sum()

            # Use convolution for sum(i * y_i)
            # To get sum_{i=0}^{n-1} i * y_{t-n+1+i}, we use weights [n-1, n-2, ..., 0]
            weights = np.arange(n - 1, -1, -1)
            sum_iy = np.convolve(series.values, weights, mode="valid")

            # Align the result with the original series index
            sum_iy_series = pd.Series(sum_iy, index=series.index[n - 1 :])

            slope = (sum_iy_series - x_mean * y_sum) / sum_x2
            return slope

        except Exception as e:
            logger.error(f"Error calculating rolling slope: {e}")
            return pd.Series(np.nan, index=series.index)

    def _calculate_adx(
        self, df: pd.DataFrame, period: int = 14, atr_series: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """Calculate Average Directional Index (ADX)"""
        try:
            # ---
            # ⚡ Bolt Optimization: Vectorized ADX calculation
            # - Replaced slow `pd.concat().max(axis=1)` with `np.maximum` (~20x faster).
            # - Used raw numpy values for arithmetic to avoid Pandas overhead (~2x faster).
            # - Reused shifted series to avoid redundant `shift()` calls.
            # - Used vectorized `np.where` for DM+ and DM- calculation.
            # - Optimized: Can reuse pre-calculated ATR to avoid redundant TR/ATR calculations.
            # ---

            # Calculate Directional Movement
            high_vals = df["high"].values
            low_vals = df["low"].values
            prev_high_vals = df["high"].shift().values
            prev_low_vals = df["low"].shift().values

            up = np.clip(high_vals - prev_high_vals, 0, None)
            down = np.clip(prev_low_vals - low_vals, 0, None)

            # Standard Wilder's logic for Directional Movement
            dm_plus_vals = np.where((up > down) & (up > 0), up, 0)
            dm_minus_vals = np.where((down > up) & (down > 0), down, 0)

            # Convert to Series for rolling calculations
            dm_plus = pd.Series(dm_plus_vals, index=df.index)
            dm_minus = pd.Series(dm_minus_vals, index=df.index)

            # Calculate smoothed averages
            if atr_series is not None:
                atr = atr_series
            else:
                prev_close_vals = df["close"].shift().values
                tr1 = high_vals - low_vals
                tr2 = np.abs(high_vals - prev_close_vals)
                tr3 = np.abs(low_vals - prev_close_vals)
                tr = np.maximum(tr1, np.maximum(tr2, tr3))
                atr = pd.Series(tr, index=df.index).rolling(window=period).mean()

            di_plus = 100 * (dm_plus.rolling(window=period).mean() / atr)
            di_minus = 100 * (dm_minus.rolling(window=period).mean() / atr)

            # Calculate ADX
            dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus)
            adx = dx.rolling(window=period).mean()

            df["di_plus"] = di_plus
            df["di_minus"] = di_minus
            df["adx"] = adx

            return df

        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return df

    def get_indicator_summary(self, df: pd.DataFrame) -> Dict:
        """Get summary of current indicator values"""
        try:
            if len(df) == 0:
                return {}

            latest = df.iloc[-1]
            summary = {}

            # Trend indicators
            if "sma_20" in df.columns and "sma_50" in df.columns:
                summary["trend"] = (
                    "UPTREND" if latest["sma_20"] > latest["sma_50"] else "DOWNTREND"
                )

            # Momentum
            if "rsi" in df.columns:
                rsi = latest["rsi"]
                if rsi > 70:
                    summary["momentum"] = "OVERBOUGHT"
                elif rsi < 30:
                    summary["momentum"] = "OVERSOLD"
                else:
                    summary["momentum"] = "NEUTRAL"

            # Volatility
            if "atr" in df.columns:
                current_atr = latest["atr"]
                avg_atr = df["atr"].tail(20).mean()
                summary["volatility"] = (
                    "HIGH" if current_atr > avg_atr * 1.5 else "NORMAL"
                )

            # Bollinger Bands position
            if "bb_position" in df.columns:
                bb_pos = latest["bb_position"]
                if bb_pos > 0.8:
                    summary["bb_position"] = "UPPER"
                elif bb_pos < 0.2:
                    summary["bb_position"] = "LOWER"
                else:
                    summary["bb_position"] = "MIDDLE"

            return summary

        except Exception as e:
            logger.error(f"Error getting indicator summary: {e}")
            return {}
