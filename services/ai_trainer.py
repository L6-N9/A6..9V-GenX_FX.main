"""
Advanced AI Training Service for GenX Trading Platform
Provides continuous learning and model improvement capabilities
"""

import asyncio
import json
import logging
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiohttp
import joblib
import numpy as np
import pandas as pd
import redis
import schedule
import websockets
from pymongo import MongoClient
from sqlalchemy import create_engine, text

from ai_models.ensemble_model import EnsembleModel
from ai_models.market_predictor import MarketPredictor
from core.indicators import TechnicalIndicators
from core.patterns import PatternDetector
from utils.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TrainingMetrics:
    """Training metrics data class"""

    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time: float
    data_points: int
    features_count: int
    timestamp: datetime


class AITrainingService:
    """
    Advanced AI Training Service with continuous learning capabilities
    """

    def __init__(self, config_path: str = "config/training_config.json"):
        self.config = load_config(config_path)
        self.is_running = False
        self.training_lock = asyncio.Lock()

        # Initialize connections
        self.db_engine = create_engine(self.config["database_url"])
        self.mongo_client = MongoClient(self.config["mongodb_url"])
        self.redis_client = redis.Redis.from_url(self.config["redis_url"])

        # Initialize models
        self.ensemble_model = EnsembleModel()
        self.market_predictor = MarketPredictor()
        self.technical_indicators = TechnicalIndicators()
        self.pattern_detector = PatternDetector()

        # Training parameters
        self.symbols = self.config.get("symbols", ["BTCUSDT", "ETHUSDT", "ADAUSDT"])
        self.timeframes = self.config.get(
            "timeframes", ["1m", "5m", "15m", "1h", "4h", "1d"]
        )
        self.retrain_interval = self.config.get("retrain_interval", 3600)  # 1 hour
        self.min_training_samples = self.config.get("min_training_samples", 1000)

        # Performance tracking
        self.training_history = []
        self.model_performance = {}

        logger.info("AI Training Service initialized")

    async def start_training_service(self):
        """Start the continuous training service"""
        self.is_running = True
        logger.info("Starting AI Training Service...")

        # Start background tasks
        tasks = [
            asyncio.create_task(self.continuous_training_loop()),
            asyncio.create_task(self.performance_monitoring_loop()),
            asyncio.create_task(self.data_collection_loop()),
            asyncio.create_task(self.model_validation_loop()),
        ]

        await asyncio.gather(*tasks)

    async def continuous_training_loop(self):
        """Main continuous training loop"""
        while self.is_running:
            try:
                async with self.training_lock:
                    logger.info("Starting training cycle...")

                    # Collect training data
                    training_data = await self.collect_training_data()

                    if len(training_data) >= self.min_training_samples:
                        # Train ensemble model
                        await self.train_ensemble_model(training_data)

                        # Train individual models
                        await self.train_individual_models(training_data)

                        # Validate models
                        await self.validate_models()

                        # Update model weights based on performance
                        await self.update_model_weights()

                        # Save models
                        await self.save_trained_models()

                        logger.info("Training cycle completed successfully")
                    else:
                        logger.warning(
                            f"Insufficient training data: {len(training_data)} < {self.min_training_samples}"
                        )

                # Wait for next training cycle
                await asyncio.sleep(self.retrain_interval)

            except Exception as e:
                logger.error(f"Error in training loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying

    async def collect_training_data(self) -> pd.DataFrame:
        """Collect and prepare training data from multiple sources"""
        logger.info("Collecting training data...")

        all_data = []

        for symbol in self.symbols:
            try:
                # Get historical market data
                market_data = await self.get_market_data(symbol)

                if market_data is not None and len(market_data) > 0:
                    # Add technical indicators
                    enhanced_data = self.technical_indicators.add_all_indicators(
                        market_data
                    )

                    # Add pattern detection
                    patterns = self.pattern_detector.detect_patterns(enhanced_data)
                    for pattern_name, pattern_values in patterns.items():
                        enhanced_data[f"pattern_{pattern_name}"] = pattern_values

                    # Add market sentiment data
                    sentiment_data = await self.get_sentiment_data(symbol)
                    if sentiment_data is not None:
                        enhanced_data = enhanced_data.merge(
                            sentiment_data, on="timestamp", how="left"
                        )

                    # Add fundamental data
                    fundamental_data = await self.get_fundamental_data(symbol)
                    if fundamental_data is not None:
                        enhanced_data = enhanced_data.merge(
                            fundamental_data, on="timestamp", how="left"
                        )

                    # Create target variable
                    enhanced_data["target"] = self.create_target_variable(enhanced_data)

                    # Add symbol identifier
                    enhanced_data["symbol"] = symbol

                    all_data.append(enhanced_data)

            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {str(e)}")

        # Combine all data
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data = combined_data.dropna()

            logger.info(f"Collected {len(combined_data)} training samples")
            return combined_data
        else:
            logger.warning("No training data collected")
            return pd.DataFrame()

    async def get_market_data(
        self, symbol: str, limit: int = 5000
    ) -> Optional[pd.DataFrame]:
        """Get market data from exchange API"""
        try:
            url = f"https://api.bybit.com/v5/market/kline"
            params = {
                "category": "spot",
                "symbol": symbol,
                "interval": "1",
                "limit": limit,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if "result" in data and "list" in data["result"]:
                            df = pd.DataFrame(data["result"]["list"])
                            df.columns = [
                                "timestamp",
                                "open",
                                "high",
                                "low",
                                "close",
                                "volume",
                                "turnover",
                            ]

                            # Convert to appropriate types
                            df["timestamp"] = pd.to_datetime(
                                df["timestamp"].astype(int), unit="ms"
                            )
                            for col in [
                                "open",
                                "high",
                                "low",
                                "close",
                                "volume",
                                "turnover",
                            ]:
                                df[col] = df[col].astype(float)

                            return df.sort_values("timestamp")

        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {str(e)}")

        return None

    async def get_sentiment_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get market sentiment data"""
        try:
            # This would integrate with sentiment analysis APIs
            # For now, we'll create mock sentiment data

            # Get recent news sentiment
            sentiment_score = await self.analyze_news_sentiment(symbol)

            # Get social media sentiment
            social_sentiment = await self.analyze_social_sentiment(symbol)

            # Combine sentiments
            combined_sentiment = (sentiment_score + social_sentiment) / 2

            return pd.DataFrame(
                {
                    "timestamp": [datetime.now()],
                    "sentiment_score": [combined_sentiment],
                    "news_sentiment": [sentiment_score],
                    "social_sentiment": [social_sentiment],
                }
            )

        except Exception as e:
            logger.error(f"Error getting sentiment data for {symbol}: {str(e)}")

        return None

    async def analyze_news_sentiment(self, symbol: str) -> float:
        """Analyze news sentiment for a symbol"""
        try:
            # This would integrate with news APIs and sentiment analysis
            # For now, return a random value between -1 and 1
            import random

            return random.uniform(-1, 1)
        except Exception:
            return 0.0

    async def analyze_social_sentiment(self, symbol: str) -> float:
        """Analyze social media sentiment for a symbol"""
        try:
            # This would integrate with Twitter, Reddit APIs
            # For now, return a random value between -1 and 1
            import random

            return random.uniform(-1, 1)
        except Exception:
            return 0.0

    async def get_fundamental_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get fundamental analysis data"""
        try:
            # This would integrate with financial data APIs
            # For now, create mock fundamental data

            return pd.DataFrame(
                {
                    "timestamp": [datetime.now()],
                    "market_cap": [1000000000],  # Mock market cap
                    "volume_24h": [50000000],  # Mock 24h volume
                    "dominance": [0.5],  # Mock market dominance
                    "fear_greed_index": [50],  # Mock fear & greed index
                }
            )

        except Exception as e:
            logger.error(f"Error getting fundamental data for {symbol}: {str(e)}")

        return None

    def create_target_variable(self, data: pd.DataFrame) -> pd.Series:
        """Create target variable for prediction"""
        # Create binary target: 1 if price goes up in next period, 0 otherwise
        future_return = data["close"].shift(-1) / data["close"] - 1

        # Define threshold for significant moves
        threshold = 0.01  # 1% change

        target = (future_return > threshold).astype(int)
        return target

    async def train_ensemble_model(self, training_data: pd.DataFrame):
        """Train the ensemble model"""
        logger.info("Training ensemble model...")

        try:
            # Prepare features and target
            feature_columns = [
                col
                for col in training_data.columns
                if col not in ["target", "symbol", "timestamp"]
            ]

            X = training_data[feature_columns]
            y = training_data["target"]

            # Train ensemble model
            start_time = time.time()
            training_results = self.ensemble_model.train(X, y)
            training_time = time.time() - start_time

            # Store training metrics
            metrics = TrainingMetrics(
                model_name="ensemble",
                accuracy=training_results["ensemble_accuracy"],
                precision=0.0,  # Would be calculated from detailed metrics
                recall=0.0,  # Would be calculated from detailed metrics
                f1_score=0.0,  # Would be calculated from detailed metrics
                training_time=training_time,
                data_points=len(X),
                features_count=len(feature_columns),
                timestamp=datetime.now(),
            )

            await self.store_training_metrics(metrics)

            logger.info(
                f"Ensemble model trained successfully. Accuracy: {training_results['ensemble_accuracy']:.4f}"
            )

        except Exception as e:
            logger.error(f"Error training ensemble model: {str(e)}")

    async def train_individual_models(self, training_data: pd.DataFrame):
        """Train individual models for comparison"""
        logger.info("Training individual models...")

        # This would train individual models like Random Forest, XGBoost, etc.
        # For now, we'll just log the intention
        logger.info("Individual model training completed")

    async def validate_models(self):
        """Validate trained models"""
        logger.info("Validating models...")

        # Get validation data
        validation_data = await self.get_validation_data()

        if validation_data is not None and len(validation_data) > 0:
            # Validate ensemble model
            ensemble_score = await self.validate_ensemble_model(validation_data)

            # Store validation results
            await self.store_validation_results("ensemble", ensemble_score)

            logger.info(
                f"Model validation completed. Ensemble score: {ensemble_score:.4f}"
            )
        else:
            logger.warning("No validation data available")

    async def get_validation_data(self) -> Optional[pd.DataFrame]:
        """Get fresh data for model validation"""
        # This would get the most recent data that wasn't used for training
        # For now, return None
        return None

    async def validate_ensemble_model(self, validation_data: pd.DataFrame) -> float:
        """Validate the ensemble model"""
        # This would run the model on validation data and calculate metrics
        # For now, return a mock score
        return 0.85

    async def update_model_weights(self):
        """Update model weights based on recent performance"""
        logger.info("Updating model weights...")

        # Get recent performance data
        recent_performance = await self.get_recent_performance()

        if recent_performance:
            # Update ensemble model weights
            self.ensemble_model.update_model_weights(recent_performance)

            logger.info("Model weights updated successfully")

    async def get_recent_performance(self) -> Optional[Dict[str, float]]:
        """Get recent model performance data"""
        try:
            # Query recent performance from database
            query = """
                SELECT model_name, AVG(accuracy) as avg_accuracy
                FROM model_performance
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                GROUP BY model_name
            """

            with self.db_engine.connect() as conn:
                result = conn.execute(text(query))
                performance_data = {row.model_name: row.avg_accuracy for row in result}

                return performance_data if performance_data else None

        except Exception as e:
            logger.error(f"Error getting recent performance: {str(e)}")
            return None

    async def save_trained_models(self):
        """Save trained models to disk"""
        logger.info("Saving trained models...")

        try:
            # Save ensemble model
            ensemble_path = Path("ai_models/ensemble_model.joblib")
            self.ensemble_model.save_model(str(ensemble_path))

            # Save individual models
            # This would save other trained models

            logger.info("Models saved successfully")

        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")

    async def store_training_metrics(self, metrics: TrainingMetrics):
        """Store training metrics in database"""
        try:
            query = """
                INSERT INTO model_performance 
                (model_name, accuracy, precision_score, recall_score, f1_score, timestamp)
                VALUES (:model_name, :accuracy, :precision, :recall, :f1_score, :timestamp)
            """

            with self.db_engine.connect() as conn:
                conn.execute(
                    text(query),
                    {
                        "model_name": metrics.model_name,
                        "accuracy": metrics.accuracy,
                        "precision": metrics.precision,
                        "recall": metrics.recall,
                        "f1_score": metrics.f1_score,
                        "timestamp": metrics.timestamp,
                    },
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error storing training metrics: {str(e)}")

    async def store_validation_results(self, model_name: str, score: float):
        """Store validation results"""
        try:
            # Store in MongoDB for detailed analysis
            collection = self.mongo_client.genx_trading.validation_results

            validation_doc = {
                "model_name": model_name,
                "validation_score": score,
                "timestamp": datetime.now(),
                "validation_type": "holdout",
            }

            collection.insert_one(validation_doc)

        except Exception as e:
            logger.error(f"Error storing validation results: {str(e)}")

    async def performance_monitoring_loop(self):
        """Monitor model performance in real-time"""
        while self.is_running:
            try:
                # Monitor prediction accuracy
                await self.monitor_prediction_accuracy()

                # Monitor system performance
                await self.monitor_system_performance()

                # Alert on performance degradation
                await self.check_performance_alerts()

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in performance monitoring: {str(e)}")
                await asyncio.sleep(60)

    async def monitor_prediction_accuracy(self):
        """Monitor real-time prediction accuracy"""
        # This would track how well recent predictions performed
        pass

    async def monitor_system_performance(self):
        """Monitor system resource usage"""
        # This would monitor CPU, memory, etc.
        pass

    async def check_performance_alerts(self):
        """Check for performance degradation and send alerts"""
        # This would send alerts when performance drops below threshold
        pass

    async def data_collection_loop(self):
        """Continuously collect data for training"""
        while self.is_running:
            try:
                # Collect real-time market data
                await self.collect_realtime_data()

                # Collect prediction feedback
                await self.collect_prediction_feedback()

                await asyncio.sleep(60)  # Collect every minute

            except Exception as e:
                logger.error(f"Error in data collection loop: {str(e)}")
                await asyncio.sleep(60)

    async def collect_realtime_data(self):
        """Collect real-time market data"""
        # This would collect streaming market data
        pass

    async def collect_prediction_feedback(self):
        """Collect feedback on predictions for continuous learning"""
        # This would collect actual outcomes for recent predictions
        pass

    async def model_validation_loop(self):
        """Continuously validate models"""
        while self.is_running:
            try:
                # Validate model performance
                await self.validate_live_performance()

                # Check for model drift
                await self.check_model_drift()

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                logger.error(f"Error in model validation loop: {str(e)}")
                await asyncio.sleep(300)

    async def validate_live_performance(self):
        """Validate model performance on live data"""
        # This would validate models against live market data
        pass

    async def check_model_drift(self):
        """Check for model drift and trigger retraining if necessary"""
        # This would detect when models need retraining due to changing market conditions
        pass

    async def shutdown(self):
        """Shutdown the training service"""
        logger.info("Shutting down AI Training Service...")
        self.is_running = False

        # Close connections
        self.db_engine.dispose()
        self.mongo_client.close()
        self.redis_client.close()

        logger.info("AI Training Service shut down successfully")


async def main():
    """Main function to run the AI Training Service"""
    training_service = AITrainingService()

    try:
        await training_service.start_training_service()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    finally:
        await training_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
