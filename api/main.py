from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncio
from .utils.cache import async_cache
from .services.data_service import DataService
from .services.ml_service import MLService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """⚡ Bolt: Manage the lifecycle of services and database connections."""
    # Initialize services
    app.state.data_service = DataService()
    app.state.ml_service = MLService()
    await app.state.data_service.initialize()
    await app.state.ml_service.initialize()

    # Connect to the database
    app.state.db_conn = sqlite3.connect("genxdb_fx.db", check_same_thread=False)

    yield

    # Shutdown services and close connections
    await app.state.data_service.shutdown()
    await app.state.ml_service.shutdown()
    app.state.db_conn.close()


app = FastAPI(
    title="GenX-FX Trading Platform API",
    description="Trading platform with ML-powered predictions",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚡ Bolt: Add GZip compression to reduce response sizes and improve network speed.
# This middleware will automatically compress responses for clients that support it.
# We set a minimum size of 1000 bytes to avoid compressing small responses
# where the overhead of compression might outweigh the benefits.
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/")
@async_cache(ttl=timedelta(seconds=60))
async def root():
    """
    Root endpoint for the API.

    Provides basic information about the API, including its name, version,
    status, and repository URL.

    ⚡ Bolt: This response is static, so we cache it for 60 seconds
    to reduce server load from frequent polling (e.g., health checks).

    Returns:
        dict: A dictionary containing API information.
    """
    return {
        "message": "GenX-FX Trading Platform API",
        "version": "1.0.0",
        "status": "running",
        "github": "Mouy-leng",
        "repository": "https://github.com/Mouy-leng/GenX_FX.git",
    }

@app.get("/health")
async def health_check(request: Request):
    """
    Performs a health check on the API and its database connection.

    Attempts to connect to the SQLite database and execute a simple query.

    Returns:
        dict: A dictionary indicating the health status. 'healthy' if the
              database connection is successful, 'unhealthy' otherwise.
    """
    try:
        # ⚡ Bolt: Use the shared database connection for health check.
        cursor = request.app.state.db_conn.cursor()
        cursor.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

@app.get("/api/v1/health")
@async_cache(ttl=timedelta(seconds=60))
async def api_health_check():
    """
    Provides a health check for the v1 API services.

    Returns a hardcoded status indicating that the main services are active.

    ⚡ Bolt: This static health check is a prime candidate for caching.
    Caching for 60 seconds prevents excessive processing from frequent
    checks by monitoring services.

    Returns:
        dict: A dictionary with the health status of internal services.
    """
    return {
        "status": "healthy",
        "services": {"ml_service": "active", "data_service": "active"},
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/api/v1/predictions")
async def get_predictions(request: Request):
    """
    ⚡ Bolt: Generate and return trading predictions using batch operations.
    This optimized endpoint fetches all trading pairs, gets their market data in a
    single batch, and then generates predictions for all symbols in another batch.
    This avoids the N+1 problem and significantly improves performance.
    """
    try:
        # Step 1: Get all active trading pairs.
        pairs_response = await get_trading_pairs(request)
        if "error" in pairs_response:
            return {
                "error": pairs_response["error"],
                "status": "error",
                "timestamp": datetime.now().isoformat(),
            }

        symbols = [pair["symbol"] for pair in pairs_response["trading_pairs"]]
        if not symbols:
            return {
                "predictions": [],
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            }

        # Step 2: Fetch market data for all symbols in a single batch.
        data_service: DataService = request.app.state.data_service
        market_data_batch = await data_service.get_batch_realtime_data(symbols)

        # Step 3: Get predictions for all symbols in a single batch.
        ml_service: MLService = request.app.state.ml_service
        predictions_batch = await ml_service.batch_predict(market_data_batch)

        # Step 4: Format the response.
        response_data = [
            {"symbol": symbol, **prediction}
            for symbol, prediction in predictions_batch.items()
        ]

        return {
            "predictions": response_data,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat(),
        }

@app.get("/trading-pairs")
@async_cache(ttl=timedelta(seconds=60))
async def get_trading_pairs(request: Request):
    """
    Retrieves a list of active trading pairs from the database.

    Connects to the SQLite database and fetches all pairs marked as active.

    ⚡ Bolt: To improve performance, the results of this query are cached in-memory
    for 60 seconds using a reusable decorator. This reduces database load and
    speeds up subsequent requests.

    Returns:
        dict: A dictionary containing a list of trading pairs or an error message.
    """
    try:
        # ⚡ Bolt: Use the shared database connection.
        cursor = request.app.state.db_conn.cursor()
        cursor.execute(
            "SELECT symbol, base_currency, quote_currency FROM trading_pairs WHERE is_active = 1"
        )
        pairs = cursor.fetchall()

        response_data = {
            "trading_pairs": [
                {
                    "symbol": pair[0],
                    "base_currency": pair[1],
                    "quote_currency": pair[2],
                }
                for pair in pairs
            ]
        }
        return response_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/users")
@async_cache(ttl=timedelta(seconds=60))
async def get_users(request: Request):
    """
    Retrieves a list of users from the database.

    Connects to the SQLite database and fetches user information.

    ⚡ Bolt: To improve performance, the results of this query are cached in-memory
    for 60 seconds using a reusable decorator. This reduces database load and
    speeds up subsequent requests.

    Returns:
        dict: A dictionary containing a list of users or an error message.
    """
    try:
        # ⚡ Bolt: Use the shared database connection.
        cursor = request.app.state.db_conn.cursor()
        cursor.execute("SELECT username, email, is_active FROM users")
        users = cursor.fetchall()

        response_data = {
            "users": [
                {"username": user[0], "email": user[1], "is_active": bool(user[2])}
                for user in users
            ]
        }
        return response_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/mt5-info")
@async_cache(ttl=timedelta(seconds=60))
async def get_mt5_info():
    """
    Provides hardcoded information about the MT5 connection.

    ⚡ Bolt: The MT5 connection info is static. Caching this response for
    60 seconds avoids unnecessary processing for a fixed-data endpoint.

    Returns:
        dict: A dictionary with static MT5 login and server details.
    """
    return {"login": "279023502", "server": "Exness-MT5Trial8", "status": "configured"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
