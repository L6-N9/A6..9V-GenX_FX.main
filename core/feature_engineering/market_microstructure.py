"""
Market Microstructure Features for GenX FX Trading System
Features related to market microstructure and order flow
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class MarketMicrostructureFeatures:
    """
    A feature engineering engine for generating market microstructure features.

    These features are derived from price and volume data to provide insights
    into market dynamics like spread, price impact, and order flow.

    Attributes:
        feature_columns (List[str]): A list to store the names of generated features.
    """

    def __init__(self):
        """Initializes the MarketMicrostructureFeatures engine."""
        self.feature_columns = []

    def generate_features(
        self, df: pd.DataFrame, symbol: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Generates a set of market microstructure features.

        Since real bid/ask and order book data are often unavailable, this method
        uses estimations and proxies based on OHLCV data.

        Args:
            df (pd.DataFrame): A DataFrame with OHLCV data.
            symbol (Optional[str]): The trading symbol (currently unused).

        Returns:
            pd.DataFrame: The DataFrame enriched with microstructure features.
        """
        if df.empty or len(df) < 10:
            return df

        features_df = df.copy()

        try:
            # Spread indicators
            features_df = self._add_spread_features(features_df)

            # Price impact features
            features_df = self._add_price_impact_features(features_df)

            # Order flow features
            features_df = self._add_order_flow_features(features_df)

            # Market depth features (simulated)
            features_df = self._add_market_depth_features(features_df)

            # Fill NaN values
            features_df = features_df.fillna(method="ffill").fillna(0)

        except Exception as e:
            print(f"Warning: Error generating microstructure features: {e}")
            return df

        return features_df

    def _add_spread_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds simulated bid-ask spread features.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with added spread features.
        """
        # Since we don't have real bid/ask data, we'll estimate the spread
        df["estimated_spread"] = (df["High"] - df["Low"]) * 0.1  # Rough estimate
        df["spread_pct"] = df["estimated_spread"] / df["Close"] * 100
        df["spread_ma_5"] = df["estimated_spread"].rolling(window=5).mean()
        df["spread_volatility"] = df["estimated_spread"].rolling(window=10).std()

        return df

    def _add_price_impact_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds features related to price impact and effective spread.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with added price impact features.
        """
        # Price impact estimation based on price movements
        df["price_impact_1"] = abs(df["Close"].shift(1) - df["Open"])
        df["price_impact_5"] = (
            abs(df["Close"].shift(5) - df["Close"]) if len(df) > 5 else 0
        )
        df["cumulative_impact"] = df["price_impact_1"].rolling(window=10).sum()

        # Effective spread (estimated)
        df["effective_spread"] = abs(df["Close"] - df["Open"])
        df["effective_spread_pct"] = df["effective_spread"] / df["Close"] * 100

        return df

    def _add_order_flow_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds features that estimate order flow from price and volume data.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with added order flow features.
        """
        if "Volume" in df.columns:
            # Volume-weighted features
            df["vwap"] = (df["Close"] * df["Volume"]).rolling(window=20).sum() / df[
                "Volume"
            ].rolling(window=20).sum()
            df["price_vs_vwap"] = (df["Close"] - df["vwap"]) / df["vwap"] * 100

            # Order flow imbalance (estimated)
            df["volume_imbalance"] = (
                df["Volume"] - df["Volume"].rolling(window=20).mean()
            )
            df["price_volume_trend"] = (
                (df["Close"].pct_change() * df["Volume"]).rolling(window=5).sum()
            )
        else:
            # Price-based approximations when volume is not available
            df["vwap"] = df["Close"].rolling(window=20).mean()
            df["price_vs_vwap"] = (df["Close"] - df["vwap"]) / df["vwap"] * 100
            df["volume_imbalance"] = 0
            df["price_volume_trend"] = df["Close"].pct_change().rolling(window=5).sum()

        # Trade direction (estimated from price movements)
        df["trade_direction"] = np.where(df["Close"] > df["Open"], 1, -1)
        df["buy_pressure"] = df["trade_direction"].rolling(window=10).sum()

        return df

    def _add_market_depth_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds simulated market depth features.

        These features are proxies for market depth and liquidity, derived from
        price and volume data.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with added market depth features.
        """
        # Depth estimation based on volatility (inverse of price range volatility)
        df["estimated_depth"] = 1 / (df["High"] - df["Low"]).rolling(window=10).std()
        df["depth_ratio"] = (
            df["estimated_depth"] / df["estimated_depth"].rolling(window=20).mean()
        )

        # Liquidity proxy
        if "Volume" in df.columns and df["Volume"].sum() > 0:
            df["liquidity_proxy"] = df["Volume"] / (df["High"] - df["Low"])
        else:
            df["liquidity_proxy"] = 1 / (df["High"] - df["Low"])

        df["liquidity_ratio"] = (
            df["liquidity_proxy"] / df["liquidity_proxy"].rolling(window=20).mean()
        )

        # Market resilience (how quickly price returns after a move)
        df["price_resilience"] = abs(df["Close"] - df["Open"]).rolling(window=5).mean()
        df["resilience_ratio"] = (
            df["price_resilience"] / df["price_resilience"].rolling(window=20).mean()
        )

        return df

    def get_feature_names(self) -> List[str]:
        """
        Returns a list of feature names generated by this class.

        Returns:
            List[str]: A list of the names of the feature columns.
        """
        return [
            "estimated_spread",
            "spread_pct",
            "spread_ma_5",
            "spread_volatility",
            "price_impact_1",
            "price_impact_5",
            "cumulative_impact",
            "effective_spread",
            "effective_spread_pct",
            "vwap",
            "price_vs_vwap",
            "volume_imbalance",
            "price_volume_trend",
            "trade_direction",
            "buy_pressure",
            "estimated_depth",
            "depth_ratio",
            "liquidity_proxy",
            "liquidity_ratio",
            "price_resilience",
            "resilience_ratio",
        ]
