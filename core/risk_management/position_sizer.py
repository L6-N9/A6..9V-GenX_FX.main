"""
Position Sizing and Risk Management for GenX FX Trading System
Manages position sizes, risk limits, and portfolio risk
"""

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .sortino_ratio_analyzer import SortinoRatioAnalyzer

# Try to import pandas and numpy, but provide fallbacks if not available
try:
    import numpy as np
    import pandas as pd

    PANDAS_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    NUMPY_AVAILABLE = False

    # Create simple fallback classes
    class pd:
        @staticmethod
        def Timestamp():
            return datetime.now()

    class np:
        @staticmethod
        def round(x, decimals=0):
            return round(x, decimals)


class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class PositionInfo:
    """
    A data structure holding all relevant information for a calculated position.

    Attributes:
        symbol (str): The trading symbol.
        entry_price (float): The price at which the position should be entered.
        position_size (float): The calculated size of the position (e.g., in lots).
        stop_loss (float): The calculated stop-loss price.
        take_profit (float): The calculated take-profit price.
        risk_amount (float): The total amount of account currency at risk.
        risk_percent (float): The risk as a percentage of the total account balance.
        max_loss (float): The maximum potential loss for this position.
    """

    symbol: str
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    risk_percent: float
    max_loss: float


class PositionSizer:
    """
    A class for calculating position sizes and managing overall portfolio risk.

    This class determines the optimal position size for a new trade based on
    pre-defined risk management rules, including account balance, risk per trade,
    and overall portfolio risk limits.

    Attributes:
        account_balance (float): The total balance of the trading account.
        max_risk_per_trade (float): The maximum risk per trade as a percentage.
        max_portfolio_risk (float): The maximum total risk for the entire portfolio.
        risk_level (RiskLevel): The current risk appetite (e.g., CONSERVATIVE).
        active_positions (Dict): A dictionary tracking currently open positions.
    """

    def __init__(
        self,
        account_balance: float = 10000.0,
        max_risk_per_trade: float = 0.02,
        max_portfolio_risk: float = 0.20,
        risk_level: RiskLevel = RiskLevel.MODERATE,
    ):
        """
        Initializes the PositionSizer.

        Args:
            account_balance (float): The total account balance.
            max_risk_per_trade (float): Max risk per trade as a percentage (e.g., 0.02 for 2%).
            max_portfolio_risk (float): Max total portfolio risk as a percentage (e.g., 0.20 for 20%).
            risk_level (RiskLevel): The risk management level to apply.
        """
        self.account_balance = account_balance
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.risk_level = risk_level
        self.sortino_analyzer = SortinoRatioAnalyzer()

        # Risk multipliers based on risk level
        self.risk_multipliers = {
            RiskLevel.CONSERVATIVE: 0.5,
            RiskLevel.MODERATE: 1.0,
            RiskLevel.AGGRESSIVE: 2.0,
        }

        # Active positions tracking
        self.active_positions = {}
        self.position_history = []

    def calculate_position_size(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        confidence: float = 1.0,
        current_positions: int = 0,
    ) -> PositionInfo:
        """
        Calculates the optimal position size based on risk management rules.

        The calculation considers the risk per trade, signal confidence, current
        portfolio concentration, and applies position size limits.

        Args:
            symbol (str): The trading symbol.
            entry_price (float): The intended entry price for the position.
            stop_loss (float): The intended stop-loss price.
            confidence (float): The confidence level of the signal (0.0 to 1.0).
            current_positions (int): The number of currently open positions.

        Returns:
            PositionInfo: A data object with the calculated position details.
        """
        try:
            # Validate inputs
            if entry_price <= 0 or stop_loss <= 0:
                raise ValueError("Entry price and stop loss must be positive")

            confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1

            # Calculate risk per pip/point
            price_difference = abs(entry_price - stop_loss)
            if price_difference == 0:
                price_difference = entry_price * 0.01  # Default 1% if no stop loss

            # Adjust risk based on confidence and risk level
            base_risk = self.max_risk_per_trade
            risk_multiplier = self.risk_multipliers[self.risk_level]
            adjusted_risk = base_risk * risk_multiplier * confidence

            # Reduce risk if portfolio is concentrated
            portfolio_risk_adjustment = self._calculate_portfolio_risk_adjustment(
                current_positions
            )
            final_risk = adjusted_risk * portfolio_risk_adjustment

            # Calculate risk amount in account currency
            risk_amount = self.account_balance * final_risk

            # Calculate position size
            position_size = risk_amount / price_difference

            # Apply position size limits
            position_size = self._apply_position_limits(position_size, entry_price)

            # Calculate actual risk and take profit
            actual_risk = position_size * price_difference
            take_profit = self._calculate_take_profit(
                entry_price, stop_loss, confidence
            )

            return PositionInfo(
                symbol=symbol,
                entry_price=entry_price,
                position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=actual_risk,
                risk_percent=actual_risk / self.account_balance,
                max_loss=actual_risk,
            )

        except Exception as e:
            print(f"Warning: Error calculating position size: {e}")
            return self._default_position_info(symbol, entry_price, stop_loss)

    def _calculate_portfolio_risk_adjustment(self, current_positions: int) -> float:
        """
        Calculates a risk adjustment factor based on portfolio concentration.

        Args:
            current_positions (int): The number of currently open positions.

        Returns:
            float: A multiplier to adjust the risk for a new trade.
        """
        if current_positions == 0:
            return 1.0
        elif current_positions <= 3:
            return 0.8
        elif current_positions <= 5:
            return 0.6
        else:
            return 0.4  # Heavily reduce risk when portfolio is over-concentrated

    def _apply_position_limits(self, position_size: float, entry_price: float) -> float:
        """
        Applies minimum and maximum position size limits to a calculated size.

        Args:
            position_size (float): The initially calculated position size.
            entry_price (float): The entry price, used for calculating max value.

        Returns:
            float: The adjusted position size, conforming to limits.
        """
        min_position = 0.01  # e.g., 0.01 lots in forex

        # Max position size as 5% of account balance value
        max_position_value = self.account_balance * 0.05
        max_position = max_position_value / entry_price

        # Apply limits and round to a standard lot size format
        sized_position = max(min_position, min(position_size, max_position))
        return round(sized_position, 2)

    def _calculate_take_profit(
        self, entry_price: float, stop_loss: float, confidence: float
    ) -> float:
        """
        Calculates a dynamic take-profit level based on a risk-reward ratio.

        The risk-reward ratio is adjusted based on the signal's confidence.

        Args:
            entry_price (float): The position's entry price.
            stop_loss (float): The position's stop-loss price.
            confidence (float): The confidence of the trading signal.

        Returns:
            float: The calculated take-profit price.
        """
        stop_distance = abs(entry_price - stop_loss)
        base_rr_ratio = 2.0  # Base 1:2 risk-reward
        rr_ratio = base_rr_ratio * (
            1 + confidence * 0.5
        )  # Adjust up to 1:3 for high confidence

        if entry_price > stop_loss:  # Long position
            take_profit = entry_price + (stop_distance * rr_ratio)
        else:  # Short position
            take_profit = entry_price - (stop_distance * rr_ratio)

        return round(take_profit, 5)  # Round for forex prices

    def _default_position_info(
        self, symbol: str, entry_price: float, stop_loss: float
    ) -> PositionInfo:
        """
        Returns a default, minimum-risk position info object in case of errors.

        Args:
            symbol (str): The trading symbol.
            entry_price (float): The entry price.
            stop_loss (float): The stop-loss price.

        Returns:
            PositionInfo: A default position info object.
        """
        return PositionInfo(
            symbol=symbol,
            entry_price=entry_price,
            position_size=0.01,  # Minimum position size
            stop_loss=stop_loss,
            take_profit=entry_price * 1.02,  # Default 2% take profit
            risk_amount=self.account_balance * 0.01,  # Default 1% risk
            risk_percent=0.01,
            max_loss=self.account_balance * 0.01,
        )

    def add_position(self, position_info: PositionInfo) -> bool:
        """
        Adds a new position to the active positions tracker if it's within portfolio risk limits.

        Args:
            position_info (PositionInfo): The information of the position to add.

        Returns:
            bool: True if the position was added successfully, False otherwise.
        """
        try:
            # Check if adding this position would exceed the max portfolio risk
            current_total_risk = self._calculate_total_portfolio_risk()
            new_total_risk = current_total_risk + position_info.risk_percent

            if new_total_risk > self.max_portfolio_risk:
                print(
                    f"Warning: Position rejected - would exceed portfolio risk limit "
                    f"({new_total_risk:.2%} > {self.max_portfolio_risk:.2%})"
                )
                return False

            # Add position to tracking
            self.active_positions[position_info.symbol] = position_info
            return True

        except Exception as e:
            print(f"Warning: Error adding position: {e}")
            return False

    def remove_position(
        self,
        symbol: str,
        exit_price: Optional[float] = None,
        profit_loss: Optional[float] = None,
    ) -> bool:
        """
        Removes a position from active tracking and logs it to history.

        Args:
            symbol (str): The symbol of the position to remove.
            exit_price (Optional[float]): The price at which the position was closed.
            profit_loss (Optional[float]): The realized profit or loss.

        Returns:
            bool: True if the position was found and removed, False otherwise.
        """
        try:
            if symbol in self.active_positions:
                position = self.active_positions[symbol]

                # Calculate P&L if exit price is provided
                if exit_price is not None and profit_loss is None:
                    profit_loss = (
                        exit_price - position.entry_price
                    ) * position.position_size

                # Add to history
                self.position_history.append(
                    {
                        "symbol": symbol,
                        "entry_price": position.entry_price,
                        "exit_price": exit_price,
                        "position_size": position.position_size,
                        "profit_loss": profit_loss,
                        "exit_time": (
                            pd.Timestamp.now() if PANDAS_AVAILABLE else datetime.now()
                        ),
                    }
                )

                # Remove from active positions
                del self.active_positions[symbol]
                return True

            return False

        except Exception as e:
            print(f"Warning: Error removing position: {e}")
            return False

    def _calculate_total_portfolio_risk(self) -> float:
        """
        Calculates the total current risk of all active positions.

        Returns:
            float: The sum of risk percentages of all active positions.
        """
        return sum(pos.risk_percent for pos in self.active_positions.values())

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Gets a summary of the current portfolio's risk and exposure.

        Returns:
            Dict[str, Any]: A dictionary containing key portfolio metrics.
        """
        try:
            total_risk = self._calculate_total_portfolio_risk()
            total_exposure = sum(
                pos.position_size * pos.entry_price
                for pos in self.active_positions.values()
            )

            return {
                "account_balance": self.account_balance,
                "active_positions": len(self.active_positions),
                "total_risk_percent": total_risk,
                "total_risk_amount": total_risk * self.account_balance,
                "total_exposure": total_exposure,
                "remaining_risk_capacity": max(0, self.max_portfolio_risk - total_risk),
                "risk_utilization": (
                    total_risk / self.max_portfolio_risk
                    if self.max_portfolio_risk > 0
                    else 0
                ),
                "positions": list(self.active_positions.keys()),
            }

        except Exception as e:
            print(f"Warning: Error calculating portfolio summary: {e}")
            return {}

    def update_account_balance(self, new_balance: float):
        """
        Updates the account balance and recalculates risk percentages for active positions.

        Args:
            new_balance (float): The new account balance.

        Raises:
            ValueError: If the new balance is not positive.
        """
        try:
            if new_balance <= 0:
                raise ValueError("Account balance must be positive")

            self.account_balance = new_balance

            # Update risk percentages for existing positions
            for position in self.active_positions.values():
                position.risk_percent = position.risk_amount / new_balance

        except Exception as e:
            print(f"Warning: Error updating account balance: {e}")

    def can_open_position(self, risk_amount: float) -> bool:
        """
        Checks if a new position can be opened based on available portfolio risk.

        Args:
            risk_amount (float): The monetary risk amount of the proposed new position.

        Returns:
            bool: True if the new position is within risk limits, False otherwise.
        """
        try:
            if risk_amount <= 0:
                return False

            current_risk_percent = self._calculate_total_portfolio_risk()
            new_risk_percent = risk_amount / self.account_balance
            total_potential_risk = current_risk_percent + new_risk_percent

            return total_potential_risk <= self.max_portfolio_risk

        except Exception as e:
            print(f"Warning: Error checking position capacity: {e}")
            return False

    def get_risk_metrics(self) -> Dict[str, float]:
        """
        Gets a dictionary of detailed risk metrics for the current portfolio.

        Returns:
            Dict[str, float]: A dictionary containing various risk metrics.
        """
        try:
            portfolio_summary = self.get_portfolio_summary()

            active_positions = portfolio_summary.get("active_positions", 0)
            total_risk_percent = portfolio_summary.get("total_risk_percent", 0)

            avg_position_risk = total_risk_percent / max(1, active_positions)

            risk_concentration = (
                total_risk_percent / self.max_portfolio_risk
                if self.max_portfolio_risk > 0
                else 0
            )

            return {
                "max_risk_per_trade": self.max_risk_per_trade,
                "max_portfolio_risk": self.max_portfolio_risk,
                "current_portfolio_risk": total_risk_percent,
                "average_position_risk": avg_position_risk,
                "risk_concentration": risk_concentration,
                "remaining_capacity": portfolio_summary.get(
                    "remaining_risk_capacity", 0
                ),
                "risk_multiplier": self.risk_multipliers[self.risk_level],
            }

        except Exception as e:
            print(f"Warning: Error calculating risk metrics: {e}")
            return {}

    def get_sortino_ratio_assessment(self) -> Dict[str, Any]:
        """
        Calculates and assesses the Sortino Ratio for the trading history.

        Returns:
            Dict[str, Any]: A dictionary with the Sortino Ratio and a qualitative assessment.
        """
        if not self.position_history:
            return {"sortino_ratio": 0, "assessment": "Not enough data"}

        returns = [
            p["profit_loss"]
            for p in self.position_history
            if p["profit_loss"] is not None
        ]
        if len(returns) < 2:
            return {"sortino_ratio": 0, "assessment": "Not enough data"}

        sortino_ratio = self.sortino_analyzer.calculate_sortino_ratio(returns)

        if sortino_ratio > 2.0:
            assessment = "Excellent"
        elif sortino_ratio > 1.0:
            assessment = "Good"
        elif sortino_ratio > 0.0:
            assessment = "Acceptable"
        else:
            assessment = "Poor"

        return {"sortino_ratio": sortino_ratio, "assessment": assessment}

    def set_risk_level(self, risk_level: RiskLevel):
        """
        Updates the risk level for the position sizer.

        Args:
            risk_level (RiskLevel): The new risk level to set.
        """
        self.risk_level = risk_level

    def reset_positions(self):
        """Resets all active position tracking and history, useful for simulations."""
        self.active_positions = {}
        self.position_history = []
