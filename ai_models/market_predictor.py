"""
Market prediction using machine learning and pattern analysis
"""

import os
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class MarketPredictor:
    """
    Machine learning-based market prediction
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = model_path or "models/market_predictor.pkl"

        # Load existing model if available
        if os.path.exists(self.model_path):
            self.load_model()

    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for machine learning model

        Args:
            data: Market data with OHLCV

        Returns:
            Feature array
        """
        features = []

        # Price-based features
        features.extend(
            [
                data["close"].pct_change().fillna(0),  # Returns
                data["high"] / data["close"] - 1,  # High ratio
                data["low"] / data["close"] - 1,  # Low ratio
                data["volume"].pct_change().fillna(0),  # Volume change
            ]
        )

        # Technical indicators
        close_prices = data["close"].values

        # Moving averages
        for period in [5, 10, 20, 50]:
            ma = pd.Series(close_prices).rolling(period).mean()
            features.append((close_prices - ma) / ma)

        # RSI
        rsi = self._calculate_rsi(close_prices)
        features.append(rsi / 100)  # Normalize to 0-1

        # MACD
        macd, signal = self._calculate_macd(close_prices)
        features.extend([macd, signal])

        # Bollinger Bands
        bb_upper, bb_lower = self._calculate_bollinger_bands(close_prices)
        features.extend(
            [(close_prices - bb_upper) / bb_upper, (close_prices - bb_lower) / bb_lower]
        )

        # Combine all features
        feature_matrix = np.column_stack(features)

        # Handle NaN values
        feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)

        return feature_matrix

    def train_model(self, data: pd.DataFrame, labels: np.ndarray):
        """
        Train the prediction model

        Args:
            data: Training data
            labels: Target labels (0=sell, 1=hold, 2=buy)
        """
        features = self.prepare_features(data)

        # Scale features
        features_scaled = self.scaler.fit_transform(features)

        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.model.fit(features_scaled, labels)

        self.is_trained = True

        # Save model
        self.save_model()

    def predict(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new data

        Args:
            data: Market data to predict on

        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")

        features = self.prepare_features(data)
        features_scaled = self.scaler.transform(features)

        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)

        return predictions, probabilities

    def get_prediction_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        Get trading signals based on predictions

        Args:
            data: Market data

        Returns:
            List of prediction signals
        """
        if not self.is_trained:
            return []

        predictions, probabilities = self.predict(data)

        signals = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            if i < len(data):
                signal = {
                    "type": "ml_prediction",
                    "timestamp": data.index[i],
                    "prediction": pred,
                    "confidence": np.max(prob),
                    "direction": self._prediction_to_direction(pred),
                    "strength": np.max(prob),
                }
                signals.append(signal)

        return signals

    def _prediction_to_direction(self, prediction: int) -> str:
        """Convert prediction to direction"""
        if prediction == 0:
            return "bearish"
        elif prediction == 2:
            return "bullish"
        else:
            return "neutral"

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate RSI"""
        delta = np.diff(prices)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = pd.Series(gain).rolling(period).mean()
        avg_loss = pd.Series(loss).rolling(period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.values

    def _calculate_macd(self, prices: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate MACD"""
        ema12 = pd.Series(prices).ewm(span=12).mean()
        ema26 = pd.Series(prices).ewm(span=26).mean()

        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()

        return macd.values, signal.values

    def _calculate_bollinger_bands(
        self, prices: np.ndarray, period: int = 20
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands"""
        sma = pd.Series(prices).rolling(period).mean()
        std = pd.Series(prices).rolling(period).std()

        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        return upper_band.values, lower_band.values

    def save_model(self):
        """Save trained model to disk"""
        if self.is_trained:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(
                {
                    "model": self.model,
                    "scaler": self.scaler,
                    "is_trained": self.is_trained,
                },
                self.model_path,
            )

    def load_model(self):
        """Load trained model from disk"""
        if os.path.exists(self.model_path):
            saved_data = joblib.load(self.model_path)
            self.model = saved_data["model"]
            self.scaler = saved_data["scaler"]
            self.is_trained = saved_data["is_trained"]
