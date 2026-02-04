"""
Advanced Ensemble Model for Trading Predictions
Combines multiple ML models for better accuracy and robustness
"""

import logging
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

from core.indicators import TechnicalIndicators
from core.patterns import PatternDetector

from .model_utils import ModelUtils


class EnsembleModel:
    """
    Advanced ensemble model combining multiple ML algorithms
    """

    def __init__(self, model_config: Dict = None):
        self.model_config = model_config or {
            "random_forest": {"n_estimators": 100, "max_depth": 10, "random_state": 42},
            "gradient_boosting": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "random_state": 42,
            },
            "svm": {"C": 1.0, "kernel": "rbf", "probability": True, "random_state": 42},
            "neural_network": {
                "hidden_layer_sizes": (100, 50),
                "max_iter": 500,
                "random_state": 42,
            },
            "logistic_regression": {"C": 1.0, "random_state": 42},
        }

        self.models = {}
        self.model_weights = {}
        self.feature_importance = {}
        self.training_history = []
        self.is_trained = False

        self.logger = logging.getLogger(__name__)
        self.model_utils = ModelUtils()
        self.technical_indicators = TechnicalIndicators()
        self.pattern_detector = PatternDetector()

    def initialize_models(self):
        """Initialize all models in the ensemble"""
        self.models = {
            "random_forest": RandomForestClassifier(
                **self.model_config["random_forest"]
            ),
            "gradient_boosting": GradientBoostingClassifier(
                **self.model_config["gradient_boosting"]
            ),
            "svm": SVC(**self.model_config["svm"]),
            "neural_network": MLPClassifier(**self.model_config["neural_network"]),
            "logistic_regression": LogisticRegression(
                **self.model_config["logistic_regression"]
            ),
        }

        # Initialize weights equally
        self.model_weights = {
            name: 1.0 / len(self.models) for name in self.models.keys()
        }

        self.logger.info(f"Initialized {len(self.models)} models in ensemble")

    def create_advanced_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced features including technical indicators and patterns
        """
        features_df = data.copy()

        # Basic OHLCV features
        features_df["returns"] = features_df["close"].pct_change()
        features_df["log_returns"] = np.log(
            features_df["close"] / features_df["close"].shift(1)
        )
        features_df["volatility"] = features_df["returns"].rolling(window=20).std()
        features_df["volume_sma"] = features_df["volume"].rolling(window=20).mean()
        features_df["volume_ratio"] = features_df["volume"] / features_df["volume_sma"]

        # Technical indicators
        features_df = self.technical_indicators.add_all_indicators(features_df)

        # Pattern detection
        patterns = self.pattern_detector.detect_patterns(features_df)
        for pattern_name, pattern_values in patterns.items():
            features_df[f"pattern_{pattern_name}"] = pattern_values

        # Advanced features
        features_df["price_momentum"] = (
            features_df["close"] / features_df["close"].shift(5) - 1
        )
        features_df["volume_momentum"] = (
            features_df["volume"] / features_df["volume"].shift(5) - 1
        )

        # Bollinger Bands squeeze
        bb_upper = (
            features_df["close"].rolling(window=20).mean()
            + 2 * features_df["close"].rolling(window=20).std()
        )
        bb_lower = (
            features_df["close"].rolling(window=20).mean()
            - 2 * features_df["close"].rolling(window=20).std()
        )
        features_df["bb_squeeze"] = (bb_upper - bb_lower) / features_df["close"]

        # Market regime features
        features_df["trend_strength"] = self._calculate_trend_strength(features_df)
        features_df["market_regime"] = self._classify_market_regime(features_df)

        # Fractal features
        features_df["fractal_high"] = self._detect_fractals(
            features_df["high"], order=2
        )
        features_df["fractal_low"] = self._detect_fractals(features_df["low"], order=2)

        # Drop NaN values
        features_df = features_df.dropna()

        self.logger.info(f"Created {len(features_df.columns)} features")
        return features_df

    def _calculate_trend_strength(self, data: pd.DataFrame) -> pd.Series:
        """Calculate trend strength using multiple timeframes"""
        short_ma = data["close"].rolling(window=10).mean()
        medium_ma = data["close"].rolling(window=20).mean()
        long_ma = data["close"].rolling(window=50).mean()

        trend_strength = (
            (short_ma > medium_ma).astype(int)
            + (medium_ma > long_ma).astype(int)
            + (data["close"] > short_ma).astype(int)
        ) / 3

        return trend_strength

    def _classify_market_regime(self, data: pd.DataFrame) -> pd.Series:
        """Classify market regime (trending vs ranging)"""
        atr = data["high"] - data["low"]
        atr_ma = atr.rolling(window=14).mean()

        price_range = (
            data["high"].rolling(window=20).max() - data["low"].rolling(window=20).min()
        )
        price_ma = data["close"].rolling(window=20).mean()

        regime = (atr_ma / price_ma > 0.02).astype(int)  # 1 = trending, 0 = ranging
        return regime

    def _detect_fractals(self, series: pd.Series, order: int = 2) -> pd.Series:
        """Detect fractal patterns"""
        fractals = pd.Series(0, index=series.index)

        for i in range(order, len(series) - order):
            # High fractal
            if all(
                series.iloc[i] > series.iloc[i - j] for j in range(1, order + 1)
            ) and all(series.iloc[i] > series.iloc[i + j] for j in range(1, order + 1)):
                fractals.iloc[i] = 1
            # Low fractal
            elif all(
                series.iloc[i] < series.iloc[i - j] for j in range(1, order + 1)
            ) and all(series.iloc[i] < series.iloc[i + j] for j in range(1, order + 1)):
                fractals.iloc[i] = -1

        return fractals

    def train(
        self, X: pd.DataFrame, y: pd.Series, validation_split: float = 0.2
    ) -> Dict:
        """
        Train the ensemble model
        """
        self.logger.info("Starting ensemble model training...")

        # Split data for validation
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        # Initialize models
        self.initialize_models()

        # Train individual models
        model_performance = {}

        for name, model in self.models.items():
            self.logger.info(f"Training {name}...")

            try:
                # Train model
                model.fit(X_train, y_train)

                # Evaluate on validation set
                y_pred = model.predict(X_val)
                accuracy = accuracy_score(y_val, y_pred)
                model_performance[name] = accuracy

                # Store feature importance if available
                if hasattr(model, "feature_importances_"):
                    self.feature_importance[name] = dict(
                        zip(X.columns, model.feature_importances_)
                    )
                elif hasattr(model, "coef_"):
                    self.feature_importance[name] = dict(
                        zip(X.columns, abs(model.coef_[0]))
                    )

                self.logger.info(f"{name} accuracy: {accuracy:.4f}")

            except Exception as e:
                self.logger.error(f"Error training {name}: {str(e)}")
                model_performance[name] = 0.0

        # Calculate weighted performance for ensemble weights
        total_performance = sum(model_performance.values())
        if total_performance > 0:
            self.model_weights = {
                name: perf / total_performance
                for name, perf in model_performance.items()
            }

        # Evaluate ensemble performance
        ensemble_pred = self.predict(X_val)
        ensemble_accuracy = accuracy_score(y_val, ensemble_pred)

        # Store training history
        training_record = {
            "timestamp": datetime.now(),
            "individual_performance": model_performance,
            "ensemble_performance": ensemble_accuracy,
            "model_weights": self.model_weights.copy(),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
        }

        self.training_history.append(training_record)
        self.is_trained = True

        self.logger.info(
            f"Ensemble training completed. Accuracy: {ensemble_accuracy:.4f}"
        )

        return {
            "ensemble_accuracy": ensemble_accuracy,
            "individual_performance": model_performance,
            "model_weights": self.model_weights,
            "feature_importance": self.feature_importance,
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using the ensemble
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        predictions = []

        for name, model in self.models.items():
            try:
                pred = model.predict(X)
                predictions.append(pred)
            except Exception as e:
                self.logger.error(f"Error predicting with {name}: {str(e)}")
                predictions.append(np.zeros(len(X)))

        # Weighted ensemble prediction
        ensemble_pred = np.zeros(len(X))
        for i, (name, pred) in enumerate(zip(self.models.keys(), predictions)):
            ensemble_pred += self.model_weights[name] * pred

        # Convert to binary predictions
        return (ensemble_pred > 0.5).astype(int)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        probabilities = []

        for name, model in self.models.items():
            try:
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(X)[
                        :, 1
                    ]  # Get positive class probability
                else:
                    # For models without predict_proba, use distance from decision boundary
                    pred = model.predict(X)
                    proba = pred.astype(float)

                probabilities.append(proba)
            except Exception as e:
                self.logger.error(f"Error getting probabilities from {name}: {str(e)}")
                probabilities.append(np.full(len(X), 0.5))

        # Weighted ensemble probabilities
        ensemble_proba = np.zeros(len(X))
        for i, (name, proba) in enumerate(zip(self.models.keys(), probabilities)):
            ensemble_proba += self.model_weights[name] * proba

        return ensemble_proba

    def update_model_weights(self, recent_performance: Dict[str, float]):
        """
        Update model weights based on recent performance
        """
        self.logger.info("Updating model weights based on recent performance")

        total_performance = sum(recent_performance.values())
        if total_performance > 0:
            self.model_weights = {
                name: perf / total_performance
                for name, perf in recent_performance.items()
            }

        self.logger.info(f"Updated weights: {self.model_weights}")

    def save_model(self, filepath: str):
        """Save the ensemble model"""
        model_data = {
            "models": self.models,
            "model_weights": self.model_weights,
            "feature_importance": self.feature_importance,
            "training_history": self.training_history,
            "is_trained": self.is_trained,
            "model_config": self.model_config,
        }

        joblib.dump(model_data, filepath)
        self.logger.info(f"Ensemble model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load the ensemble model"""
        model_data = joblib.load(filepath)

        self.models = model_data["models"]
        self.model_weights = model_data["model_weights"]
        self.feature_importance = model_data["feature_importance"]
        self.training_history = model_data["training_history"]
        self.is_trained = model_data["is_trained"]
        self.model_config = model_data["model_config"]

        self.logger.info(f"Ensemble model loaded from {filepath}")

    def get_model_status(self) -> Dict:
        """Get current model status"""
        return {
            "is_trained": self.is_trained,
            "num_models": len(self.models),
            "model_weights": self.model_weights,
            "last_training": (
                self.training_history[-1] if self.training_history else None
            ),
            "feature_count": (
                len(self.feature_importance.get(list(self.models.keys())[0], {}))
                if self.models
                else 0
            ),
        }
