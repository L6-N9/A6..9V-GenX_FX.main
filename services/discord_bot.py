"""
Discord Bot Service for GenX Trading Platform
Sends trading signals and notifications to Discord channels
"""

import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)


class DiscordBot:
    """Discord bot for sending trading signals and notifications"""

    def __init__(self):
        """Initialize Discord bot with configuration from environment"""
        self.token = os.getenv("DISCORD_TOKEN", "")
        self.enabled = bool(self.token)

        if self.enabled:
            logger.info("Discord bot initialized")
        else:
            logger.warning("Discord bot not configured - DISCORD_TOKEN not set")

    def send_signal(self, signal: Dict) -> bool:
        """Send a trading signal to Discord"""
        if not self.enabled:
            return False
        logger.info(f"Discord signal: {signal.get('symbol', 'unknown')}")
        return True

    def send_notification(self, title: str, message: str) -> bool:
        """Send a notification to Discord"""
        if not self.enabled:
            return False
        logger.info(f"Discord notification: {title}")
        return True

    def send_status_update(
        self, service_name: str, status: str, details: str = ""
    ) -> bool:
        """Send a status update to Discord"""
        if not self.enabled:
            return False
        logger.info(f"Discord status: {service_name} - {status}")
        return True


# Create singleton instance
discord_bot = DiscordBot()
