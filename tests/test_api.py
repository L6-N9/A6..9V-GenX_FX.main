import asyncio
import json
import os
import sqlite3
from unittest.mock import MagicMock, Mock, patch

import pytest

# Skip tests if FastAPI is not available
try:
    from fastapi.testclient import TestClient

    from api.main import app, get_db

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    # Set test environment variables
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
    os.environ["REDIS_URL"] = "redis://localhost:6379"

    client = TestClient(app)
else:
    client = None


@pytest.fixture
def mock_auth():
    """Mock authentication"""
    with patch("api.utils.auth.get_current_user") as mock_user:
        mock_user.return_value = {"username": "testuser"}
        yield mock_user


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


@pytest.mark.asyncio
async def test_ml_service():
    """Test ML service"""
    from api.services.ml_service import MLService

    service = MLService()
    await service.initialize()

    # Test prediction
    prediction = await service.predict("BTCUSDT", {})
    assert "prediction" in prediction
    assert "confidence" in prediction

    # Test health check
    health = await service.health_check()
    assert health == "healthy"

    await service.shutdown()


@pytest.mark.asyncio
async def test_data_service():
    """Test data service"""
    from api.services.data_service import DataService

    service = DataService()
    await service.initialize()

    # Test get data
    data = await service.get_realtime_data("BTCUSDT")
    assert data is not None

    # Test health check
    health = await service.health_check()
    assert health == "healthy"

    await service.shutdown()


def test_technical_indicators():
    """Test technical indicators"""
    import pandas as pd

    from core.indicators import TechnicalIndicators

    # Create sample data
    data = pd.DataFrame(
        {
            "open": [100, 101, 102, 103, 104],
            "high": [105, 106, 107, 108, 109],
            "low": [95, 96, 97, 98, 99],
            "close": [102, 103, 104, 105, 106],
            "volume": [1000, 1100, 1200, 1300, 1400],
        }
    )

    indicators = TechnicalIndicators()
    result = indicators.add_all_indicators(data)

    # Check that indicators were added
    assert "rsi" in result.columns
    assert "macd" in result.columns
    assert "sma_20" in result.columns


def test_pattern_detector():
    """Test pattern detector"""
    import pandas as pd

    from core.patterns import PatternDetector

    # Create sample data
    data = pd.DataFrame(
        {
            "open": [100, 102, 101, 103, 102],
            "high": [105, 106, 107, 108, 109],
            "low": [95, 96, 97, 98, 99],
            "close": [102, 101, 105, 104, 107],
            "volume": [1000, 1100, 1200, 1300, 1400],
        }
    )

    detector = PatternDetector()
    patterns = detector.detect_patterns(data)

    # Check that patterns were detected
    assert "bullish_engulfing" in patterns
    assert "bearish_engulfing" in patterns
    assert "doji" in patterns


def test_config_loading():
    """Test config loading"""
    from utils.config import load_config

    config = load_config("non_existent_file.json")
    assert isinstance(config, dict)
    assert "database_url" in config
    assert "symbols" in config


def test_v2_users_pagination():
    """Test pagination for the /api/v2/users endpoint"""
    # Create an in-memory SQLite database for this test
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        is_active INTEGER NOT NULL
    );
    """)
    # Insert 20 users
    for i in range(20):
        cursor.execute(
            "INSERT INTO users (username, email, is_active) VALUES (?, ?, ?)",
            (f"user{i+1}", f"user{i+1}@test.com", 1),
        )
    conn.commit()

    def get_test_db():
        yield conn

    # Override the dependency
    app.dependency_overrides[get_db] = get_test_db

    # Test with default limit
    response = client.get("/api/v2/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 10
    assert data["users"][0]["username"] == "user1"

    # Test with custom limit
    response = client.get("/api/v2/users?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 5

    # Test with skip and limit
    response = client.get("/api/v2/users?skip=10&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 5
    assert data["users"][0]["username"] == "user11"

    # Clean up the dependency override
    app.dependency_overrides.clear()
    conn.close()


from unittest.mock import AsyncMock


@pytest.mark.asyncio
@patch("sqlite3.connect")
async def test_trading_pairs_caching(mock_sqlite_connect):
    """
    Test that the /trading-pairs endpoint correctly uses in-memory caching.
    """
    # 1. Setup Mock
    mock_db_cursor = MagicMock()
    mock_db_cursor.fetchall.return_value = [
        {"symbol": "EURUSD", "base_currency": "EUR", "quote_currency": "USD"}
    ]

    mock_db_conn = MagicMock()
    mock_sqlite_connect.return_value = mock_db_conn
    mock_db_conn.cursor.return_value = mock_db_cursor

    # 2. First Request (Cache Miss)
    response = client.get("/trading-pairs")

    # 3. Assertions for First Request
    assert response.status_code == 200
    expected_data = {
        "trading_pairs": [
            {"symbol": "EURUSD", "base_currency": "EUR", "quote_currency": "USD"}
        ]
    }
    assert response.json() == expected_data
    # Expected call count: 1 from get_db + 1 from _get_all_trading_pairs_cached
    assert mock_sqlite_connect.call_count == 2

    # Reset mock to verify subsequent calls
    mock_sqlite_connect.reset_mock()

    # 4. Second Request (Cache Hit)
    response = client.get("/trading-pairs")

    # 5. Assertions for Second Request
    assert response.status_code == 200
    assert response.json() == expected_data
    # Expected call count: 1 from get_db (dependency) but 0 from _get_all_trading_pairs_cached (hit cache)
    assert mock_sqlite_connect.call_count == 1
