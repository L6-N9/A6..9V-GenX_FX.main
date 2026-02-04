import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from .cnn_model import CNNModel

# These modules will be created in subsequent steps
from .feature_engineer import FeatureEngineer
from .hyperparameter_optimizer import HyperparameterOptimizer
from .lstm_model import LSTMModel
from .xgboost_model import XGBoostModel

logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    Orchestrates the training and prediction of an ensemble of models.
    This new version is designed for modularity and clarity.
    """

    def __init__(
        self, sequence_length: int = 60, model_dir: str = "ai_models/saved_models"
    ):
        self.sequence_length = sequence_length
        self.model_dir = model_dir
        self.feature_engineer = FeatureEngineer()
        self.xgb_model = XGBoostModel()
        self.lstm_model = LSTMModel(sequence_length)
        self.cnn_model = CNNModel(sequence_length)
        self.meta_learner = LogisticRegression(random_state=42)
        self.is_trained = False
        self.class_names = ["short", "neutral", "long"]

    def train(self, df: pd.DataFrame, optimize_hyperparameters: bool = False):
        """Trains the entire ensemble model pipeline."""
        logger.info("Starting ensemble model training...")

        features = self.feature_engineer.engineer_features(df, self.sequence_length)

        xgb_params, lstm_params, cnn_params = {}, {}, {}

        if optimize_hyperparameters:
            logger.info("Starting hyperparameter optimization...")
            optimizer = HyperparameterOptimizer(features)
            xgb_params = optimizer.optimize_xgboost()
            lstm_params = optimizer.optimize_lstm()
            cnn_params = optimizer.optimize_cnn()
            logger.info("Hyperparameter optimization complete.")

        self.xgb_model.train(features.technical_indicators, features.labels, xgb_params)
        self.lstm_model.train(features.price_sequences, features.labels, lstm_params)
        self.cnn_model.train(features.chart_patterns, features.labels, cnn_params)

        meta_features = self._create_meta_features(features)
        self.meta_learner.fit(meta_features, features.labels)

        self.is_trained = True
        self.save_models()
        logger.info("Ensemble model training completed successfully.")

    def _create_meta_features(self, features) -> np.ndarray:
        """Creates meta-features from base model predictions."""
        xgb_probas = self.xgb_model.predict(
            features.technical_indicators, return_probas=True
        )
        lstm_probas = self.lstm_model.predict(
            features.price_sequences, return_probas=True
        )
        cnn_probas = self.cnn_model.predict(features.chart_patterns, return_probas=True)
        return np.concatenate([xgb_probas, lstm_probas, cnn_probas], axis=1)

    def predict(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Makes a prediction using the trained ensemble model."""
        if not self.is_trained:
            logger.warning("Models are not trained. Loading from disk.")
            self.load_models()
            if not self.is_trained:
                raise ValueError("Models are not trained and could not be loaded.")

        features = self.feature_engineer.engineer_features_for_prediction(
            df, self.sequence_length
        )

        meta_feature = self._create_meta_features_for_prediction(features)

        prediction_idx = self.meta_learner.predict(meta_feature)[0]
        probabilities = self.meta_learner.predict_proba(meta_feature)[0]

        return {
            "prediction": self.class_names[prediction_idx],
            "confidence": np.max(probabilities),
            "timestamp": datetime.utcnow(),
            "probabilities": dict(zip(self.class_names, probabilities)),
        }

    def _create_meta_features_for_prediction(self, features) -> np.ndarray:
        """Creates meta-features for a single prediction."""
        xgb_proba = self.xgb_model.predict(
            features.technical_indicators, return_probas=True
        )
        lstm_proba = self.lstm_model.predict(
            features.price_sequences, return_probas=True
        )
        cnn_proba = self.cnn_model.predict(features.chart_patterns, return_probas=True)
        return np.concatenate([xgb_proba, lstm_proba, cnn_proba], axis=1)

    def save_models(self):
        """Saves all models to the specified directory."""
        os.makedirs(self.model_dir, exist_ok=True)
        self.xgb_model.save(os.path.join(self.model_dir, "xgb.pkl"))
        self.lstm_model.save(os.path.join(self.model_dir, "lstm.h5"))
        self.cnn_model.save(os.path.join(self.model_dir, "cnn.h5"))
        joblib.dump(self.meta_learner, os.path.join(self.model_dir, "meta_learner.pkl"))
        self.feature_engineer.save_scalers(self.model_dir)
        logger.info(f"All models saved to {self.model_dir}")

    def load_models(self):
        """Loads all models from the specified directory."""
        try:
            self.xgb_model.load(os.path.join(self.model_dir, "xgb.pkl"))
            self.lstm_model.load(os.path.join(self.model_dir, "lstm.h5"))
            self.cnn_model.load(os.path.join(self.model_dir, "cnn.h5"))
            self.meta_learner = joblib.load(
                os.path.join(self.model_dir, "meta_learner.pkl")
            )
            self.feature_engineer.load_scalers(self.model_dir)
            self.is_trained = True
            logger.info(f"All models loaded from {self.model_dir}")
        except FileNotFoundError:
            logger.error(
                f"Could not load models from {self.model_dir}. Please train the models first."
            )
