import logging
import sys
from pathlib import Path


def setup_logging():
    """
    Sets up the logging configuration for the application.

    This function configures the root logger to output messages to both a file
    (logs/app.log) and the standard output (console). It also sets specific
    log levels for noisy third-party libraries like uvicorn and sqlalchemy
    to reduce log verbosity.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
