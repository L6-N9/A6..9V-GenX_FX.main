"""
Unified Notifier Service for GenX Trading Platform
Manages notifications across multiple channels (Telegram, Discord, WhatsApp)
"""

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class NotificationService:
    """Unified notification service for multiple channels"""

    def __init__(self):
        """Initialize notification service with all available channels"""
        self.channels = []
        self._initialize_channels()

    def _initialize_channels(self):
        """Initialize all available notification channels"""
        # Import channel modules
        try:
            from services.telegram_bot import telegram_bot

            if telegram_bot.enabled:
                self.channels.append(("telegram", telegram_bot))
                logger.info("Telegram channel initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Telegram: {e}")

        try:
            from services.discord_bot import discord_bot

            if discord_bot.enabled:
                self.channels.append(("discord", discord_bot))
                logger.info("Discord channel initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Discord: {e}")

        try:
            from services.whatsapp_bot import whatsapp_bot

            if whatsapp_bot.enabled:
                self.channels.append(("whatsapp", whatsapp_bot))
                logger.info("WhatsApp channel initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize WhatsApp: {e}")

        if not self.channels:
            logger.warning("No notification channels are configured!")

    def send_signal(self, signal: Dict) -> Dict[str, bool]:
        """
        Send a trading signal to all configured channels

        Args:
            signal: Signal dictionary containing trade information

        Returns:
            Dictionary mapping channel names to success status
        """
        results = {}

        for channel_name, channel_bot in self.channels:
            try:
                success = channel_bot.send_signal(signal)
                results[channel_name] = success
                logger.info(f"Signal sent to {channel_name}: {success}")
            except Exception as e:
                logger.error(f"Error sending signal to {channel_name}: {e}")
                results[channel_name] = False

        return results

    def send_notification(
        self, title: str, message: str, channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send a notification to specified or all channels

        Args:
            title: Notification title
            message: Notification message
            channels: List of specific channels to notify, or None for all

        Returns:
            Dictionary mapping channel names to success status
        """
        results = {}

        for channel_name, channel_bot in self.channels:
            # Skip if specific channels requested and this isn't one of them
            if channels and channel_name not in channels:
                continue

            try:
                success = channel_bot.send_notification(title, message)
                results[channel_name] = success
                logger.info(f"Notification sent to {channel_name}: {success}")
            except Exception as e:
                logger.error(f"Error sending notification to {channel_name}: {e}")
                results[channel_name] = False

        return results

    def send_status_update(
        self, service_name: str, status: str, details: str = ""
    ) -> Dict[str, bool]:
        """
        Send a status update to all configured channels

        Args:
            service_name: Name of the service
            status: Service status
            details: Additional details

        Returns:
            Dictionary mapping channel names to success status
        """
        results = {}

        for channel_name, channel_bot in self.channels:
            try:
                success = channel_bot.send_status_update(service_name, status, details)
                results[channel_name] = success
                logger.info(f"Status update sent to {channel_name}: {success}")
            except Exception as e:
                logger.error(f"Error sending status update to {channel_name}: {e}")
                results[channel_name] = False

        return results

    def get_active_channels(self) -> List[str]:
        """Get list of active channel names"""
        return [name for name, _ in self.channels]


# Create singleton instance
notifier = NotificationService()


def send_signal(signal: Dict) -> Dict[str, bool]:
    """Helper function to send a trading signal"""
    return notifier.send_signal(signal)


def send_notification(
    title: str, message: str, channels: Optional[List[str]] = None
) -> Dict[str, bool]:
    """Helper function to send a notification"""
    return notifier.send_notification(title, message, channels)


def send_status_update(
    service_name: str, status: str, details: str = ""
) -> Dict[str, bool]:
    """Helper function to send a status update"""
    return notifier.send_status_update(service_name, status, details)
