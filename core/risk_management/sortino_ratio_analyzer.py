"""
This module provides the SortinoRatioAnalyzer class for calculating the Sortino ratio,
a measure of risk-adjusted return that focuses on downside volatility.
"""

from typing import List, Union

import numpy as np

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class SortinoRatioAnalyzer:
    """
    A class for calculating the Sortino Ratio.

    The Sortino Ratio is a modification of the Sharpe Ratio that differentiates
    harmful volatility from total overall volatility by using the asset's
    standard deviation of negative asset returns, called downside deviation.
    """

    def calculate_sortino_ratio(
        self,
        returns: Union[List[float], "pd.Series"],
        target_return: float = 0.0,
        annualization_factor: int = 252,
    ) -> float:
        """
        Calculates the Sortino Ratio for a given series of returns.

        Args:
            returns (Union[List[float], pd.Series]): A list or pandas Series of periodic returns.
            target_return (float): The minimum acceptable return, often the risk-free rate.
            annualization_factor (int): The number of trading periods in a year (e.g., 252 for daily).

        Returns:
            float: The annualized Sortino Ratio.
        """
        if PANDAS_AVAILABLE and isinstance(returns, pd.Series):
            returns_arr = returns.values
        else:
            returns_arr = np.array(returns)

        # Calculate annualized average return
        average_return = np.mean(returns_arr)
        annualized_average_return = average_return * annualization_factor

        # Calculate annualized downside deviation
        downside_returns = returns_arr[returns_arr < target_return]
        downside_deviation = np.sqrt(np.mean((downside_returns - target_return) ** 2))
        annualized_downside_deviation = downside_deviation * np.sqrt(
            annualization_factor
        )

        # Calculate Sortino Ratio
        if annualized_downside_deviation == 0:
            return np.inf

        sortino_ratio = (
            annualized_average_return - (target_return * annualization_factor)
        ) / annualized_downside_deviation

        return sortino_ratio
