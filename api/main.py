from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import asyncio

# ⚡ Bolt: Add a thread-safe in-memory cache.
# This will store frequently accessed data that doesn't change often.
cache = {}
CACHE_TIMEOUT = timedelta(seconds=60)
cache_lock = asyncio.Lock()

# ⚡ Bolt: Create a single, reusable database connection to improve performance.
# By creating the connection when the app starts and closing it when it stops,
# we avoid the overhead of connecting to the database on every single request.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database
    app.state.db_conn = sqlite3.connect("genxdb_fx.db", check_same_thread=False)
    yield
    # Close the connection
    app.state.db_conn.close()

app = FastAPI(
    title="GenX-FX Trading Platform API",
    description="Trading platform with ML-powered predictions",
    version="1.0.0",
    lifespan=lifespan
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
async def root():
    """
    Root endpoint for the API.

    Provides basic information about the API, including its name, version,
    status, and repository URL.

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

@app.get("/api/v1/predictions")
async def get_predictions():
    """
    Endpoint to get trading predictions.

    Currently returns a placeholder response.

    Returns:
        dict: A dictionary containing an empty list of predictions.
    """
    return {
        "predictions": [],
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/trading-pairs")
async def get_trading_pairs(request: Request):
    """
    Retrieves a list of active trading pairs from the database.

    Connects to the SQLite database and fetches all pairs marked as active.

    ⚡ Bolt: To improve performance, the results of this query are cached in-memory
    for 60 seconds. This reduces database load and speeds up subsequent requests.

    Returns:
        dict: A dictionary containing a list of trading pairs or an error message.
    """
    now = datetime.now()
    cache_entry = cache.get("trading_pairs")

    if cache_entry and (now - cache_entry["timestamp"]) < CACHE_TIMEOUT:
        return cache_entry["data"]

    # ⚡ Bolt: Use a lock to prevent race conditions when updating the cache.
    async with cache_lock:
        # ⚡ Bolt: Double-check the cache in case it was populated while waiting for the lock.
        cache_entry = cache.get("trading_pairs")
        if cache_entry and (now - cache_entry["timestamp"]) < CACHE_TIMEOUT:
            return cache_entry["data"]

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

            # ⚡ Bolt: Update the cache.
            cache["trading_pairs"] = {"timestamp": now, "data": response_data}
            return response_data
        except Exception as e:
            return {"error": str(e)}

@app.get("/users")
async def get_users(request: Request):
    """
    Retrieves a list of users from the database.

    Connects to the SQLite database and fetches user information.

    ⚡ Bolt: To improve performance, the results of this query are cached in-memory
    for 60 seconds. This reduces database load and speeds up subsequent requests.

    Returns:
        dict: A dictionary containing a list of users or an error message.
    """
    now = datetime.now()
    cache_entry = cache.get("users")

    if cache_entry and (now - cache_entry["timestamp"]) < CACHE_TIMEOUT:
        return cache_entry["data"]

    # ⚡ Bolt: Use a lock to prevent race conditions when updating the cache.
    async with cache_lock:
        # ⚡ Bolt: Double-check the cache in case it was populated while waiting for the lock.
        cache_entry = cache.get("users")
        if cache_entry and (now - cache_entry["timestamp"]) < CACHE_TIMEOUT:
            return cache_entry["data"]

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

            # ⚡ Bolt: Update the cache.
            cache["users"] = {"timestamp": now, "data": response_data}
            return response_data
        except Exception as e:
            return {"error": str(e)}

@app.get("/mt5-info")
async def get_mt5_info():
    """
    Provides hardcoded information about the MT5 connection.

    Returns:
        dict: A dictionary with static MT5 login and server details.
    """
    return {"login": "279023502", "server": "Exness-MT5Trial8", "status": "configured"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
