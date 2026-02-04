"""
Sentiment Features for GenX FX Trading System
Features related to market sentiment and news analysis
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class SentimentFeatures:
    """
    A feature engineering engine for generating sentiment-based features.

    This class creates features that attempt to proxy market sentiment using
    price action, volatility, and simulated news and social media data.

    Attributes:
        feature_columns (List[str]): A list to store the names of generated features.
        sentiment_cache (Dict): A cache for storing sentiment data.
    """

    def __init__(self):
        """Initializes the SentimentFeatures engine."""
        self.feature_columns = []
        self.sentiment_cache: Dict[str, Any] = {}

    def generate_features(
        self, df: pd.DataFrame, symbol: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Generates a set of sentiment-based features.

        Args:
            df (pd.DataFrame): A DataFrame with OHLCV data.
            symbol (Optional[str]): The trading symbol (currently unused).

        Returns:
            pd.DataFrame: The DataFrame enriched with sentiment features.
        """
        if df.empty:
            return df

        features_df = df.copy()

        try:
            # Market sentiment features
            features_df = self._add_market_sentiment_features(features_df)

            # News sentiment features (simulated)
            features_df = self._add_news_sentiment_features(features_df, symbol)

            # Social media sentiment (simulated)
            features_df = self._add_social_sentiment_features(features_df, symbol)

            # Fear & Greed indicators
            features_df = self._add_fear_greed_features(features_df)

            # Fill NaN values
            features_df = features_df.fillna(method="ffill").fillna(0)

        except Exception as e:
            print(f"Warning: Error generating sentiment features: {e}")
            return df

        return features_df

    def _add_market_sentiment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds market sentiment indicators based on price action.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with added market sentiment features.
        """
        # Bull/Bear sentiment from candlesticks
        df["bullish_candles"] = (df["Close"] > df["Open"]).astype(int)
        df["bearish_candles"] = (df["Close"] < df["Open"]).astype(int)
        df["bull_bear_ratio"] = df["bullish_candles"].rolling(window=20).sum() / 20

        # Market momentum sentiment
        df["momentum_sentiment"] = (
            df["Close"].pct_change(periods=5).rolling(window=10).mean()
        )
        df["sentiment_strength"] = abs(df["momentum_sentiment"])

        # Volatility sentiment (high volatility suggests uncertainty)
        df["volatility_sentiment"] = (
            df["Close"].rolling(window=20).std() / df["Close"].rolling(window=20).mean()
        )
        df["uncertainty_index"] = (
            df["volatility_sentiment"]
            - df["volatility_sentiment"].rolling(window=50).mean()
        ) / df["volatility_sentiment"].rolling(window=50).std()

        # Price position sentiment
        price_range = (
            df["High"].rolling(window=20).max() - df["Low"].rolling(window=20).min()
        )
        df["price_position"] = (
            df["Close"] - df["Low"].rolling(window=20).min()
        ) / price_range
        df["sentiment_extreme"] = np.where(
            df["price_position"] > 0.8, 1, np.where(df["price_position"] < 0.2, -1, 0)
        )

        return df

    def _add_news_sentiment_features(
        self, df: pd.DataFrame, symbol: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Adds simulated news sentiment features.

        Args:
            df (pd.DataFrame): The input DataFrame.
            symbol (Optional[str]): The trading symbol.

        Returns:
            pd.DataFrame: The DataFrame with added news sentiment features.
        """
        # News impact estimation (higher volatility = more news impact)
        df["news_impact"] = (df["High"] - df["Low"]) / df["Close"] * 100
        df["news_sentiment"] = np.where(
            df["Close"] > df["Open"],
            df["news_impact"] * 0.5,  # Positive news proxy
            df["news_impact"] * -0.5,  # Negative news proxy
        )

        # News frequency (estimated from volatility spikes)
        df["volatility_spike"] = df["news_impact"] > df["news_impact"].rolling(
            window=20
        ).quantile(0.8)
        df["news_frequency"] = df["volatility_spike"].rolling(window=10).sum()

        # Economic calendar impact (simulated)
        if not df.index.empty and isinstance(df.index, pd.DatetimeIndex):
            df["calendar_impact"] = np.random.normal(0, 0.1, len(df))
            weekday_multiplier = np.where(df.index.dayofweek < 5, 1.2, 0.8)
            df["calendar_impact"] *= weekday_multiplier
        else:
            df["calendar_impact"] = 0

        return df

    def _add_social_sentiment_features(
        self, df: pd.DataFrame, symbol: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Adds simulated social media sentiment features.

        Args:
            df (pd.DataFrame): The input DataFrame.
            symbol (Optional[str]): The trading symbol.

        Returns:
            pd.DataFrame: The DataFrame with added social media features.
        """
        # Simulated social sentiment based on price momentum
        price_momentum = df["Close"].pct_change(periods=3).rolling(window=5).mean()
        df["twitter_sentiment"] = np.tanh(price_momentum * 10)
        df["twitter_volume"] = abs(price_momentum) * 100

        # Reddit sentiment proxy
        df["reddit_sentiment"] = df["twitter_sentiment"].rolling(window=3).mean()
        df["reddit_mentions"] = df["twitter_volume"].rolling(window=2).sum()

        # Social media trend
        df["social_trend"] = (df["twitter_sentiment"] + df["reddit_sentiment"]) / 2
        df["social_momentum"] = df["social_trend"].pct_change().rolling(window=5).mean()

        # Influencer sentiment (simulated high-impact accounts)
        df["influencer_sentiment"] = np.where(
            abs(price_momentum) > price_momentum.rolling(window=20).std(),
            np.sign(price_momentum) * 0.8,
            0,
        )

        return df

    def _add_fear_greed_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds features that act as proxies for fear and greed in the market.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with added fear and greed features.
        """
        # VIX-like fear index based on volatility
        rolling_vol = df["Close"].rolling(window=20).std()
        vol_percentile = rolling_vol.rolling(window=50).rank(pct=True)
        df["fear_index"] = vol_percentile * 100
        df["greed_index"] = 100 - df["fear_index"]

        # Put/Call ratio proxy (based on price action)
        downward_moves = (df["Close"] < df["Close"].shift(1)).rolling(window=10).sum()
        upward_moves = (df["Close"] > df["Close"].shift(1)).rolling(window=10).sum()
        df["put_call_ratio"] = downward_moves / (upward_moves + 1e-6)

        # Market stress indicators
        df["stress_indicator"] = np.where(df["fear_index"] > 70, 1, 0)
        df["euphoria_indicator"] = np.where(df["greed_index"] > 80, 1, 0)

        # Sentiment oscillator
        df["sentiment_oscillator"] = (df["greed_index"] - 50) / 50
        df["sentiment_extreme_flag"] = np.where(
            abs(df["sentiment_oscillator"]) > 0.6, 1, 0
        )

        return df

    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Gets a summary of the current sentiment based on the latest data point.

        Args:
            df (pd.DataFrame): The DataFrame with sentiment features.

        Returns:
            Dict[str, float]: A dictionary of current sentiment metrics.
        """
        if df.empty or len(df) < 5:
            return {}

        try:
            latest = df.iloc[-1]
            recent = df.tail(5)

            summary = {
                "overall_sentiment": latest.get("social_trend", 0),
                "sentiment_strength": latest.get("sentiment_strength", 0),
                "fear_level": latest.get("fear_index", 50),
                "greed_level": latest.get("greed_index", 50),
                "news_impact": latest.get("news_impact", 0),
                "social_momentum": latest.get("social_momentum", 0),
                "market_stress": latest.get("stress_indicator", 0),
                "sentiment_trend": (
                    recent["social_trend"].mean()
                    if "social_trend" in recent.columns
                    else 0
                ),
            }

            return summary

        except Exception as e:
            print(f"Warning: Error calculating sentiment summary: {e}")
            return {}

    def get_feature_names(self) -> List[str]:
        """
        Returns a list of feature names generated by this class.

        Returns:
            List[str]: A list of the names of the feature columns.
        """
        return [
            "bullish_candles",
            "bearish_candles",
            "bull_bear_ratio",
            "momentum_sentiment",
            "sentiment_strength",
            "volatility_sentiment",
            "uncertainty_index",
            "price_position",
            "sentiment_extreme",
            "news_impact",
            "news_sentiment",
            "news_frequency",
            "calendar_impact",
            "twitter_sentiment",
            "twitter_volume",
            "reddit_sentiment",
            "reddit_mentions",
            "social_trend",
            "social_momentum",
            "influencer_sentiment",
            "fear_index",
            "greed_index",
            "put_call_ratio",
            "stress_indicator",
            "euphoria_indicator",
            "sentiment_oscillator",
            "sentiment_extreme_flag",
        ]
