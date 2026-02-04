import json
import logging
import os
import time
from datetime import datetime

import psutil
import redis


def get_system_metrics():
    """
    Gathers system metrics such as CPU usage, memory consumption, and disk space.
    """
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage("/")

    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": cpu_usage,
        "memory": {
            "total": memory_info.total,
            "available": memory_info.available,
            "percent": memory_info.percent,
            "used": memory_info.used,
        },
        "disk": {
            "total": disk_info.total,
            "used": disk_info.used,
            "free": disk_info.free,
            "percent": disk_info.percent,
        },
    }
    return metrics


def main():
    """
    Main function to run the monitoring loop.
    """
    # --- Performance Optimization: Write directly to Redis ---
    # To avoid the performance overhead of writing to a file every 5 seconds,
    # this script now connects to Redis and writes the system metrics directly
    # to a Redis key. This is significantly faster and more efficient than
    # disk I/O, and it allows the API to read the metrics from a shared,
    # in-memory cache.
    # --------------------------------------------------------------------------
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    CACHE_DURATION_SECONDS = 10  # Set a slightly longer TTL for the metrics

    # --- Set up basic logging ---
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    while True:
        try:
            redis_client = redis.Redis(
                host=REDIS_HOST, port=REDIS_PORT, db=0, socket_connect_timeout=1
            )
            redis_client.ping()
            logging.info(
                f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}."
            )

            while True:
                metrics = get_system_metrics()
                try:
                    # --- Serialize metrics to JSON and write to Redis with an expiration ---
                    redis_client.setex(
                        "system_metrics", CACHE_DURATION_SECONDS, json.dumps(metrics)
                    )
                    logging.info(f"Successfully wrote metrics to Redis.")
                except redis.exceptions.ConnectionError as e:
                    logging.error(f"Could not write to Redis: {e}. Reconnecting...")
                    break  # Break inner loop to trigger reconnection
                time.sleep(5)

        except redis.exceptions.ConnectionError as e:
            logging.error(f"Could not connect to Redis: {e}. Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
