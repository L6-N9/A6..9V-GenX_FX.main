"""
Logger Setup for GenX FX Trading System
Handles logging configuration and setup
"""

import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str = None):
    """Setup logging configuration"""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file or "logs/genx_trading.log"),
        ],
    )

    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging setup completed")
