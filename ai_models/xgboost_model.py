import joblib
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split


class XGBoostModel:
    """
    Encapsulates the XGBoost model logic.
    """

    def __init__(self):
        self.model = None

    def train(self, X, y, params=None):
        """Trains the XGBoost model."""
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        if params is None:
            params = {
                "objective": "multi:softmax",
                "num_class": len(np.unique(y)),
                "eval_metric": "mlogloss",
                "n_estimators": 200,
            }

        self.model = xgb.XGBClassifier(**params)
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=50,
            verbose=False,
        )

    def predict(self, X, return_probas=False):
        """Makes predictions with the trained model."""
        if return_probas:
            return self.model.predict_proba(X)
        return self.model.predict(X)

    def save(self, path):
        """Saves the model to disk."""
        joblib.dump(self.model, path)

    def load(self, path):
        """Loads the model from disk."""
        self.model = joblib.load(path)
