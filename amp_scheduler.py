#!/usr/bin/env python3
"""
AMP Scheduler Module
Handles automated job scheduling and execution
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import schedule

from amp_auth import check_auth, get_user_info
from amp_job_runner import AMPJobRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/amp_scheduler.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AMPScheduler:
    """
    Handles automated job scheduling and execution for the AMP system.

    This class uses the 'schedule' library to run jobs at specified intervals.

    Attributes:
        scheduler_config (Path): The path to the scheduler's configuration file.
        job_runner (AMPJobRunner): An instance of the job runner to execute tasks.
        is_running (bool): True if the scheduler's main loop is active.
        config (Dict): The loaded scheduler configuration.
    """

    def __init__(self):
        """Initializes the AMPScheduler."""
        self.scheduler_config = Path("amp_scheduler_config.json")
        self.job_runner = AMPJobRunner()
        self.is_running = False

        self.default_schedule = {
            "market_open": "09:00",
            "market_close": "17:00",
            "interval_minutes": 30,
            "timezone": "UTC",
            "enabled": True,
        }
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Loads the scheduler configuration from a JSON file, or creates a default."""
        if self.scheduler_config.exists():
            try:
                with open(self.scheduler_config, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading scheduler config: {e}")
                self.config = self.default_schedule
        else:
            self.config = self.default_schedule
            self.save_config()

    def save_config(self):
        """Saves the current scheduler configuration to a JSON file."""
        try:
            with open(self.scheduler_config, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving scheduler config: {e}")

    async def run_scheduled_job(self):
        """
        Executes a single scheduled job run.

        This method checks for authentication and then triggers the job runner.
        """
        try:
            if not check_auth():
                logger.warning("User not authenticated. Skipping scheduled job.")
                return

            user_info = get_user_info()
            logger.info(f"Running scheduled job for user: {user_info.get('user_id')}")

            await self.job_runner.run_next_job()

            logger.info("Scheduled job completed successfully.")
        except Exception as e:
            logger.error(f"Error during scheduled job execution: {e}")

    def setup_schedule(self):
        """Sets up the job schedule based on the loaded configuration."""
        schedule.clear()

        if not self.config.get("enabled", True):
            logger.info("Scheduler is disabled in the configuration.")
            return

        interval = self.config.get("interval_minutes", 30)
        schedule.every(interval).minutes.do(
            lambda: asyncio.run(self.run_scheduled_job())
        )
        logger.info(f"Scheduler configured to run jobs every {interval} minutes.")

    def start(self):
        """Starts the scheduler's main loop."""
        if self.is_running:
            logger.warning("Scheduler is already running.")
            return

        logger.info("Starting AMP Scheduler...")
        self.is_running = True
        self.setup_schedule()

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)  # Check for pending jobs every second
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user.")
                break
            except Exception as e:
                logger.error(f"An error occurred in the scheduler loop: {e}")
                time.sleep(60)  # Wait before retrying on error

    def stop(self):
        """Stops the scheduler's main loop."""
        logger.info("Stopping AMP Scheduler...")
        self.is_running = False

    def get_status(self) -> Dict[str, Any]:
        """
        Gets the current status of the scheduler.

        Returns:
            Dict[str, Any]: A dictionary with status information.
        """
        return {
            "is_running": self.is_running,
            "config": self.config,
            "next_jobs": [str(job) for job in schedule.jobs],
            "last_run": self.get_last_run_time(),
        }

    def get_last_run_time(self) -> Optional[str]:
        """
        Gets the timestamp of the last job run by parsing the log file.

        Returns:
            Optional[str]: The timestamp of the last run, or None if not found.
        """
        log_file = Path("logs/amp_scheduler.log")
        if not log_file.exists():
            return None
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in reversed(list(f)):
                    if "Running scheduled job" in line:
                        return line.split(" - ")[0]
        except Exception as e:
            logger.warning(f"Could not read last run time from log: {e}")
        return None

    def update_config(self, **kwargs):
        """
        Updates the scheduler's configuration and saves it.

        If the scheduler is running, it will be restarted to apply the changes.

        Args:
            **kwargs: Configuration key-value pairs to update.
        """
        self.config.update(kwargs)
        self.save_config()
        logger.info(f"Scheduler configuration updated: {kwargs}")

        if self.is_running:
            logger.info("Restarting scheduler to apply new configuration...")
            # This restart logic might be better handled by a process manager
            self.setup_schedule()


# Global scheduler instance
amp_scheduler = AMPScheduler()


def start_scheduler():
    """A convenience function to start the global AMP scheduler."""
    amp_scheduler.start()


def stop_scheduler():
    """A convenience function to stop the global AMP scheduler."""
    amp_scheduler.stop()


def get_scheduler_status() -> Dict[str, Any]:
    """A convenience function to get the status of the global scheduler."""
    return amp_scheduler.get_status()


def update_scheduler_config(**kwargs):
    """A convenience function to update the global scheduler's configuration."""
    amp_scheduler.update_config(**kwargs)
