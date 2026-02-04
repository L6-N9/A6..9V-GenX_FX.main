import os
import sys

import numpy as np
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.indicators.macd import calculate_macd
from core.indicators.moving_average import calculate_sma
from core.indicators.rsi import calculate_rsi


def create_features(df):
    """
    Creates features for the machine learning model.
    """
    # --- Performance Optimization: Calculate all indicators before assigning ---
    # To avoid chained indexing and repeated data slicing, we calculate all
    # technical indicators first, based on the original 'close' series.
    # This is more efficient and prevents pandas SettingWithCopyWarning.
    close_prices = df["close"]
    rsi = calculate_rsi(close_prices)
    macd_line, signal_line, histogram = calculate_macd(close_prices)
    sma_20 = calculate_sma(close_prices, period=20)
    sma_50 = calculate_sma(close_prices, period=50)

    # Assign all indicators to the DataFrame at once.
    df = df.assign(
        rsi=rsi,
        macd_line=macd_line,
        signal_line=signal_line,
        histogram=histogram,
        sma_20=sma_20,
        sma_50=sma_50,
    )

    # Create target variable (1 if the price goes up in the next period, 0 otherwise)
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)

    # Drop rows with missing values
    df.dropna(inplace=True)

    return df


if __name__ == "__main__":
    # Load sample data
    data_dir = "data"
    file_path = os.path.join(data_dir, "sample_data.csv")

    # Create sample data if it doesn't exist
    if not os.path.exists(file_path):
        print("Creating sample data...")
        num_rows = 1000
        data = {
            "timestamp": pd.to_datetime(
                pd.date_range(start="2023-01-01", periods=num_rows, freq="h")
            ),
            "open": pd.Series(np.random.uniform(40000, 41000, num_rows)),
            "high": pd.Series(np.random.uniform(41000, 42000, num_rows)),
            "low": pd.Series(np.random.uniform(39000, 40000, num_rows)),
            "close": pd.Series(np.random.uniform(40000, 41000, num_rows)),
            "volume": pd.Series(np.random.uniform(1000, 2000, num_rows)),
        }
        df = pd.DataFrame(data)

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        df.to_csv(file_path, index=False)
        print(f"Sample data saved to {file_path}")

    df = pd.read_csv(file_path)

    # Create features
    df = create_features(df)

    # Save the features to a new CSV file
    features_file_path = os.path.join(data_dir, "features.csv")
    df.to_csv(features_file_path, index=False)
    print(f"Features saved to {features_file_path}")
