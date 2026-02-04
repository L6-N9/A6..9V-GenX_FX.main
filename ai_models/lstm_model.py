import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical


class LSTMModel:
    """
    Encapsulates the LSTM model logic.
    """

    def __init__(self, sequence_length=60, n_features=5):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None

    def build_model(self, params=None):
        """Builds the LSTM model architecture."""
        if params is None:
            params = {
                "lstm_units_1": 50,
                "dropout_1": 0.2,
                "lstm_units_2": 50,
                "dropout_2": 0.2,
                "dense_units": 25,
                "learning_rate": 0.001,
            }

        model = Sequential(
            [
                LSTM(
                    params["lstm_units_1"],
                    return_sequences=True,
                    input_shape=(self.sequence_length, self.n_features),
                ),
                Dropout(params["dropout_1"]),
                LSTM(params["lstm_units_2"]),
                Dropout(params["dropout_2"]),
                Dense(params["dense_units"], activation="relu"),
                Dense(3, activation="softmax"),
            ]
        )

        optimizer = Adam(learning_rate=params["learning_rate"])
        model.compile(
            optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
        )
        return model

    def train(self, X, y, params=None):
        """Trains the LSTM model."""
        y_categorical = to_categorical(y, num_classes=3)
        X_train, X_val, y_train, y_val = train_test_split(
            X, y_categorical, test_size=0.2, random_state=42, stratify=y
        )

        self.model = self.build_model(params)

        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ReduceLROnPlateau(patience=5, factor=0.5),
        ]

        self.model.fit(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=100,
            batch_size=32,
            callbacks=callbacks,
            verbose=0,
        )

    def predict(self, X, return_probas=False):
        """Makes predictions with the trained model."""
        if not return_probas:
            return np.argmax(self.model.predict(X), axis=1)
        return self.model.predict(X)

    def save(self, path):
        """Saves the model to disk."""
        self.model.save(path)

    def load(self, path):
        """Loads the model from disk."""
        self.model = load_model(path)
