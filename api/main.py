import asyncio
import json
import logging
import os
import re
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

# Check if ai_models module exists and can be imported
try:
    from ai_models.ensemble_predictor import EnsemblePredictor

    has_ai_models = True
except ImportError:
    logging.warning("Could not import ai_models. Predictions will be disabled.")
    has_ai_models = False

# Check if ScalpingService exists and can be imported
try:
    from api.services.scalping_service import ScalpingService

    has_scalping_service = True
except ImportError:
    logging.warning("Could not import ScalpingService.")
    has_scalping_service = False

import api.redis
from api.database import get_db
from api.routers import market_data, performance, predictions, system, trading

predictor = None
scalping_service = None
MONITORING_DASHBOARD_CACHE = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor, MONITORING_DASHBOARD_CACHE, scalping_service

    # --- Redis Setup ---
    await api.redis.init_redis()

    # --- AI Predictor Setup ---
    if has_ai_models:
        try:
            predictor = EnsemblePredictor()
            logging.info("EnsemblePredictor initialized.")
        except Exception as e:
            logging.error(f"Failed to initialize EnsemblePredictor: {e}")
            predictor = None

    # --- Scalping Service Setup ---
    if has_scalping_service:
        try:
            scalping_service = ScalpingService()
            logging.info("ScalpingService initialized.")
        except Exception as e:
            logging.error(f"Failed to initialize ScalpingService: {e}")
            scalping_service = None

    # --- Database Setup (Billing) ---
    try:
        conn = sqlite3.connect("genxdb_fx.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY,
                cardholder_name TEXT,
                masked_card_number TEXT
            )
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT NOT NULL,
                balance REAL,
                equity REAL,
                total_profit REAL,
                total_loss REAL,
                pnl REAL,
                profit_factor REAL,
                currency TEXT DEFAULT 'USD',
                timestamp TEXT
            )
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                base_currency TEXT,
                quote_currency TEXT,
                is_active INTEGER DEFAULT 1
            )
            """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1
            )
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Failed to setup database: {e}")

    # --- Dashboard Cache Setup ---
    try:
        with open("monitoring_dashboard.html", "r") as f:
            MONITORING_DASHBOARD_CACHE = f.read()
        logging.info("Successfully cached monitoring_dashboard.html.")
    except FileNotFoundError:
        logging.error(
            "monitoring_dashboard.html not found. "
            "The /monitor endpoint will be disabled."
        )
        MONITORING_DASHBOARD_CACHE = "<h1>Error: Monitoring dashboard not found.</h1>"
    except Exception as e:
        logging.error(f"An error occurred while caching the dashboard: {e}")
        MONITORING_DASHBOARD_CACHE = (
            "<h1>Error: Could not load monitoring dashboard.</h1>"
        )

    yield

    # --- Shutdown Logic ---
    await api.redis.close_redis()


app = FastAPI(
    title="GenX-FX Trading Platform API",
    description="Trading platform with ML-powered predictions",
    version="1.0.0",
    lifespan=lifespan,
)

# Include Routers
app.include_router(performance.router, prefix="/api/v1")
app.include_router(market_data.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")
app.include_router(trading.router, prefix="/api/v1")


# --- Optimization: Define static root response as a constant ---
# To prevent the dictionary from being recreated on every call to the
# root endpoint, we define it once as a module-level constant. This is a
# micro-optimization that reduces a small amount of overhead for a
# frequently accessed endpoint (e.g., by health checkers).
ROOT_RESPONSE = {
    "message": "GenX-FX Trading Platform API",
    "version": "1.0.0",
    "status": "active",
    "docs": "/docs",
    "github": "Mouy-leng",
    "repository": "https://github.com/Mouy-leng/GenX_FX.git",
}

# Add Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0", "genx-fx.com", "testserver"],
)

# --------------------------------------------------------------------------
# Performance Optimization: Add GZip Compression Middleware
# --------------------------------------------------------------------------
# To reduce the size of the response bodies and improve network performance,
# we add GZipMiddleware. This middleware automatically compresses responses
# for clients that support gzip encoding, which is a standard feature in
# modern browsers and HTTP clients. A minimum size of 1000 bytes is set to
# avoid the overhead of compressing very small responses where compression
# might not be beneficial.
# --------------------------------------------------------------------------
app.add_middleware(GZipMiddleware, minimum_size=1000)


class PaymentMethod(BaseModel):
    """
    Pydantic model for payment method data with built-in validation.
    This model ensures that the data is well-formed before any business logic
    is executed, preventing unnecessary processing of invalid requests. This
    "fail-fast" approach improves API performance and robustness.
    """

    cardholderName: str
    cardNumber: str
    expiryDate: str
    cvc: str

    @field_validator("cardholderName")
    def validate_cardholder_name(cls, v):
        """Ensure cardholder name is not empty."""
        if not v.strip():
            raise ValueError("Cardholder name must not be empty.")
        return v

    @field_validator("cardNumber")
    def validate_card_number(cls, v):
        """Validate card number format (16 digits, optional separators)."""
        if not re.match(r"^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$", v):
            raise ValueError("Invalid card number format.")
        return v

    @field_validator("expiryDate")
    def validate_expiry_date(cls, v):
        """Validate expiry date format (MM/YY)."""
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", v):
            raise ValueError("Invalid expiry date format. Must be MM/YY.")
        return v

    @field_validator("cvc")
    def validate_cvc(cls, v):
        """Validate CVC format (3 or 4 digits)."""
        if not re.match(r"^\d{3,4}$", v):
            raise ValueError("Invalid CVC format. Must be 3 or 4 digits.")
        return v


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://genx-fx.com",
        "https://a-333-time-3-2--genxav69.replit.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Performance Optimization: Redis Cache for Monitoring Endpoint ---
# To avoid frequent and slow disk I/O on the monitoring endpoint, we use a
# Redis cache. This ensures that the cache is shared across all worker
# processes, which is not the case with a simple in-memory global variable.
# It also provides more robust caching with a configurable expiration time.
#
# The Redis connection details are retrieved from environment variables,
# with sensible defaults for local development.
# --------------------------------------------------------------------------
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
CACHE_DURATION_SECONDS = 5  # Cache metrics for 5 seconds

# --- Set up basic logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --------------------------------------------------------------------------
# Performance Optimization: In-Memory Cache for Static HTML
# --------------------------------------------------------------------------
# To avoid reading the same static HTML file from disk on every request,
# we cache its content in a global variable on application startup. This
# reduces disk I/O and improves the response time for the monitoring dashboard.
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Dependency Injection for Database Connection
# --------------------------------------------------------------------------
# To ensure thread safety with SQLite, we use FastAPI's dependency injection
# system to manage the database connection. A new connection is created for
# each request and closed when the request is complete. This is a safe and
# standard pattern for managing resources in a web application.
# --------------------------------------------------------------------------


def is_safe_string(input_string):
    """
    A simple function to check for potentially malicious characters.
    """
    # Reject strings with common SQL injection or XSS characters
    if re.search(r"[;\"'<>]", input_string):
        return False
    return True


@app.get("/")
async def root():
    """
    Root endpoint for the API.

    Provides basic information about the API, including its name, version,
    status, and repository URL.

    Returns:
        dict: A dictionary containing API information.
    """
    # --- Performance: Use Redis cache if available ---
    # This endpoint returns a static JSON response. Caching it reduces
    # processing time for frequent requests, such as from health checkers.
    redis_client = api.redis.redis_client

    if redis_client:
        try:
            cached_root = await redis_client.get("root_cache")
            if cached_root:
                return json.loads(cached_root)
        except Exception as e:
            logging.error(f"Redis connection error: {e}. Performing live query.")

    # --- Update Redis cache if available ---
    if redis_client:
        try:
            # Cache for 1 minute (60 seconds)
            await redis_client.setex("root_cache", 60, json.dumps(ROOT_RESPONSE))
        except Exception as e:
            logging.error(f"Could not write to Redis cache: {e}.")

    return ROOT_RESPONSE


@app.get("/health")
async def health_check(db: sqlite3.Connection = Depends(get_db)):
    """
    Performs a health check on the API and its database connection.

    Attempts to connect to the SQLite database and execute a simple query.
    This endpoint is optimized with a short-lived Redis cache to reduce
    database load from frequent health checks.

    Returns:
        dict: A dictionary indicating the health status. 'healthy' if the
              database connection is successful, 'unhealthy' otherwise.
    """
    # --- Performance: Use Redis cache if available ---
    redis_client = api.redis.redis_client

    if redis_client:
        try:
            cached_health = await redis_client.get("health_check_status")
            if cached_health:
                return json.loads(cached_health)
        except Exception as e:
            logging.error(f"Redis connection error: {e}. Performing live check.")

    try:
        # --- Use the DB connection from the dependency ---
        cursor = db.cursor()
        cursor.execute("SELECT 1")

        healthy_response = {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "services": {"ml_service": "active", "data_service": "active"},
        }

        # --- Update Redis cache if available ---
        if redis_client:
            try:
                await redis_client.setex(
                    "health_check_status", 10, json.dumps(healthy_response)
                )
            except Exception as e:
                logging.error(f"Could not write to Redis cache: {e}.")

        return healthy_response

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "services": {"ml_service": "inactive", "data_service": "inactive"},
        }


@app.get("/api/v1/health")
async def api_health_check():
    """
    Provides a health check for the v1 API services.

    Returns a hardcoded status indicating that the main services are active.

    Returns:
        dict: A dictionary with the health status of internal services.
    """
    return {
        "status": "healthy",
        "services": {"ml_service": "active", "data_service": "active"},
        "timestamp": datetime.now().isoformat(),
    }


def _create_prediction_dataframe(historical_data: list) -> pd.DataFrame:
    """
    Converts historical data to a pandas DataFrame and validates it.

    This is a CPU-bound operation that should be run in a separate thread
    to avoid blocking the asyncio event loop.
    """
    df = pd.DataFrame(historical_data)
    # Basic data validation
    required_columns = ["open", "high", "low", "close", "volume"]
    if not all(col in df.columns for col in required_columns):
        # Raise ValueError to be caught in the endpoint
        raise ValueError("Missing required columns in historical data.")
    return df


@app.post("/api/v1/predictions")
async def get_predictions(request: Request):
    """
    Endpoint to get trading predictions.

    Accepts a POST request with historical price data and returns a prediction.

    Returns:
        dict: A dictionary containing the prediction.
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # --- Performance Optimization: Fail-fast input validation ---
    # To avoid unnecessary processing for invalid requests, we immediately
    # check if the 'historical_data' is provided and is a list. If not,
    # we raise a 422 Unprocessable Entity error. This fail-fast approach
    # conserves server resources and provides clearer API feedback.
    if "historical_data" not in data or not isinstance(data["historical_data"], list):
        raise HTTPException(
            status_code=422, detail="'historical_data' is required and must be a list."
        )

    if predictor:
        try:
            if "historical_data" in data and isinstance(data["historical_data"], list):
                # --- Performance: Offload CPU-bound DataFrame creation to a thread ---
                # Creating a pandas DataFrame can be CPU-intensive for large datasets.
                # Running this in a separate thread prevents blocking the main asyncio
                # event loop, ensuring the server remains responsive.
                try:
                    df = await asyncio.to_thread(
                        _create_prediction_dataframe, data["historical_data"]
                    )
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))

                # --- Performance: Run CPU-bound prediction in a separate thread ---
                # The prediction model is CPU-intensive and would block the main
                # asyncio event loop. By using asyncio.to_thread, we run it in a
                # separate thread, allowing the server to remain responsive to
                # other requests.
                prediction = await asyncio.to_thread(predictor.predict, df)
                return prediction
            else:
                return {
                    "predictions": [],
                    "status": "ready (no data provided)",
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            logging.error(f"Prediction failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    else:
        return {
            "predictions": [],
            "status": "predictor not initialized",
            "timestamp": datetime.now().isoformat(),
        }


@app.post("/api/v1/scalping/signals")
async def get_scalping_signals(request: Request):
    """
    Endpoint to get scalping signals for 5m, 15m, and 30m timeframes.

    Accepts historical data and timeframe parameters.
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not scalping_service:
        return {
            "signal": "NEUTRAL",
            "status": "scalping service not initialized",
            "timestamp": datetime.now().isoformat(),
        }

    historical_data = data.get("historical_data")
    timeframe = data.get("timeframe", "5m")

    # Input validation
    if not historical_data or not isinstance(historical_data, list):
        raise HTTPException(
            status_code=422, detail="'historical_data' is required and must be a list."
        )

    if timeframe not in ["5m", "15m", "30m"]:
        raise HTTPException(
            status_code=422,
            detail="Invalid 'timeframe'. Must be '5m', '15m', or '30m'.",
        )

    try:
        # Offload DataFrame creation and analysis to a thread
        df = await asyncio.to_thread(_create_prediction_dataframe, historical_data)

        result = await asyncio.to_thread(
            scalping_service.analyze_strategy, df, timeframe
        )
        return result
    except Exception as e:
        logging.error(f"Scalping analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/trading-pairs")
async def get_trading_pairs(
    symbol: str | None = Query(default=None), db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves a list of active trading pairs from the database.

    This endpoint is optimized with a Redis cache to reduce database load, as
    the list of trading pairs does not change frequently. The cache expires
    every hour.

    If a symbol filter is provided, it performs a direct database query.

    Returns:
        dict: A dictionary containing a list of trading pairs or an error
              message.
    """
    # --- Performance: Use Redis cache if available and no filter ---
    redis_client = api.redis.redis_client

    if redis_client and not symbol:
        try:
            cached_pairs = await redis_client.get("trading_pairs_cache")
            if cached_pairs:
                return json.loads(cached_pairs)
        except Exception as e:
            logging.error(f"Redis connection error: {e}. Performing live query.")

    try:
        # --- Use the DB connection from the dependency ---
        cursor = db.cursor()

        if symbol:
            cursor.execute(
                "SELECT symbol, base_currency, quote_currency "
                "FROM trading_pairs WHERE is_active = 1 AND symbol = ?",
                (symbol,),
            )
        else:
            cursor.execute(
                "SELECT symbol, base_currency, quote_currency "
                "FROM trading_pairs WHERE is_active = 1"
            )

        pairs = cursor.fetchall()

        response = {
            "trading_pairs": [
                {
                    "symbol": pair["symbol"],
                    "base_currency": pair["base_currency"],
                    "quote_currency": pair["quote_currency"],
                }
                for pair in pairs
            ]
        }

        # --- Update Redis cache if available and no filter ---
        if redis_client and not symbol:
            try:
                # Cache for 1 hour (3600 seconds)
                await redis_client.setex(
                    "trading_pairs_cache", 3600, json.dumps(response)
                )
            except Exception as e:
                logging.error(f"Could not write to Redis cache: {e}.")

        return response
    except Exception as e:
        return {"error": str(e)}


@app.get("/users", deprecated=True)
async def get_users_deprecated(db: sqlite3.Connection = Depends(get_db)):
    """
    Retrieves a list of users from the database.

    **Deprecated:** This endpoint is not recommended for new use. Please use
    the paginated `/api/v2/users` endpoint instead.

    Connects to the SQLite database and fetches user information.

    Returns:
        dict: A dictionary containing a list of users or an error message.
    """
    # --- Performance Warning: This endpoint is not paginated ---
    try:
        # --- Use the DB connection from the dependency ---
        cursor = db.cursor()
        cursor.execute("SELECT username, email, is_active FROM users")
        users = cursor.fetchall()

        return {
            "users": [
                {
                    "username": user["username"],
                    "email": user["email"],
                    "is_active": bool(user["is_active"]),
                }
                for user in users
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/v2/users")
async def get_users(
    db: sqlite3.Connection = Depends(get_db), skip: int = 0, limit: int = 10
):
    """
    Retrieves a list of users from the database with pagination.

    Connects to the SQLite database and fetches user information.

    - **skip**: The number of records to skip (for pagination).
    - **limit**: The maximum number of records to return.

    Returns:
        dict: A dictionary containing a list of users or an error message.
    """
    # --- Performance: Add pagination ---
    try:
        # --- Use the DB connection from the dependency ---
        cursor = db.cursor()
        cursor.execute(
            "SELECT username, email, is_active FROM users LIMIT ? OFFSET ?",
            (limit, skip),
        )
        users = cursor.fetchall()

        return {
            "users": [
                {
                    "username": user["username"],
                    "email": user["email"],
                    "is_active": bool(user["is_active"]),
                }
                for user in users
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/mt5-info")
async def get_mt5_info():
    """
    Provides information about the MT5 connection.
    Updated for account 411534497 on Exness-MT5Real8.

    Returns:
        dict: A dictionary with MT5 login and server details.
    """
    # --- Performance: Use Redis cache for static data ---
    redis_client = api.redis.redis_client

    if redis_client:
        try:
            cached_info = await redis_client.get("mt5_info_cache_v2")
            if cached_info:
                return json.loads(cached_info)
        except Exception as e:
            logging.error(f"Redis connection error: {e}. Serving live data.")

    response = {
        "login": "411534497",
        "server": "Exness-MT5Real8",
        "status": "configured",
        "account_type": "real",
        "broker": "Exness",
    }

    # --- Update Redis cache if available ---
    if redis_client:
        try:
            # Cache for 1 hour (3600 seconds)
            await redis_client.setex("mt5_info_cache_v2", 3600, json.dumps(response))
        except Exception as e:
            logging.error(f"Could not write to Redis cache: {e}.")

    return response


@app.get("/api/v1/monitor")
async def get_monitoring_data():
    """
    Retrieves the latest system metrics directly from the Redis cache.

    This endpoint is optimized to serve metrics from an in-memory Redis cache,
    which is populated by the `system_monitor.py` service. This approach
    avoids any disk I/O in the API, making it highly performant.

    Returns:
        dict: A dictionary containing the latest system metrics, or an
              error message if the metrics are not available in the cache.
    """
    redis_client = api.redis.redis_client

    if not redis_client:
        return {"error": "Redis is not connected; monitoring data is unavailable."}

    try:
        cached_metrics = await redis_client.get("system_metrics")
        if cached_metrics:
            return json.loads(cached_metrics)
        else:
            return {"error": "Monitoring data not available yet."}
    except Exception as e:
        logging.error(f"Redis connection error: {e}")
        return {"error": "Could not connect to Redis for monitoring data."}


@app.get("/monitor")
async def serve_monitoring_dashboard():
    """
    Serves the monitoring dashboard HTML file from an in-memory cache.

    This endpoint is optimized to serve the dashboard from a global variable,
    reducing disk I/O and improving performance.

    Returns:
        HTMLResponse: The HTML content of the monitoring dashboard.
    """
    return HTMLResponse(content=MONITORING_DASHBOARD_CACHE)


@app.post("/api/v1/billing")
async def add_payment_method(
    payment_method: PaymentMethod, db: sqlite3.Connection = Depends(get_db)
):
    """
    Adds a new payment method to the database.

    Returns:
        dict: A dictionary with a success message.
    """
    # --- Performance Optimization ---
    # Using FastAPI's dependency injection for the DB connection avoids creating
    # a new connection on every request, improving performance and reliability.
    try:
        masked_card_number = f"**** **** **** {payment_method.cardNumber[-4:]}"
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO payment_methods (cardholder_name, masked_card_number) VALUES (?, ?)",
            (
                payment_method.cardholderName,
                masked_card_number,
            ),
        )
        db.commit()
        return {"status": "success", "message": "Payment method added successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/v1/data")
async def handle_data(data: dict):
    """
    Handles incoming data POST requests.

    This endpoint is designed to gracefully handle various data formats
    and return a consistent success response. It's used for testing
    edge cases and data validation.

    Args:
        data (dict): The incoming data payload.

    Returns:
        dict: A success message.
    """
    # In a real application, you would process the data here
    return {"status": "success", "data_received": data}


# Serve the frontend (Place this after all API routes)
if os.path.exists("client/dist"):
    app.mount("/", StaticFiles(directory="client/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
