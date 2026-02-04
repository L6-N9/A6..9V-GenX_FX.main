"""
Advanced Ensemble AI Predictor for Forex Trading
Combines multiple ML models for robust trading signal generation
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import xgboost as xgb

# ML imports
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_recall_fscore_support,
)
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.svm import SVC

from core.feature_engineering.market_microstructure import MarketMicrostructureFeatures
from core.feature_engineering.sentiment_features import SentimentFeatures
from core.feature_engineering.technical_features import TechnicalFeatureEngine
from utils.model_validation import ModelValidator

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    An advanced ensemble predictor for generating forex trading signals.

    This class combines multiple machine learning models to produce a more robust
    prediction. It integrates various feature engineering engines, handles model
    training, persistence, and generates weighted predictions based on model
    performance.

    Attributes:
        config (Dict[str, Any]): Configuration settings for the predictor.
        models (Dict): A dictionary to store the trained models for each symbol.
        scalers (Dict): A dictionary to store the feature scalers for each model.
        feature_engine (TechnicalFeatureEngine): The engine for technical features.
        microstructure_engine (MarketMicrostructureFeatures): The engine for market microstructure features.
        sentiment_engine (SentimentFeatures): The engine for sentiment features.
        validator (ModelValidator): The utility for model validation.
        model_dir (Path): The directory where models are saved.
        is_initialized (bool): A flag indicating if the predictor is initialized.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the EnsemblePredictor.

        Args:
            config (Dict[str, Any]): A dictionary containing configuration parameters.
        """
        self.config = config
        self.models: Dict[str, Dict[str, Any]] = {}
        self.scalers: Dict[str, Dict[str, Any]] = {}
        self.feature_engine = TechnicalFeatureEngine()
        self.microstructure_engine = MarketMicrostructureFeatures()
        self.sentiment_engine = SentimentFeatures()
        self.validator = ModelValidator()

        self.model_weights: Dict[str, Dict[str, float]] = {}
        self.feature_importance: Dict[str, Any] = {}
        self.performance_history: Dict[str, Any] = {}
        self.last_retrain_time: Dict[str, datetime] = {}

        # Model directory
        self.model_dir = Path("ai_models/ensemble_models")
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.is_initialized = False
        logger.info("Ensemble Predictor initialized")

    async def initialize(self):
        """
        Initializes the ensemble predictor and its components.

        This method loads any existing persisted models and initializes the
        various feature engineering engines.

        Raises:
            Exception: If initialization of any component fails.
        """
        try:
            # Load existing models if available
            await self._load_models()

            # Initialize feature engines
            # Note: Placeholder initialize methods are assumed for engines.
            # await self.feature_engine.initialize()
            # await self.microstructure_engine.initialize()
            # await self.sentiment_engine.initialize()

            self.is_initialized = True
            logger.info("Ensemble Predictor initialization complete")

        except Exception as e:
            logger.error(f"Error initializing ensemble predictor: {e}")
            raise

    async def predict(
        self,
        symbol: str,
        data: pd.DataFrame,
        multi_timeframe_data: Optional[Dict[str, pd.DataFrame]] = None,
    ) -> Dict[str, Any]:
        """
        Generates a trading prediction using an ensemble of models.

        Args:
            symbol (str): The currency pair to predict for (e.g., 'EURUSD').
            data (pd.DataFrame): The primary timeframe data for feature generation.
            multi_timeframe_data (Optional[Dict[str, pd.DataFrame]]): Data from other
                                                                    timeframes.

        Returns:
            Dict[str, Any]: A dictionary containing the prediction details, including
                            direction, confidence, and individual model scores.
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Generate features
            features = await self._generate_features(symbol, data, multi_timeframe_data)

            if features is None or len(features) == 0:
                return self._get_default_prediction()

            # Get predictions from all models
            model_predictions = await self._get_model_predictions(symbol, features)

            # Calculate ensemble prediction
            ensemble_result = self._calculate_ensemble_prediction(model_predictions)

            # Add metadata
            ensemble_result.update(
                {
                    "symbol": symbol,
                    "timestamp": datetime.now(),
                    "feature_count": len(features),
                    "model_count": len(model_predictions),
                    "model_scores": model_predictions,
                }
            )

            logger.debug(
                f"Generated prediction for {symbol}: confidence={ensemble_result['confidence']:.3f}"
            )
            return ensemble_result

        except Exception as e:
            logger.error(f"Error generating prediction for {symbol}: {e}")
            return self._get_default_prediction()

    async def _generate_features(
        self,
        symbol: str,
        data: pd.DataFrame,
        multi_timeframe_data: Optional[Dict[str, pd.DataFrame]] = None,
    ) -> Optional[np.ndarray]:
        """
        Generates a comprehensive feature set for a given data point.

        Args:
            symbol (str): The trading symbol.
            data (pd.DataFrame): The primary timeframe data.
            multi_timeframe_data (Optional[Dict[str, pd.DataFrame]]): Additional timeframe data.

        Returns:
            Optional[np.ndarray]: A NumPy array of features, or None if data is insufficient.
        """
        try:
            if len(data) < 50:  # Minimum data required for some indicators
                logger.warning(f"Insufficient data for feature generation on {symbol}")
                return None

            # Generate features from different engines
            technical_df = self.feature_engine.generate_features(data)
            microstructure_df = self.microstructure_engine.generate_features(
                technical_df
            )

            # For prediction, we use the latest row
            latest_features = microstructure_df.iloc[-1]

            # Combine features into a single list
            # Note: This part is simplified. A real implementation would carefully select
            # and align features from the generated DataFrames.
            features = latest_features.values.tolist()

            # Multi-timeframe features
            if multi_timeframe_data:
                mtf_features = await self._generate_multi_timeframe_features(
                    multi_timeframe_data
                )
                features.extend(mtf_features)

            # Sentiment features
            try:
                sentiment_features = await self.sentiment_engine.get_sentiment_summary(
                    data
                )
                # Convert dict to list of features
                features.extend(list(sentiment_features.values()))
            except Exception:
                # Sentiment features are optional
                features.extend([0.0] * 8)  # Placeholder for 8 sentiment features

            # Time-based features
            time_features = self._generate_time_features(data.index[-1])
            features.extend(time_features)

            return np.array(features).reshape(1, -1)

        except Exception as e:
            logger.error(f"Error generating features for {symbol}: {e}")
            return None

    async def _generate_multi_timeframe_features(
        self, multi_timeframe_data: Dict[str, pd.DataFrame]
    ) -> List[float]:
        """
        Generates features based on data from multiple timeframes.

        Args:
            multi_timeframe_data (Dict[str, pd.DataFrame]): A dictionary mapping
                                                            timeframes to dataframes.

        Returns:
            List[float]: A list of multi-timeframe features.
        """
        features = []

        # Standard timeframes to analyze
        timeframes = ["M15", "H1", "H4", "D1"]

        for tf in timeframes:
            if tf in multi_timeframe_data:
                data = multi_timeframe_data[tf]
                if len(data) >= 20:
                    # Trend features
                    sma_20 = data["close"].rolling(20).mean().iloc[-1]
                    sma_50 = (
                        data["close"].rolling(50).mean().iloc[-1]
                        if len(data) >= 50
                        else sma_20
                    )
                    current_price = data["close"].iloc[-1]

                    trend_strength = (current_price - sma_20) / sma_20
                    trend_consistency = 1.0 if sma_20 > sma_50 else -1.0

                    # Volatility features
                    volatility = (
                        data["close"].rolling(20).std().iloc[-1] / current_price
                    )

                    # Momentum features
                    roc = (
                        (current_price - data["close"].iloc[-10])
                        / data["close"].iloc[-10]
                        if len(data) >= 10
                        else 0
                    )

                    features.extend(
                        [trend_strength, trend_consistency, volatility, roc]
                    )
                else:
                    features.extend([0.0, 0.0, 0.0, 0.0])

        return features

    def _generate_time_features(self, timestamp: datetime) -> List[float]:
        """
        Generates time-based features from a timestamp.

        This includes cyclical features for hour and day of the week, and
        indicators for market sessions.

        Args:
            timestamp (datetime): The timestamp to generate features from.

        Returns:
            List[float]: A list of time-based features.
        """
        features = []

        # Hour of day (cyclical)
        hour_sin = np.sin(2 * np.pi * timestamp.hour / 24)
        hour_cos = np.cos(2 * np.pi * timestamp.hour / 24)
        features.extend([hour_sin, hour_cos])

        # Day of week (cyclical)
        dow_sin = np.sin(2 * np.pi * timestamp.weekday() / 7)
        dow_cos = np.cos(2 * np.pi * timestamp.weekday() / 7)
        features.extend([dow_sin, dow_cos])

        # Market session indicators (UTC-based)
        london_session = 1.0 if 7 <= timestamp.hour < 16 else 0.0
        ny_session = 1.0 if 12 <= timestamp.hour < 21 else 0.0
        asian_session = 1.0 if 23 <= timestamp.hour or timestamp.hour < 8 else 0.0
        overlap_session = 1.0 if 12 <= timestamp.hour < 16 else 0.0  # London/NY

        features.extend([london_session, ny_session, asian_session, overlap_session])

        return features

    async def _get_model_predictions(
        self, symbol: str, features: np.ndarray
    ) -> Dict[str, float]:
        """
        Gets predictions from all individual models in the ensemble.

        Args:
            symbol (str): The trading symbol.
            features (np.ndarray): The feature array for prediction.

        Returns:
            Dict[str, float]: A dictionary mapping model names to their prediction scores.
        """
        predictions: Dict[str, float] = {}

        # Ensure models exist for this symbol
        if symbol not in self.models:
            await self._create_models_for_symbol(symbol)

        symbol_models = self.models[symbol]
        symbol_scalers = self.scalers[symbol]

        for model_name, model in symbol_models.items():
            try:
                # Scale features
                scaler = symbol_scalers[model_name]
                scaled_features = scaler.transform(features)

                # Get prediction
                if hasattr(model, "predict_proba"):
                    # Classification models
                    proba = model.predict_proba(scaled_features)[0]
                    # Convert to direction score (-1 to 1)
                    if len(proba) >= 2:
                        direction_score = (
                            proba[1] - proba[0]
                        )  # Positive for buy, negative for sell
                    else:
                        direction_score = 0.0
                else:
                    # Regression models
                    direction_score = model.predict(scaled_features)[0]

                # Apply model weight
                weight = self.model_weights.get(symbol, {}).get(model_name, 1.0)
                predictions[model_name] = direction_score * weight

            except Exception as e:
                logger.error(
                    f"Error getting prediction from {model_name} for {symbol}: {e}"
                )
                predictions[model_name] = 0.0

        return predictions

    def _calculate_ensemble_prediction(
        self, model_predictions: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculates the final ensemble prediction from individual model outputs.

        Args:
            model_predictions (Dict[str, float]): The predictions from individual models.

        Returns:
            Dict[str, Any]: A dictionary with the final direction, confidence, and other metrics.
        """
        if not model_predictions:
            return self._get_default_prediction()

        # Calculate weighted average
        predictions = list(model_predictions.values())
        weights = [abs(p) for p in predictions]  # Use absolute values as weights

        if sum(weights) == 0:
            return self._get_default_prediction()

        # Weighted average direction
        weighted_direction = sum(p * w for p, w in zip(predictions, weights)) / sum(
            weights
        )

        # Calculate confidence based on agreement between models
        agreement = self._calculate_model_agreement(predictions)
        base_confidence = min(abs(weighted_direction), 1.0)
        confidence = base_confidence * agreement

        # Determine signal strength
        signal_strength = self._calculate_signal_strength(
            weighted_direction, confidence
        )

        return {
            "direction": weighted_direction,
            "confidence": confidence,
            "signal_strength": signal_strength,
            "model_agreement": agreement,
            "fundamental_score": 0.5,  # Placeholder for fundamental analysis
        }

    def _calculate_model_agreement(self, predictions: List[float]) -> float:
        """
        Calculates the agreement between models.

        Agreement is defined as the ratio of the most common signal type
        (buy, sell, or hold) to the total number of models.

        Args:
            predictions (List[float]): A list of prediction scores from the models.

        Returns:
            float: The agreement ratio, from 0.0 to 1.0.
        """
        if len(predictions) < 2:
            return 0.5

        # Convert to buy/sell/hold signals
        signals = []
        for pred in predictions:
            if pred > 0.1:
                signals.append(1)  # Buy
            elif pred < -0.1:
                signals.append(-1)  # Sell
            else:
                signals.append(0)  # Hold

        # Calculate agreement
        if not signals:
            return 0.5

        most_common = max(set(signals), key=signals.count)
        agreement_count = signals.count(most_common)
        agreement_ratio = agreement_count / len(signals)

        return agreement_ratio

    def _calculate_signal_strength(self, direction: float, confidence: float) -> str:
        """
        Categorizes the signal strength based on direction and confidence.

        Args:
            direction (float): The directional score of the signal.
            confidence (float): The confidence score of the signal.

        Returns:
            str: A category for the signal strength (e.g., "STRONG", "WEAK").
        """
        strength_score = abs(direction) * confidence

        if strength_score >= 0.8:
            return "VERY_STRONG"
        elif strength_score >= 0.6:
            return "STRONG"
        elif strength_score >= 0.4:
            return "MODERATE"
        else:
            return "WEAK"

    def _get_default_prediction(self) -> Dict[str, Any]:
        """
        Returns a default, neutral prediction when a valid one cannot be generated.

        Returns:
            Dict[str, Any]: A dictionary with neutral prediction values.
        """
        return {
            "direction": 0.0,
            "confidence": 0.0,
            "signal_strength": "WEAK",
            "model_agreement": 0.0,
            "fundamental_score": 0.5,
            "model_scores": {},
        }

    async def _create_models_for_symbol(self, symbol: str):
        """
        Creates and initializes a set of models and scalers for a new symbol.

        Args:
            symbol (str): The symbol for which to create models.
        """
        logger.info(f"Creating new model set for symbol: {symbol}")

        # Initialize model containers
        self.models[symbol] = {}
        self.scalers[symbol] = {}
        self.model_weights[symbol] = {}

        # Define model configurations
        model_configs = {
            "random_forest": {
                "model": RandomForestClassifier(
                    n_estimators=100, max_depth=10, min_samples_split=5, random_state=42
                ),
                "scaler": RobustScaler(),
            },
            "xgboost": {
                "model": xgb.XGBClassifier(
                    n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
                ),
                "scaler": StandardScaler(),
            },
            "lightgbm": {
                "model": lgb.LGBMClassifier(
                    n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
                ),
                "scaler": StandardScaler(),
            },
            "gradient_boosting": {
                "model": GradientBoostingClassifier(
                    n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42
                ),
                "scaler": RobustScaler(),
            },
            "svm": {
                "model": SVC(kernel="rbf", probability=True, random_state=42),
                "scaler": StandardScaler(),
            },
        }

        # Initialize models
        for model_name, config in model_configs.items():
            self.models[symbol][model_name] = config["model"]
            self.scalers[symbol][model_name] = config["scaler"]
            self.model_weights[symbol][model_name] = 1.0

        logger.info(f"Created {len(model_configs)} models for {symbol}")

    async def train_models(
        self,
        symbol: str,
        training_data: pd.DataFrame,
        target_column: str = "target",
    ) -> Dict[str, Any]:
        """
        Trains all models in the ensemble for a specific symbol.

        Args:
            symbol (str): The symbol to train models for.
            training_data (pd.DataFrame): The DataFrame containing training data.
            target_column (str): The name of the target variable column.

        Returns:
            Dict[str, Any]: A dictionary summarizing the training results.
        """
        try:
            logger.info(f"Starting model training for {symbol}")

            if symbol not in self.models:
                await self._create_models_for_symbol(symbol)

            # Prepare training data
            X, y = await self._prepare_training_data(
                symbol, training_data, target_column
            )

            if len(X) < 100:  # Minimum training samples
                logger.warning(
                    f"Insufficient training data for {symbol}: {len(X)} samples"
                )
                return {"status": "insufficient_data"}

            # Train each model
            model_scores = {}
            for model_name, model in self.models[symbol].items():
                try:
                    scaler = self.scalers[symbol][model_name]

                    # Scale features
                    X_scaled = scaler.fit_transform(X)

                    # Time series cross-validation
                    tscv = TimeSeriesSplit(n_splits=5)
                    cv_scores = cross_val_score(
                        model, X_scaled, y, cv=tscv, scoring="accuracy"
                    )

                    # Train on full dataset
                    model.fit(X_scaled, y)

                    # Calculate model weight based on performance
                    avg_score = np.mean(cv_scores)
                    self.model_weights[symbol][model_name] = max(0.1, avg_score)

                    model_scores[model_name] = {
                        "cv_mean": avg_score,
                        "cv_std": np.std(cv_scores),
                        "weight": self.model_weights[symbol][model_name],
                    }

                    logger.info(
                        f"Trained {model_name} for {symbol}: CV score = {avg_score:.3f}"
                    )

                except Exception as e:
                    logger.error(f"Error training {model_name} for {symbol}: {e}")
                    model_scores[model_name] = {"error": str(e)}

            # Save models
            await self._save_models(symbol)

            # Update training history
            self.last_retrain_time[symbol] = datetime.now()

            return {
                "status": "success",
                "symbol": symbol,
                "training_samples": len(X),
                "models_trained": len(model_scores),
                "model_scores": model_scores,
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error training models for {symbol}: {e}")
            return {"status": "error", "error": str(e)}

    async def _prepare_training_data(
        self, symbol: str, data: pd.DataFrame, target_column: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepares training data by generating features for each data point.

        Args:
            symbol (str): The trading symbol.
            data (pd.DataFrame): The input DataFrame with OHLCV and target data.
            target_column (str): The name of the target column.

        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing the feature matrix (X)
                                           and the target vector (y).
        """
        # This is a simplified example. A more efficient implementation would
        # use vectorized operations to generate features for the whole DataFrame at once.
        features_list = []
        targets = []

        for i in range(50, len(data)):  # Start with enough history for indicators
            data_slice = data.iloc[: i + 1]
            features = await self._generate_features(symbol, data_slice)

            if features is not None:
                features_list.append(features.flatten())
                targets.append(data[target_column].iloc[i])

        X = np.array(features_list)
        y = np.array(targets)

        return X, y

    async def _save_models(self, symbol: str):
        """
        Saves the trained models, scalers, and metadata for a symbol to disk.

        Args:
            symbol (str): The symbol for which models are being saved.
        """
        try:
            symbol_dir = self.model_dir / symbol
            symbol_dir.mkdir(exist_ok=True)

            # Save models
            for model_name, model in self.models[symbol].items():
                model_path = symbol_dir / f"{model_name}_model.joblib"
                joblib.dump(model, model_path)

            # Save scalers
            for scaler_name, scaler in self.scalers[symbol].items():
                scaler_path = symbol_dir / f"{scaler_name}_scaler.joblib"
                joblib.dump(scaler, scaler_path)

            # Save weights and metadata
            metadata = {
                "model_weights": self.model_weights[symbol],
                "last_retrain_time": self.last_retrain_time.get(symbol),
                "feature_importance": self.feature_importance.get(symbol, {}),
            }

            metadata_path = symbol_dir / "metadata.joblib"
            joblib.dump(metadata, metadata_path)

            logger.info(f"Saved models for {symbol} to {symbol_dir}")

        except Exception as e:
            logger.error(f"Error saving models for {symbol}: {e}")

    async def _load_models(self):
        """Loads existing models, scalers, and metadata from disk."""
        try:
            if not self.model_dir.exists():
                return

            for symbol_dir in self.model_dir.iterdir():
                if symbol_dir.is_dir():
                    symbol = symbol_dir.name
                    logger.info(f"Loading models for symbol: {symbol}")

                    # Load metadata
                    metadata_path = symbol_dir / "metadata.joblib"
                    if metadata_path.exists():
                        metadata = joblib.load(metadata_path)
                        self.model_weights[symbol] = metadata.get("model_weights", {})
                        self.last_retrain_time[symbol] = metadata.get(
                            "last_retrain_time"
                        )
                        self.feature_importance[symbol] = metadata.get(
                            "feature_importance", {}
                        )

                    # Load models and scalers
                    self.models[symbol] = {}
                    self.scalers[symbol] = {}

                    for model_file in symbol_dir.glob("*_model.joblib"):
                        model_name = model_file.stem.replace("_model", "")
                        try:
                            self.models[symbol][model_name] = joblib.load(model_file)
                        except Exception as e:
                            logger.error(
                                f"Error loading model {model_name} for {symbol}: {e}"
                            )

                    for scaler_file in symbol_dir.glob("*_scaler.joblib"):
                        scaler_name = scaler_file.stem.replace("_scaler", "")
                        try:
                            self.scalers[symbol][scaler_name] = joblib.load(scaler_file)
                        except Exception as e:
                            logger.error(
                                f"Error loading scaler {scaler_name} for {symbol}: {e}"
                            )

                    if self.models.get(symbol):
                        logger.info(
                            f"Loaded {len(self.models[symbol])} models for {symbol}"
                        )

        except Exception as e:
            logger.error(f"Error loading models from disk: {e}")

    async def should_retrain(self, symbol: str) -> bool:
        """
        Checks if the models for a given symbol should be retrained.

        Args:
            symbol (str): The symbol to check.

        Returns:
            bool: True if retraining is needed, False otherwise.
        """
        if symbol not in self.last_retrain_time:
            return True

        last_retrain = self.last_retrain_time.get(symbol)
        if last_retrain is None:
            return True

        retrain_interval_hours = self.config.get("retrain_interval_hours", 24)
        retrain_interval = timedelta(hours=retrain_interval_hours)
        return (datetime.now() - last_retrain) > retrain_interval

    async def get_model_summary(self, symbol: str) -> Dict[str, Any]:
        """
        Gets a summary of the models for a specific symbol.

        Args:
            symbol (str): The symbol to get the summary for.

        Returns:
            Dict[str, Any]: A dictionary containing model summary information.
        """
        if symbol not in self.models:
            return {"status": "no_models_for_symbol"}

        should_retrain_flag = await self.should_retrain(symbol)

        return {
            "symbol": symbol,
            "model_count": len(self.models.get(symbol, {})),
            "model_names": list(self.models.get(symbol, {}).keys()),
            "model_weights": self.model_weights.get(symbol, {}),
            "last_retrain_time": self.last_retrain_time.get(symbol),
            "feature_importance": self.feature_importance.get(symbol, {}),
            "should_retrain": should_retrain_flag,
        }
