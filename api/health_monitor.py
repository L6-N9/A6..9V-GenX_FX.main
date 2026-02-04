import time
from datetime import datetime

import psutil


def get_system_health():
    """
    Retrieves the current health status of the system.

    This function gathers key system metrics such as memory usage, CPU usage,
    and disk usage to provide a snapshot of the system's health.

    Returns:
        dict: A dictionary containing system health information, including:
            - status (str): A hardcoded status 'healthy'.
            - timestamp (str): The current timestamp in ISO format.
            - uptime (float): The system uptime in seconds.
            - memory_usage (float): The percentage of virtual memory used.
            - cpu_usage (float): The current system-wide CPU utilization as a percentage.
            - disk_usage (float): The percentage of disk space used on the root partition.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time(),
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage("/").percent,
    }
