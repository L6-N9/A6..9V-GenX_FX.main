from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OrderType(str, Enum):
    """Enumeration for the type of an order."""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Enumeration for the status of an order."""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class SignalType(str, Enum):
    """Enumeration for the type of a trading signal."""

    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


# Market Data Schemas
class MarketData(BaseModel):
    """Schema for representing market data for a specific symbol and time."""

    symbol: str = Field(..., description="The trading symbol (e.g., 'XAUUSD').")
    price: float = Field(..., description="The current price of the asset.")
    volume: float = Field(..., description="The trading volume.")
    timestamp: datetime = Field(..., description="The timestamp of the data point.")
    high: float = Field(..., description="The highest price in the interval.")
    low: float = Field(..., description="The lowest price in the interval.")
    open: float = Field(..., description="The opening price of the interval.")
    close: float = Field(..., description="The closing price of the interval.")


class PredictionRequest(BaseModel):
    """Schema for requesting a market prediction."""

    symbol: str = Field(..., description="The symbol to get a prediction for.")
    timeframe: str = Field(
        "1h", description="The timeframe for the prediction (e.g., '1h', '4h')."
    )
    use_ensemble: bool = Field(
        True, description="Whether to use an ensemble of models for prediction."
    )


class PredictionResponse(BaseModel):
    """Schema for the response of a market prediction."""

    symbol: str = Field(
        ..., description="The symbol for which the prediction was made."
    )
    prediction: SignalType = Field(
        ..., description="The predicted signal type (long, short, or neutral)."
    )
    confidence: float = Field(
        ..., description="The confidence level of the prediction (0.0 to 1.0)."
    )
    timestamp: datetime = Field(
        ..., description="The timestamp of when the prediction was generated."
    )
    features_used: List[str] = Field(
        ..., description="A list of features used to make the prediction."
    )
    model_version: str = Field(
        ..., description="The version of the model that made the prediction."
    )


# Trading Schemas
class TradeSignal(BaseModel):
    """Schema for a complete trading signal."""

    symbol: str = Field(..., description="The trading symbol.")
    signal_type: SignalType = Field(
        ..., description="The type of signal (long or short)."
    )
    entry_price: float = Field(
        ..., description="The suggested entry price for the trade."
    )
    stop_loss: float = Field(..., description="The suggested stop-loss price.")
    take_profit: float = Field(..., description="The suggested take-profit price.")
    confidence: float = Field(..., description="The confidence level of the signal.")
    risk_reward_ratio: float = Field(
        ..., description="The risk/reward ratio of the trade."
    )
    timestamp: datetime = Field(
        ..., description="The timestamp when the signal was generated."
    )


class OrderRequest(BaseModel):
    """Schema for requesting a new trade order."""

    symbol: str = Field(..., description="The symbol to trade.")
    order_type: OrderType = Field(..., description="The type of order (buy or sell).")
    quantity: float = Field(..., description="The quantity to trade (e.g., lot size).")
    price: Optional[float] = Field(
        None, description="The price for limit or stop orders."
    )
    stop_loss: Optional[float] = Field(
        None, description="The stop-loss price for the order."
    )
    take_profit: Optional[float] = Field(
        None, description="The take-profit price for the order."
    )


class OrderResponse(BaseModel):
    """Schema for the response after placing an order."""

    order_id: str = Field(..., description="The unique identifier for the order.")
    symbol: str = Field(..., description="The symbol traded.")
    order_type: OrderType = Field(..., description="The type of order placed.")
    quantity: float = Field(..., description="The quantity of the order.")
    price: float = Field(
        ..., description="The price at which the order was placed/filled."
    )
    status: OrderStatus = Field(..., description="The current status of the order.")
    timestamp: datetime = Field(..., description="The timestamp of the order response.")


# Portfolio Schemas
class PortfolioStatus(BaseModel):
    """Schema for representing the current status of the trading portfolio."""

    total_balance: float = Field(..., description="The total account balance.")
    available_balance: float = Field(
        ..., description="The balance available for new trades."
    )
    unrealized_pnl: float = Field(
        ..., description="The profit or loss on open positions."
    )
    realized_pnl: float = Field(
        ..., description="The profit or loss from closed positions."
    )
    positions: List[Dict[str, Any]] = Field(
        ..., description="A list of currently open positions."
    )
    open_orders: List[Dict[str, Any]] = Field(
        ..., description="A list of pending orders."
    )


# AI Model Schemas
class ModelMetrics(BaseModel):
    """Schema for representing the performance metrics of an AI model."""

    accuracy: float = Field(..., description="The accuracy of the model.")
    precision: float = Field(..., description="The precision score of the model.")
    recall: float = Field(..., description="The recall score of the model.")
    f1_score: float = Field(..., description="The F1-score of the model.")
    last_updated: datetime = Field(
        ..., description="When the metrics were last calculated."
    )


class ModelRetraining(BaseModel):
    """Schema for initiating a model retraining process."""

    model_name: str = Field(..., description="The name of the model to be retrained.")
    data_start_date: datetime = Field(
        ..., description="The start date for the training data."
    )
    data_end_date: datetime = Field(
        ..., description="The end date for the training data."
    )
    symbols: List[str] = Field(
        ..., description="The list of symbols to use for training."
    )
    features: List[str] = Field(
        ..., description="The list of features to use for training."
    )


# Account Performance Schemas
class PerformanceUpdate(BaseModel):
    """Schema for updating account performance data."""

    account_number: str = Field(..., description="The MT5 account number.")
    balance: float = Field(..., description="The current account balance.")
    equity: float = Field(..., description="The current account equity.")
    total_profit: float = Field(..., description="The total realized profit.")
    total_loss: float = Field(..., description="The total realized loss.")
    currency: str = Field("USD", description="The account currency.")
    timestamp: Optional[datetime] = Field(
        None, description="The timestamp of the update."
    )


class AccountPerformance(PerformanceUpdate):
    """Schema for representing historical account performance."""

    id: Optional[int] = Field(None, description="The unique identifier for the record.")
    pnl: float = Field(..., description="The net profit or loss (profit - loss).")
    profit_factor: Optional[float] = Field(
        None, description="The ratio of total profit to total loss."
    )


# System Status
class SystemStatus(BaseModel):
    """Schema for representing the overall status of the trading system."""

    api_status: str = Field(
        ..., description="The status of the main API (e.g., 'online', 'offline')."
    )
    database_status: str = Field(
        ..., description="The status of the database connection."
    )
    model_status: str = Field(..., description="The status of the AI prediction model.")
    trading_enabled: bool = Field(
        ..., description="Whether automated trading is currently enabled."
    )
    last_update: datetime = Field(
        ..., description="The timestamp of the last status update."
    )
    active_strategies: List[str] = Field(
        ..., description="A list of currently active trading strategies."
    )
