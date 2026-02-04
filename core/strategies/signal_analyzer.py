from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


class SignalAnalyzer:
    """
    Analyzes and filters trading signals based on various criteria.

    This class processes raw detected patterns or AI predictions, calculates
    confidence scores, and applies a series of filters to produce a list of
    high-quality trading signals.

    Attributes:
        signal_history (List[Dict]): A history of recently generated signals.
        filters (Dict[str, Callable]): A dictionary of filter functions to be applied.
    """

    def __init__(self):
        """Initializes the SignalAnalyzer."""
        self.signal_history: List[Dict] = []
        self.filters = {
            "strength": self._filter_by_strength,
            "time": self._filter_by_time,
            "confluence": self._filter_by_confluence,
        }

    def analyze_signals(
        self, patterns: Dict[str, List], market_data: pd.DataFrame
    ) -> List[Dict]:
        """
        Analyzes detected patterns and generates a filtered list of trading signals.

        Args:
            patterns (Dict[str, List]): A dictionary where keys are pattern types
                                        and values are lists of detected patterns.
            market_data (pd.DataFrame): DataFrame with market data for context.

        Returns:
            List[Dict]: A sorted and filtered list of trading signals.
        """
        all_signals = []

        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                timestamp = pattern.get("timestamp")
                if not timestamp:
                    continue

                signal = {
                    "id": f"{pattern_type}_{len(all_signals)}",
                    "pattern_type": pattern_type,
                    "pattern": pattern.get("type"),
                    "timestamp": timestamp,
                    "strength": pattern.get("strength"),
                    "direction": pattern.get("direction"),
                    "price": self._get_price_at_timestamp(market_data, timestamp),
                    "confidence": self._calculate_confidence(pattern, market_data),
                }
                all_signals.append(signal)

        # Apply filters
        filtered_signals = self._apply_filters(all_signals)

        # Sort by confidence and timestamp
        filtered_signals.sort(
            key=lambda x: (x["confidence"], x["timestamp"]), reverse=True
        )

        return filtered_signals

    def generate_signals_from_predictions(
        self, predictions: pd.DataFrame
    ) -> List[Dict]:
        """
        Generates trading signals from a DataFrame of AI model predictions.

        Args:
            predictions (pd.DataFrame): A DataFrame containing model predictions,
                                        indexed by timestamp. Expected columns
                                        include 'prediction' and 'close'.

        Returns:
            List[Dict]: A list of generated signal dictionaries.
        """
        signals = []
        for index, row in predictions.iterrows():
            direction = "neutral"
            pattern = "price_stable"
            if row["prediction"] == 1:
                direction = "bullish"
                pattern = "price_increase"
            elif row["prediction"] == 0:  # Assuming 0 is bearish
                direction = "bearish"
                pattern = "price_decrease"

            if direction != "neutral":
                signals.append(
                    {
                        "id": f"ai_model_{len(signals)}",
                        "pattern_type": "ai_model",
                        "pattern": pattern,
                        "timestamp": index,
                        "strength": 1,  # Placeholder strength
                        "direction": direction,
                        "price": row["close"],
                        "confidence": 1,  # Placeholder confidence
                    }
                )
        return signals

    def _get_price_at_timestamp(self, data: pd.DataFrame, timestamp) -> float:
        """
        Gets the closing price at a specific timestamp from the market data.

        If the exact timestamp is not found, it finds the nearest available one.

        Args:
            data (pd.DataFrame): The market data DataFrame.
            timestamp: The timestamp to look up.

        Returns:
            float: The closing price at or nearest to the timestamp.
        """
        try:
            if timestamp in data.index:
                return data.loc[timestamp, "close"]
            else:
                # Find nearest timestamp
                nearest_idx = data.index.get_indexer([timestamp], method="nearest")[0]
                return data.iloc[nearest_idx]["close"]
        except (KeyError, IndexError):
            return 0.0

    def _calculate_confidence(self, pattern: Dict, market_data: pd.DataFrame) -> float:
        """
        Calculates a confidence score for a given pattern.

        The confidence is based on the pattern's intrinsic strength, adjusted by
        market conditions like volume.

        Args:
            pattern (Dict): The pattern dictionary.
            market_data (pd.DataFrame): The market data for context.

        Returns:
            float: The calculated confidence score.
        """
        base_confidence = min(pattern.get("strength", 0.5), 1.0)

        # Adjust based on market volume at the time of the pattern
        volume_factor = 1.0
        if "volume" in market_data.columns:
            try:
                timestamp = pattern["timestamp"]
                if timestamp in market_data.index:
                    current_volume = market_data.loc[timestamp, "volume"]
                    avg_volume = market_data["volume"].rolling(20).mean().loc[timestamp]
                    if avg_volume > 0:
                        volume_factor = min(current_volume / avg_volume, 2.0)
            except (KeyError, IndexError):
                pass  # Ignore if timestamp is out of bounds

        return base_confidence * volume_factor

    def _apply_filters(self, signals: List[Dict]) -> List[Dict]:
        """
        Applies a series of pre-defined filters to a list of signals.

        Args:
            signals (List[Dict]): The list of signals to be filtered.

        Returns:
            List[Dict]: The list of signals after applying all filters.
        """
        filtered_signals = signals
        for filter_func in self.filters.values():
            filtered_signals = filter_func(filtered_signals)
        return filtered_signals

    def _filter_by_strength(self, signals: List[Dict]) -> List[Dict]:
        """Filters signals by a minimum strength threshold."""
        min_strength = 0.5
        return [s for s in signals if s.get("strength", 0) >= min_strength]

    def _filter_by_time(self, signals: List[Dict]) -> List[Dict]:
        """
        Filters signals to include only those generated within a recent time window.

        FIXME: This filter is currently disabled.
        """
        # cutoff_time = datetime.now() - timedelta(hours=24)
        # return [s for s in signals if s['timestamp'] >= cutoff_time]
        return signals  # FIXME: Re-enable this filter with proper timezone handling.

    def _filter_by_confluence(self, signals: List[Dict]) -> List[Dict]:
        """
        Filters for signals that have confluence.

        Confluence is defined as multiple signals occurring in the same direction
        within the same hour. The strongest signal from a confluent group is kept.

        Args:
            signals (List[Dict]): The list of signals to filter.

        Returns:
            List[Dict]: A list of signals that have confluence.
        """
        signal_groups: Dict[str, List[Dict]] = {}

        for signal in signals:
            time_key = signal["timestamp"].strftime("%Y-%m-%d %H")
            direction_key = f"{time_key}_{signal['direction']}"

            if direction_key not in signal_groups:
                signal_groups[direction_key] = []
            signal_groups[direction_key].append(signal)

        # Keep only signals from groups that have confluence
        confluent_signals = []
        for group in signal_groups.values():
            if len(group) >= 2:  # At least 2 signals in the same hour and direction
                # Take the signal with the highest confidence from the group
                strongest_signal = max(group, key=lambda x: x.get("confidence", 0))
                strongest_signal["confluence_count"] = len(group)
                confluent_signals.append(strongest_signal)

        return confluent_signals

    def update_signal_history(self, signals: List[Dict]):
        """
        Updates the signal history with new signals and prunes old ones.

        Args:
            signals (List[Dict]): The new signals to add to the history.
        """
        self.signal_history.extend(signals)

        # Keep only signals from the last 7 days
        cutoff_time = datetime.now() - timedelta(days=7)
        self.signal_history = [
            s for s in self.signal_history if s["timestamp"] >= cutoff_time
        ]
