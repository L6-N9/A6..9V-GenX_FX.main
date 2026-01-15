from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import joblib
import asyncio
from datetime import datetime
import logging

from ..models.schemas import PredictionRequest, PredictionResponse, SignalType, ModelMetrics
from ..config import settings
from ..services.ml_service import MLService
from ..services.data_service import DataService
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
            prediction=SignalType(prediction_result["signal"]),
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
    timeframe: str = "1h",
    use_ensemble: bool = True,
    current_user: dict = Depends(get_current_user),
):
    """
    ⚡ Bolt: Refactor to use batch processing for improved performance.
    Generates predictions for a batch of symbols concurrently.

    Args:
        symbols (str): A comma-separated string of symbols (e.g., "BTCUSDT,ETHUSDT").
        timeframe (str): The timeframe for the predictions.
        use_ensemble (bool): Whether to use the ensemble model.
        current_user (dict): The authenticated user.

    Returns:
        dict: A dictionary containing lists of successful predictions and errors.
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    predictions = []
    errors = []

    try:
        # Fetch data in one batch
        market_data_batch = await data_service.get_batch_realtime_data(symbol_list)

        # Identify symbols for which data fetching failed
        missing_symbols = set(symbol_list) - set(market_data_batch.keys())
        for symbol in missing_symbols:
            errors.append({"symbol": symbol, "error": "No data found"})

        # Run predictions in one batch
        if market_data_batch:
            prediction_results = await ml_service.batch_predict(
                market_data_batch, use_ensemble
            )

            for symbol, result in prediction_results.items():
                predictions.append(
                    PredictionResponse(
                        symbol=symbol,
                        prediction=SignalType(result["signal"]),
                        confidence=result["confidence"],
                        timestamp=datetime.now(),
                        features_used=result["features"],
                        model_version=result["model_version"],
                    )
                )

    except Exception as e:
        logger.error(f"Batch prediction error for symbols {symbols}: {str(e)}")
        # Add a generic error for all symbols if the batch process fails
        for symbol in symbol_list:
            if not any(err["symbol"] == symbol for err in errors):
                 errors.append({"symbol": symbol, "error": f"Batch prediction failed: {str(e)}"})

    successful_symbols = {p.symbol for p in predictions}
    final_errors = [e for e in errors if e["symbol"] not in successful_symbols]

    # Add errors for symbols that were successfully fetched but failed prediction
    prediction_failed_symbols = set(market_data_batch.keys()) - successful_symbols
    for symbol in prediction_failed_symbols:
        final_errors.append({"symbol": symbol, "error": "Prediction failed"})

    return {
        "predictions": predictions,
        "errors": final_errors,
        "total_processed": len(symbol_list),
    }

@router.get("/model/metrics", response_model=ModelMetrics)
async def get_model_metrics(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the performance metrics of the current prediction model.

    Args:
        current_user (dict): The authenticated user.

    Returns:
        ModelMetrics: An object containing model performance metrics.

    Raises:
        HTTPException: If the metrics cannot be retrieved.
    """
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
        background_tasks.add_task(ml_service.retrain_model, symbols)
        return {"message": "Model retraining started", "symbols": symbols}
    except Exception as e:
        logger.error(f"Failed to start model retraining: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start model retraining")
