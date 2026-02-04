import json
import os
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""

    # Default configuration
    default_config = {
        "database_url": os.getenv(
            "DATABASE_URL", "postgresql://user:password@localhost/db"
        ),
        "mongodb_url": os.getenv("MONGODB_URL", "mongodb://localhost:27017/db"),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "timeframes": ["1m", "5m", "15m", "1h"],
        "retrain_interval": 3600,
        "min_training_samples": 1000,
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                file_config = json.load(f)
                default_config.update(file_config)
    except Exception as e:
        print(f"Error loading config from {config_path}: {e}")

    return default_config
