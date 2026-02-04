import asyncio
import json
import logging
import time
from datetime import datetime
from typing import List, Optional

import joblib
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..config import settings
from ..redis import redis_client
from ..models.schemas import (
    ModelMetrics,
    PredictionRequest,
    PredictionResponse,
    SignalType,
)
from ..services.data_service import DataService
from ..services.ml_service import MLService
from ..utils.auth import get_current_user

router = APIRouter(prefix="/predictions", tags=["predictions"])
logger = logging.getLogger(__name__)

# Initialize services
ml_service = MLService()
data_service = DataService()


@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """
    Generates an AI-powered market prediction for a given symbol.

    This endpoint retrieves real-time market data, uses the machine learning
    service to generate a prediction, and logs the prediction in a background task.

    Args:
        request (PredictionRequest): The request body containing the symbol and other
                                     prediction parameters.
        background_tasks (BackgroundTasks): FastAPI's background task runner.
        current_user (dict): The authenticated user.

    Returns:
        PredictionResponse: An object containing the prediction details.

    Raises:
        HTTPException: If data for the symbol cannot be found or if the
                       prediction process fails.
    """
    try:
        # Get real-time market data
        market_data = await data_service.get_realtime_data(request.symbol)
        if market_data is None or market_data.empty:
            raise HTTPException(
                status_code=404, detail=f"No data found for symbol {request.symbol}"
            )

        # Generate prediction
        prediction_result = await ml_service.predict(
            symbol=request.symbol,
            market_data=market_data,
            use_ensemble=request.use_ensemble,
        )

        # Log prediction for future model training
        background_tasks.add_task(
            ml_service.log_prediction, request.symbol, prediction_result
        )

        return PredictionResponse(
            symbol=request.symbol,
            prediction=SignalType(prediction_result["prediction"]),
            confidence=prediction_result["confidence"],
            timestamp=datetime.now(),
            features_used=prediction_result["features"],
            model_version=prediction_result["model_version"],
        )

    except Exception as e:
        logger.error(f"Prediction error for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/batch/{symbols}")
