"""
Model Validation Utilities for GenX FX Trading System
Provides validation and performance metrics for ML models
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import TimeSeriesSplit, cross_val_score


class ModelValidator:
    """
    Model validation and performance metrics for trading models
    """

    def __init__(self):
        self.validation_results = {}
        self.performance_history = []

    def validate_classification_model(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
    ) -> Dict[str, float]:
        """
        Validate classification model performance

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities (optional)

        Returns:
            Dictionary with validation metrics
        """
        try:
            metrics = {
                "accuracy": accuracy_score(y_true, y_pred),
                "precision": precision_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
                "recall": recall_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
                "f1_score": f1_score(
                    y_true, y_pred, average="weighted", zero_division=0
                ),
            }

            # Add ROC AUC if probabilities provided
            if y_proba is not None:
                try:
                    from sklearn.metrics import roc_auc_score

                    if len(np.unique(y_true)) == 2:  # Binary classification
                        metrics["roc_auc"] = roc_auc_score(
                            y_true, y_proba[:, 1] if y_proba.ndim > 1 else y_proba
                        )
                    else:  # Multi-class
                        metrics["roc_auc"] = roc_auc_score(
                            y_true, y_proba, multi_class="ovr", average="weighted"
                        )
                except Exception as e:
                    print(f"Warning: Could not calculate ROC AUC: {e}")
                    metrics["roc_auc"] = 0.0

            return metrics

        except Exception as e:
            print(f"Warning: Error validating classification model: {e}")
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "roc_auc": 0.0,
            }

    def validate_regression_model(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Validate regression model performance

        Args:
            y_true: True values
            y_pred: Predicted values

        Returns:
            Dictionary with validation metrics
        """
        try:
            metrics = {
                "mse": mean_squared_error(y_true, y_pred),
                "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
                "mae": mean_absolute_error(y_true, y_pred),
                "r2": r2_score(y_true, y_pred),
                "mape": np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8)))
                * 100,  # Add small epsilon
            }

            # Add directional accuracy for trading
            direction_true = np.sign(np.diff(y_true))
            direction_pred = np.sign(np.diff(y_pred))
            if len(direction_true) > 0:
                metrics["directional_accuracy"] = np.mean(
                    direction_true == direction_pred
                )
            else:
                metrics["directional_accuracy"] = 0.0

            return metrics

        except Exception as e:
            print(f"Warning: Error validating regression model: {e}")
            return {
                "mse": float("inf"),
                "rmse": float("inf"),
                "mae": float("inf"),
                "r2": -float("inf"),
                "mape": float("inf"),
                "directional_accuracy": 0.0,
            }

    def cross_validate_timeseries(
        self,
        model,
        X: np.ndarray,
        y: np.ndarray,
        cv_folds: int = 5,
        scoring: str = "accuracy",
    ) -> Dict[str, float]:
        """
        Perform time series cross-validation

        Args:
            model: Model to validate
            X: Feature matrix
            y: Target vector
            cv_folds: Number of CV folds
            scoring: Scoring metric

        Returns:
            Dictionary with CV results
        """
        try:
            tscv = TimeSeriesSplit(n_splits=cv_folds)

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                scores = cross_val_score(model, X, y, cv=tscv, scoring=scoring)

            return {
                "cv_mean": np.mean(scores),
                "cv_std": np.std(scores),
                "cv_scores": scores.tolist(),
                "cv_folds": cv_folds,
            }

        except Exception as e:
            print(f"Warning: Error in cross-validation: {e}")
            return {
                "cv_mean": 0.0,
                "cv_std": 0.0,
                "cv_scores": [],
                "cv_folds": cv_folds,
            }

    def validate_trading_performance(
        self, returns: np.ndarray, benchmark_returns: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Validate trading performance metrics

        Args:
            returns: Trading returns
            benchmark_returns: Benchmark returns (optional)

        Returns:
            Dictionary with trading metrics
        """
        try:
            if len(returns) == 0:
                return self._empty_trading_metrics()

            metrics = {
                "total_return": np.sum(returns),
                "mean_return": np.mean(returns),
                "volatility": np.std(returns),
                "sharpe_ratio": np.mean(returns)
                / (np.std(returns) + 1e-8)
                * np.sqrt(252),  # Annualized
                "max_drawdown": self._calculate_max_drawdown(returns),
                "win_rate": np.mean(returns > 0),
                "profit_factor": self._calculate_profit_factor(returns),
                "calmar_ratio": np.sum(returns)
                / (abs(self._calculate_max_drawdown(returns)) + 1e-8),
            }

            # Add benchmark comparison if provided
            if benchmark_returns is not None and len(benchmark_returns) == len(returns):
                metrics["alpha"] = np.mean(returns) - np.mean(benchmark_returns)
                metrics["beta"] = np.cov(returns, benchmark_returns)[0, 1] / (
                    np.var(benchmark_returns) + 1e-8
                )
                metrics["information_ratio"] = metrics["alpha"] / (
                    np.std(returns - benchmark_returns) + 1e-8
                )

            return metrics

        except Exception as e:
            print(f"Warning: Error validating trading performance: {e}")
            return self._empty_trading_metrics()

    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown from returns"""
        try:
            cumulative = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            return np.min(drawdown)
        except Exception:
            return 0.0

    def _calculate_profit_factor(self, returns: np.ndarray) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        try:
            profits = returns[returns > 0]
            losses = returns[returns < 0]

            gross_profit = np.sum(profits) if len(profits) > 0 else 0
            gross_loss = abs(np.sum(losses)) if len(losses) > 0 else 1e-8

            return gross_profit / gross_loss
        except Exception:
            return 1.0

    def _empty_trading_metrics(self) -> Dict[str, float]:
        """Return empty trading metrics"""
        return {
            "total_return": 0.0,
            "mean_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "profit_factor": 1.0,
            "calmar_ratio": 0.0,
        }

    def generate_validation_report(
        self, model_name: str, validation_results: Dict[str, Any]
    ) -> str:
        """
        Generate a validation report

        Args:
            model_name: Name of the model
            validation_results: Validation results dictionary

        Returns:
            Formatted validation report
        """
        try:
            report = f"\n=== Model Validation Report: {model_name} ===\n"

            for category, metrics in validation_results.items():
                report += f"\n{category.upper()}:\n"
                for metric, value in metrics.items():
                    if isinstance(value, float):
                        report += f"  {metric}: {value:.4f}\n"
                    else:
                        report += f"  {metric}: {value}\n"

            report += "\n" + "=" * 50 + "\n"
            return report

        except Exception as e:
            return f"Error generating validation report: {e}"

    def is_model_stable(
        self,
        validation_results: Dict[str, Any],
        min_accuracy: float = 0.6,
        min_f1: float = 0.5,
    ) -> bool:
        """
        Check if model performance is stable and acceptable

        Args:
            validation_results: Validation results
            min_accuracy: Minimum acceptable accuracy
            min_f1: Minimum acceptable F1 score

        Returns:
            True if model is stable
        """
        try:
            # Check classification metrics if available
            if "classification" in validation_results:
                clf_metrics = validation_results["classification"]
                if clf_metrics.get("accuracy", 0) < min_accuracy:
                    return False
                if clf_metrics.get("f1_score", 0) < min_f1:
                    return False

            # Check cross-validation stability
            if "cross_validation" in validation_results:
                cv_metrics = validation_results["cross_validation"]
                cv_std = cv_metrics.get("cv_std", float("inf"))
                cv_mean = cv_metrics.get("cv_mean", 0)

                # High CV standard deviation indicates instability
                if cv_std / (cv_mean + 1e-8) > 0.5:  # CV > 50%
                    return False

            # Check trading performance
            if "trading" in validation_results:
                trading_metrics = validation_results["trading"]
                if trading_metrics.get("sharpe_ratio", 0) < 0.5:
                    return False
                if (
                    trading_metrics.get("max_drawdown", 0) < -0.3
                ):  # More than 30% drawdown
                    return False

            return True

        except Exception as e:
            print(f"Warning: Error checking model stability: {e}")
            return False

    def update_performance_history(
        self, model_name: str, metrics: Dict[str, Any]
    ) -> None:
        """
        Update performance history for tracking

        Args:
            model_name: Name of the model
            metrics: Performance metrics
        """
        try:
            self.performance_history.append(
                {
                    "timestamp": pd.Timestamp.now(),
                    "model_name": model_name,
                    "metrics": metrics,
                }
            )

            # Keep only recent history (last 100 entries)
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]

        except Exception as e:
            print(f"Warning: Error updating performance history: {e}")

    def get_performance_trend(self, model_name: str, metric_name: str) -> List[float]:
        """
        Get performance trend for a specific metric

        Args:
            model_name: Name of the model
            metric_name: Name of the metric

        Returns:
            List of metric values over time
        """
        try:
            trend = []
            for entry in self.performance_history:
                if entry["model_name"] == model_name:
                    # Navigate nested dictionary structure
                    value = entry["metrics"]
                    for key in metric_name.split("."):
                        if isinstance(value, dict) and key in value:
                            value = value[key]
                        else:
                            value = None
                            break

                    if value is not None and isinstance(value, (int, float)):
                        trend.append(float(value))

            return trend

        except Exception as e:
            print(f"Warning: Error getting performance trend: {e}")
            return []
