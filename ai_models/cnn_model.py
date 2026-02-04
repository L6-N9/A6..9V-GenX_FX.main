import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import Conv1D, Dense, Dropout, Flatten, MaxPooling1D
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical


class CNNModel:
    """
    Encapsulates the CNN model logic.
    """

    def __init__(self, sequence_length=60, n_channels=4):
        self.sequence_length = sequence_length
        self.n_channels = n_channels
        self.model = None

    def build_model(self, params=None):
        """Builds the CNN model architecture."""
        if params is None:
            params = {
                "filters_1": 64,
                "kernel_size_1": 3,
                "pool_size_1": 2,
                "filters_2": 32,
                "kernel_size_2": 3,
                "pool_size_2": 2,
                "dense_units": 50,
                "dropout": 0.3,
                "learning_rate": 0.001,
            }

        model = Sequential(
            [
                Conv1D(
                    filters=params["filters_1"],
                    kernel_size=params["kernel_size_1"],
                    activation="relu",
                    input_shape=(self.sequence_length, self.n_channels),
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

        optimizer = Adam(learning_rate=params["learning_rate"])
        model.compile(
            optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
        )
        return model

    def train(self, X, y, params=None):
        """Trains the CNN model."""
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