async def batch_predictions(
    symbols: str,
    background_tasks: BackgroundTasks,
    timeframe: str = "1h",
    use_ensemble: bool = True,
    current_user: dict = Depends(get_current_user),
):
    """
    Generates predictions for a batch of symbols concurrently.
    This endpoint is optimized to fetch all market data in a single batch
    to avoid the N+1 problem, making it much more efficient than calling
    the prediction endpoint for each symbol individually.
    Args:
        symbols (str): A comma-separated string of symbols (e.g., "BTCUSDT,ETHUSDT").
        background_tasks (BackgroundTasks): FastAPI's background task runner.
        use_ensemble (bool): Whether to use the ensemble model.
        current_user (dict): The authenticated user.
    Returns:
        dict: A dictionary containing lists of successful predictions and errors.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    predictions = []
    errors = []

    # --- Performance Optimization: Batch Data Fetching ---
    # Instead of fetching data for each symbol one by one, we fetch it all
    # in a single batch. This significantly reduces latency and API calls.
    market_data_batch = await data_service.get_batch_realtime_data(
        symbol_list, timeframe
    )

    # --- Concurrently generate predictions ---
    prediction_tasks = []
    valid_symbols = []
    for symbol in symbol_list:
        if symbol in market_data_batch and not market_data_batch[symbol].empty:
            task = ml_service.predict(
                symbol=symbol,
                market_data=market_data_batch[symbol],
                use_ensemble=use_ensemble,
            )
            prediction_tasks.append(task)
            valid_symbols.append(symbol)
        else:
            errors.append({"symbol": symbol, "error": "Market data not found"})

    results = await asyncio.gather(*prediction_tasks, return_exceptions=True)

    # --- Process results and log predictions ---
    for i, result in enumerate(results):
        symbol = valid_symbols[i]
        if isinstance(result, Exception):
            errors.append({"symbol": symbol, "error": str(result)})
        else:
            # Log prediction in the background
            background_tasks.add_task(ml_service.log_prediction, symbol, result)

            # Create the response object
            predictions.append(
                PredictionResponse(
                    symbol=symbol,
                    prediction=SignalType(result["prediction"]),
                    confidence=result["confidence"],
                    timestamp=datetime.now(),
                    features_used=result["features"],
                    model_version=result["model_version"],
                )
            )

    return {
        "predictions": predictions,
        "errors": errors,
        "total_processed": len(symbol_list),
    }


@router.get("/model/metrics", response_model=ModelMetrics)
async def get_model_metrics(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the performance metrics of the current prediction model.
    This endpoint is optimized with a Redis cache and a distributed lock to prevent
    a "cache stampede" when metrics are recalculated. If Redis is unavailable,
    it gracefully falls back to direct calculation.
    Args:
        current_user (dict): The authenticated user.
    Returns:
        ModelMetrics: An object containing model performance metrics.
    Raises:
        HTTPException: If the metrics cannot be retrieved.
    """
    # --- Performance Optimization: Redis Cache & Lock ---
    # This entire block only runs if Redis is available.
    if redis_client:
        try:
            # 1. Check cache first
            cached_metrics = await redis_client.get("model_metrics")
            if cached_metrics:
                return ModelMetrics(**json.loads(cached_metrics))

            # 2. If no cache, try to acquire a lock to prevent a stampede
            lock_key = "lock:model_metrics"
            lock_acquired = await redis_client.set(lock_key, "1", nx=True, ex=10)

            if lock_acquired:
                try:
                    # 3. Double-check cache after getting lock, in case another
                    # process populated it while we were waiting.
                    cached_metrics = await redis_client.get("model_metrics")
                    if cached_metrics:
                        return ModelMetrics(**json.loads(cached_metrics))

                    # 4. If still no cache, calculate, cache, and return
                    metrics = await ml_service.get_model_metrics()
                    await redis_client.setex("model_metrics", 3600, json.dumps(metrics))
                    return ModelMetrics(**metrics)
                finally:
                    # 5. Always release the lock
                    await redis_client.delete(lock_key)
            else:
                # 6. If lock not acquired, wait briefly and retry the cache
                await asyncio.sleep(0.1)  # Use asyncio.sleep in an async function
                cached_metrics = await redis_client.get("model_metrics")
                if cached_metrics:
                    return ModelMetrics(**json.loads(cached_metrics))

                logger.warning(
                    "Could not get model metrics from cache after waiting for lock."
                )
        except Exception as e:
            # If any Redis operation fails, log the error and fall through
            # to the non-cached calculation.
            logger.error(
                f"Redis operation failed: {e}. Falling back to direct calculation."
            )

    # --- Fallback Logic ---
    # This code runs if Redis is not available OR if any Redis operation failed.
    try:
        metrics = await ml_service.get_model_metrics()
        return ModelMetrics(**metrics)
    except Exception as e:
        logger.error(f"Failed to get model metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model metrics")


@router.post("/model/retrain")
async def retrain_model(
    background_tasks: BackgroundTasks,
    symbols: List[str] = ["BTCUSDT", "ETHUSDT"],
    current_user: dict = Depends(get_current_user),
):
    """
    Triggers a background task to retrain the prediction model.

    This endpoint also invalidates the model metrics cache to ensure that
    fresh metrics are served after the model is updated.

    Args:
        background_tasks (BackgroundTasks): FastAPI's background task runner.
        symbols (List[str]): A list of symbols to use for retraining the model.
        current_user (dict): The authenticated user.

    Returns:
        dict: A confirmation message that the retraining has started.

    Raises:
        HTTPException: If the retraining task fails to start.
    """
    try:
        # --- Performance: Invalidate cache before retraining ---
        if redis_client:
            try:
                await redis_client.delete("model_metrics")
            except Exception as e:
                logger.error(f"Redis cache delete error: {e}")

        background_tasks.add_task(ml_service.retrain_model, symbols)
        return {"message": "Model retraining started", "symbols": symbols}
    except Exception as e:
        logger.error(f"Failed to start model retraining: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start model retraining")
