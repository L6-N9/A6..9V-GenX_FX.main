import logging
import sqlite3
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from ..models.schemas import AccountPerformance, PerformanceUpdate

router = APIRouter(prefix="/performance", tags=["performance"])
logger = logging.getLogger(__name__)


@router.post("/update", response_model=AccountPerformance)
async def update_performance(
    update: PerformanceUpdate, db: sqlite3.Connection = Depends(get_db)
):
    """
    Updates the account performance data.
    """
    try:
        timestamp = update.timestamp or datetime.now()
        pnl = update.total_profit - update.total_loss
        profit_factor = (
            update.total_profit / update.total_loss
            if update.total_loss > 0
            else update.total_profit
        )

        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO account_performance
            (account_number, balance, equity, total_profit, total_loss, pnl, profit_factor, currency, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                update.account_number,
                update.balance,
                update.equity,
                update.total_profit,
                update.total_loss,
                pnl,
                profit_factor,
                update.currency,
                timestamp.isoformat(),
            ),
        )
        db.commit()

        record_id = cursor.lastrowid

        return AccountPerformance(
            id=record_id,
            account_number=update.account_number,
            balance=update.balance,
            equity=update.equity,
            total_profit=update.total_profit,
            total_loss=update.total_loss,
            pnl=pnl,
            profit_factor=profit_factor,
            currency=update.currency,
            timestamp=timestamp,
        )
    except Exception as e:
        logger.error(f"Failed to update performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_number}", response_model=List[AccountPerformance])
async def get_performance(
    account_number: str, limit: int = 100, db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves performance history for a specific account.
    """
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT * FROM account_performance
            WHERE account_number = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (account_number, limit),
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append(
                AccountPerformance(
                    id=row["id"],
                    account_number=row["account_number"],
                    balance=row["balance"],
                    equity=row["equity"],
                    total_profit=row["total_profit"],
                    total_loss=row["total_loss"],
                    pnl=row["pnl"],
                    profit_factor=row["profit_factor"],
                    currency=row["currency"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                )
            )

        return results
    except Exception as e:
        logger.error(f"Failed to retrieve performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
