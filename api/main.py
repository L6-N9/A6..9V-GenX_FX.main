from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
from datetime import datetime
from contextlib import asynccontextmanager

# ⚡ Bolt: Lifespan manager for a shared database connection.
# This creates a single SQLite connection when the app starts and closes it
# when the app shuts down. Reusing the connection is more performant than
# creating a new one for every single request.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # `check_same_thread=False` is required for SQLite when used in a multi-threaded
    # environment like FastAPI.
    conn = sqlite3.connect("genxdb_fx.db", check_same_thread=False)
    app.state.db_conn = conn
    yield
    conn.close()

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
        # ⚡ Bolt: Reuse the shared database connection from the app state.
        conn = request.app.state.db_conn
        cursor = conn.cursor()
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

    Returns:
        dict: A dictionary containing a list of trading pairs or an error message.
    """
    try:
        # ⚡ Bolt: Reuse the shared database connection from the app state.
        conn = request.app.state.db_conn
        cursor = conn.cursor()
        cursor.execute(
            "SELECT symbol, base_currency, quote_currency FROM trading_pairs WHERE is_active = 1"
        )
        pairs = cursor.fetchall()

        return {
            "trading_pairs": [
                {
                    "symbol": pair[0],
                    "base_currency": pair[1],
                    "quote_currency": pair[2],
                }
                for pair in pairs
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/users")
async def get_users(request: Request):
    """
    Retrieves a list of users from the database.

    Connects to the SQLite database and fetches user information.

    Returns:
        dict: A dictionary containing a list of users or an error message.
    """
    try:
        # ⚡ Bolt: Reuse the shared database connection from the app state.
        conn = request.app.state.db_conn
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, is_active FROM users")
        users = cursor.fetchall()

        return {
            "users": [
                {"username": user[0], "email": user[1], "is_active": bool(user[2])}
                for user in users
            ]
        }
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
