import numpy as np
import optuna
import xgboost as xgb
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import LSTM, Conv1D, Dense, Dropout, Flatten, MaxPooling1D
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical


class HyperparameterOptimizer:
    """
    Handles hyperparameter tuning for the ensemble models using Optuna.
    """

    def __init__(self, features):
        self.features = features

    def _objective_xgb(self, trial):
        """Objective function for XGBoost optimization."""
        X_train, X_val, y_train, y_val = train_test_split(
            self.features.technical_indicators,
            self.features.labels,
            test_size=0.2,
            random_state=42,
            stratify=self.features.labels,
        )

        params = {
            "objective": "multi:softmax",
            "num_class": len(np.unique(y_train)),
            "eval_metric": "mlogloss",
            "booster": trial.suggest_categorical("booster", ["gbtree", "dart"]),
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        }

        model = xgb.XGBClassifier(**params)
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=30,
            verbose=False,
        )

        return model.best_score

    def optimize_xgboost(self, n_trials=30):
        """Optimizes XGBoost hyperparameters."""
        study = optuna.create_study(direction="minimize")
        study.optimize(self._objective_xgb, n_trials=n_trials)
        return study.best_params

    def _objective_lstm(self, trial):
        """Objective function for LSTM optimization."""
        y_categorical = to_categorical(self.features.labels, num_classes=3)
        X_train, X_val, y_train, y_val = train_test_split(
            self.features.price_sequences,
            y_categorical,
            test_size=0.2,
            random_state=42,
            stratify=self.features.labels,
        )

        params = {
            "lstm_units_1": trial.suggest_int("lstm_units_1", 32, 128),
            "dropout_1": trial.suggest_float("dropout_1", 0.1, 0.5),
            "lstm_units_2": trial.suggest_int("lstm_units_2", 32, 128),
            "dropout_2": trial.suggest_float("dropout_2", 0.1, 0.5),
            "dense_units": trial.suggest_int("dense_units", 16, 64),
            "learning_rate": trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
        }

        model = Sequential(
            [
                LSTM(
                    params["lstm_units_1"],
                    return_sequences=True,
                    input_shape=X_train.shape[1:],
                ),
                Dropout(params["dropout_1"]),
                LSTM(params["lstm_units_2"]),
                Dropout(params["dropout_2"]),
                Dense(params["dense_units"], activation="relu"),
                Dense(3, activation="softmax"),
            ]
        )

        model.compile(
            optimizer=Adam(learning_rate=params["learning_rate"]),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=20,
            batch_size=32,
            verbose=0,
        )

        return np.min(history.history["val_loss"])

    def optimize_lstm(self, n_trials=20):
        """Optimizes LSTM hyperparameters."""
        study = optuna.create_study(direction="minimize")
        study.optimize(self._objective_lstm, n_trials=n_trials)
        return study.best_params

    def _objective_cnn(self, trial):
        """Objective function for CNN optimization."""
        y_categorical = to_categorical(self.features.labels, num_classes=3)
        X_train, X_val, y_train, y_val = train_test_split(
            self.features.chart_patterns,
            y_categorical,
            test_size=0.2,
            random_state=42,
            stratify=self.features.labels,
        )

        params = {
            "filters_1": trial.suggest_int("filters_1", 32, 128),
            "kernel_size_1": trial.suggest_categorical("kernel_size_1", [3, 5]),
            "pool_size_1": 2,
            "filters_2": trial.suggest_int("filters_2", 16, 64),
            "kernel_size_2": trial.suggest_categorical("kernel_size_2", [3, 5]),
            "pool_size_2": 2,
            "dense_units": trial.suggest_int("dense_units", 32, 128),
            "dropout": trial.suggest_float("dropout", 0.1, 0.5),
            "learning_rate": trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
        }

        model = Sequential(
            [
                Conv1D(
                    filters=params["filters_1"],
                    kernel_size=params["kernel_size_1"],
                    activation="relu",
                    input_shape=X_train.shape[1:],
                ),
                MaxPooling1D(pool_size=params["pool_size_1"]),
                Conv1D(
                    filters=params["filters_2"],
                    kernel_size=params["kernel_size_2"],
                    activation="relu",
                ),
                MaxPooling1D(pool_size=params["pool_size_2"]),
                Flatten(),
                Dense(params["dense_units"], activation="relu"),
                Dropout(params["dropout"]),
                Dense(3, activation="softmax"),
            ]
        )

        model.compile(
            optimizer=Adam(learning_rate=params["learning_rate"]),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        history = model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=20,
            batch_size=32,
            verbose=0,
        )

        return np.min(history.history["val_loss"])

    def optimize_cnn(self, n_trials=20):
        """Optimizes CNN hyperparameters."""
        study = optuna.create_study(direction="minimize")
        study.optimize(self._objective_cnn, n_trials=n_trials)
        return study.best_params
