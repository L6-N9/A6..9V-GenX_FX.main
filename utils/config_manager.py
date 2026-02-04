"""
Configuration Manager for GenX FX Trading System
Handles configuration loading and management
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ConfigManager:
    """Configuration manager for the trading system"""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(
                    f"Config file {self.config_path} not found, using defaults"
                )
                self.config = self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = self.get_default_config()

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return self.config

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "broker": "exness",
            "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
            "timeframes": ["H1", "H4", "D1"],
            "risk_percentage": 2.0,
            "max_positions": 5,
            "stop_loss_pips": 50,
            "take_profit_pips": 100,
        }
