import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..config import settings
from ..models.schemas import (
    OrderRequest,
    OrderResponse,
    OrderStatus,
    OrderType,
    PortfolioStatus,
    SignalType,
    TradeSignal,
)
from ..services.risk_service import RiskService
from ..services.trading_service import TradingService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/trading", tags=["trading"])
logger = logging.getLogger(__name__)

# Initialize services
trading_service = TradingService()
risk_service = RiskService()


@router.get("/signals", response_model=List[TradeSignal])
async def get_active_signals(
    symbol: Optional[str] = None, current_user: dict = Depends(get_current_user)
):
    """
    Retrieves a list of active trading signals.

    Can be filtered by a specific symbol.

    Args:
        symbol (Optional[str]): The symbol to filter signals for.
        current_user (dict): The authenticated user.

    Returns:
        List[TradeSignal]: A list of active trading signals.

    Raises:
        HTTPException: If signals cannot be retrieved.
    """
    try:
        signals = await trading_service.get_active_signals(symbol)
        return signals
    except Exception as e:
        logger.error(f"Failed to get trading signals: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve trading signals"
        )


@router.post("/signals", response_model=TradeSignal)
async def create_signal(
    symbol: str,
    signal_type: SignalType,
    confidence: float,
    current_user: dict = Depends(get_current_user),
):
    """
    Creates a new trading signal after passing a risk assessment.

    Args:
        symbol (str): The trading symbol for the signal.
        signal_type (SignalType): The type of signal (e.g., long or short).
        confidence (float): The confidence level of the signal.
        current_user (dict): The authenticated user.

    Returns:
        TradeSignal: The newly created trading signal.

    Raises:
        HTTPException: If the signal is rejected by risk management or if
                       the creation process fails.
    """
    try:
        # Risk assessment
        risk_assessment = await risk_service.assess_signal_risk(
            symbol=symbol, signal_type=signal_type, confidence=confidence
        )

        if not risk_assessment["approved"]:
            raise HTTPException(
                status_code=400,
                detail=f"Signal rejected by risk management: {risk_assessment['reason']}",
            )

        # Create signal
        signal = await trading_service.create_signal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence,
            risk_params=risk_assessment["params"],
        )

        return signal

    except Exception as e:
        logger.error(f"Failed to create signal: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create signal: {str(e)}"
        )


@router.post("/orders", response_model=OrderResponse)
async def place_order(
    order_request: OrderRequest, current_user: dict = Depends(get_current_user)
):
    """
    Places a trading order after passing a risk check.

    Args:
        order_request (OrderRequest): The details of the order to be placed.
        current_user (dict): The authenticated user.

    Returns:
        OrderResponse: The response from the trading service after placing the order.

    Raises:
        HTTPException: If the order is rejected by risk management or if the
                       order placement fails.
    """
    try:
        # Risk check
        risk_check = await risk_service.check_order_risk(order_request)
        if not risk_check["approved"]:
            raise HTTPException(
                status_code=400, detail=f"Order rejected: {risk_check['reason']}"
            )

        # Place order
        order = await trading_service.place_order(order_request)
        return order

    except Exception as e:
        logger.error(f"Failed to place order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Retrieves the details of a specific order by its ID.

    Args:
        order_id (str): The unique identifier of the order.
        current_user (dict): The authenticated user.

    Returns:
        OrderResponse: The details of the requested order.

    Raises:
        HTTPException: If the order is not found or if retrieval fails.
    """
    try:
        order = await trading_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        logger.error(f"Failed to get order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve order")


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """
    Cancels a specific order by its ID.

    Args:
        order_id (str): The unique identifier of the order to cancel.
        current_user (dict): The authenticated user.

    Returns:
        dict: A confirmation message of the cancellation.

    Raises:
        HTTPException: If the order cancellation fails.
    """
    try:
        result = await trading_service.cancel_order(order_id)
        return {"message": "Order cancelled", "order_id": order_id, "result": result}
    except Exception as e:
        logger.error(f"Failed to cancel order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel order")


@router.get("/portfolio", response_model=PortfolioStatus)
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the current status of the trading portfolio.

    This includes balances, profit/loss, and open positions.

    Args:
        current_user (dict): The authenticated user.

    Returns:
        PortfolioStatus: An object containing the portfolio details.

    Raises:
        HTTPException: If the portfolio status cannot be retrieved.
    """
    try:
        portfolio = await trading_service.get_portfolio_status()
        return portfolio
    except Exception as e:
        logger.error(f"Failed to get portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve portfolio")


@router.post("/auto-trade/start")
async def start_auto_trading(
    symbols: List[str],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """
    Starts an automated trading strategy in a background task.

    Args:
        symbols (List[str]): The list of symbols to include in the auto-trading.
        background_tasks (BackgroundTasks): FastAPI's background task runner.
        current_user (dict): The authenticated user.

    Returns:
        dict: A confirmation message that auto-trading has started.

    Raises:
        HTTPException: If the auto-trading task fails to start.
    """
    try:
        background_tasks.add_task(trading_service.start_auto_trading, symbols)
        return {"message": "Auto trading started", "symbols": symbols}
    except Exception as e:
        logger.error(f"Failed to start auto trading: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start auto trading")


@router.post("/auto-trade/stop")
async def stop_auto_trading(current_user: dict = Depends(get_current_user)):
    """
    Stops the automated trading strategy.

    Args:
        current_user (dict): The authenticated user.

    Returns:
        dict: A confirmation message that auto-trading has stopped.

    Raises:
        HTTPException: If the auto-trading task fails to stop.
    """
    try:
        await trading_service.stop_auto_trading()
        return {"message": "Auto trading stopped"}
    except Exception as e:
        logger.error(f"Failed to stop auto trading: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop auto trading")
