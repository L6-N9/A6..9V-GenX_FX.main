import os
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def train_model(df):
    """
    Trains a machine learning model to predict price movements.
    """
    # Split the data into features (X) and target (y)
    X = df.drop(columns=["timestamp", "target"])
    y = df["target"]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train a Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    print(f"Accuracy: {accuracy:.2f}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")

    return model


if __name__ == "__main__":
    # Load the features
    data_dir = "data"
    features_file_path = os.path.join(data_dir, "features.csv")
    df = pd.read_csv(features_file_path)

    # Train the model
    model = train_model(df)

    # Save the model
    models_dir = "ai_models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    model_file_path = os.path.join(models_dir, "market_predictor.joblib")
    joblib.dump(model, model_file_path)
    print(f"Model saved to {model_file_path}")
