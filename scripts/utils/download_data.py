import os
import sys

import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.execution.bybit import BybitAPI


def download_historical_data(symbol, interval, start_time, end_time):
    """
    Downloads historical market data from Bybit and saves it to a CSV file.
    """
    bybit_api = BybitAPI()
    all_data = []

    current_time = start_time
    while current_time < end_time:
        data = bybit_api.get_market_data(
            symbol, interval, limit=1000, startTime=current_time
        )

        if data and data.get("retCode") == 0 and data.get("result", {}).get("list"):
            kline_data = data["result"]["list"]
            all_data.extend(kline_data)

            # The Bybit API returns data in reverse chronological order.
            # The last timestamp is the earliest one.
            last_timestamp = int(kline_data[-1][0])

            # If we have reached the end of the data, break the loop.
            if last_timestamp >= end_time:
                break

            # Update the current time to the last timestamp to fetch the next batch of data.
            current_time = last_timestamp
        else:
            print(f"Error fetching data: {data}")
            break

    if all_data:
        # Create a pandas DataFrame from the data.
        df = pd.DataFrame(
            all_data,
            columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"],
        )

        # Convert the timestamp to a datetime object.
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Save the data to a CSV file.
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        file_path = os.path.join(data_dir, f"{symbol}_{interval}.csv")
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
    else:
        print("No data downloaded.")


if __name__ == "__main__":
    # Download 1-hour data for BTCUSDT from 2023-01-01 to 2024-01-01.
    start_time = 1672531200000
    end_time = 1704067200000
    download_historical_data("BTCUSDT", "60", start_time, end_time)
