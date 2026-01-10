import pytest
import asyncio
from unittest.mock import Mock, patch
import os
import sys
import sqlite3

# Skip tests if FastAPI is not available
try:
    from fastapi.testclient import TestClient
    from api.main import app
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    # Set test environment variables
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
    os.environ["REDIS_URL"] = "redis://localhost:6379"

@pytest.fixture
def client():
    """
    ⚡ Bolt: Create a test client with an in-memory SQLite database.
    This fixture ensures that tests run against a clean, isolated database.
    We use a mock connection and cursor to allow for call assertions.
    """
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not installed, skipping API tests.")

    real_conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = real_conn.cursor()
    cursor.execute("""
    CREATE TABLE trading_pairs (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        base_currency TEXT NOT NULL,
        quote_currency TEXT NOT NULL,
        is_active INTEGER NOT NULL
    )
    """)
    cursor.execute("""
    INSERT INTO trading_pairs (symbol, base_currency, quote_currency, is_active)
    VALUES ('EURUSD', 'EUR', 'USD', 1),
           ('GBPUSD', 'GBP', 'USD', 1)
    """)
    real_conn.commit()

    # Create a mock cursor that wraps a real cursor, allowing assertions
    mock_cursor = Mock(wraps=real_conn.cursor())

    # Create a mock connection that wraps the real one
    mock_conn = Mock(wraps=real_conn)
    # Configure the mock connection's cursor() method to return our mock_cursor
    mock_conn.cursor.return_value = mock_cursor

    with patch("sqlite3.connect", return_value=mock_conn):
        with TestClient(app) as c:
            yield c

    real_conn.close()

@pytest.fixture
def mock_auth():
    """Mock authentication"""
    with patch('api.utils.auth.get_current_user') as mock_user:
        mock_user.return_value = {"username": "testuser"}
        yield mock_user

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_endpoint(client):
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
    assert "signal" in prediction
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
    data = pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 103, 104, 105, 106],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })
    
    indicators = TechnicalIndicators()
    result = indicators.add_all_indicators(data)
    
    # Check that indicators were added
    assert 'rsi' in result.columns
    assert 'macd' in result.columns
    assert 'sma_20' in result.columns

def test_pattern_detector():
    """Test pattern detector"""
    import pandas as pd
    from core.patterns import PatternDetector
    
    # Create sample data
    data = pd.DataFrame({
        'open': [100, 102, 101, 103, 102],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 101, 105, 104, 107],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })
    
    detector = PatternDetector()
    patterns = detector.detect_patterns(data)
    
    # Check that patterns were detected
    assert 'bullish_engulfing' in patterns
    assert 'bearish_engulfing' in patterns
    assert 'doji' in patterns

def test_config_loading():
    """Test config loading"""
    from utils.config import load_config
    
    config = load_config("non_existent_file.json")
    assert isinstance(config, dict)
    assert "database_url" in config
    assert "symbols" in config

def test_trading_pairs_cache(client):
    """
    ⚡ Bolt: Test that the trading_pairs endpoint is cached by ensuring the
    database is only queried on the first request.
    """
    from api.utils import cache
    cache.clear()

    mock_conn = app.state.db_conn
    mock_cursor = mock_conn.cursor.return_value

    # First request should trigger a database query
    response1 = client.get("/trading-pairs")
    assert response1.status_code == 200
    assert "trading_pairs" in response1.json()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()

    # Reset mocks
    mock_conn.cursor.reset_mock()
    mock_cursor.execute.reset_mock()

    # Second request should be served from the cache
    response2 = client.get("/trading-pairs")
    assert response2.status_code == 200
    assert response1.json() == response2.json()
    mock_conn.cursor.assert_not_called()
    mock_cursor.execute.assert_not_called()
