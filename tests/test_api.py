import pytest
import asyncio
from unittest.mock import Mock, patch
import os
import sys

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
    """Create a test client that respects the lifespan context manager."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not installed, skipping API tests.")
    with TestClient(app) as c:
        yield c

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

def test_trading_pairs_caching(client):
    """
    ⚡ Bolt: Verify that the /trading-pairs endpoint caches results.
    This test ensures that the database is only hit on the first request.
    Subsequent requests within the cache timeout should return cached data.
    """
    # ⚡ Bolt: Clear the cache to ensure test isolation.
    from api.utils.cache import cache
    cache.clear()

    # ⚡ Bolt: Mock the cursor on the actual connection object used by the app.
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        ('BTC/USD', 'BTC', 'USD'),
        ('ETH/USD', 'ETH', 'USD'),
    ]

    with patch.object(client.app.state, 'db_conn') as mock_db_conn:
        mock_db_conn.cursor.return_value = mock_cursor

        # First call should hit the database
        response1 = client.get("/trading-pairs")
        assert response1.status_code == 200
        assert len(response1.json()["trading_pairs"]) == 2
        mock_db_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()

        # Second call should be cached
        response2 = client.get("/trading-pairs")
        assert response2.status_code == 200
        assert len(response2.json()["trading_pairs"]) == 2
        # The cursor and execute methods should NOT be called again
        mock_db_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()


from unittest.mock import AsyncMock


@pytest.mark.asyncio
@patch("api.main.get_trading_pairs", new_callable=AsyncMock)
@patch("api.services.ml_service.MLService.batch_predict", new_callable=AsyncMock)
@patch(
    "api.services.data_service.DataService.get_batch_realtime_data",
    new_callable=AsyncMock,
)
async def test_get_predictions_endpoint_optimized(
    mock_get_batch_data, mock_batch_predict, mock_get_trading_pairs, client
):
    """⚡ Bolt: Test that the get_predictions endpoint uses batch operations."""
    # Arrange
    mock_get_trading_pairs.return_value = {
        "trading_pairs": [
            {"symbol": "EUR/USD", "base_currency": "EUR", "quote_currency": "USD"},
            {"symbol": "GBP/USD", "base_currency": "GBP", "quote_currency": "USD"},
        ]
    }
    mock_get_batch_data.return_value = {
        "EUR/USD": {"feature": 1},
        "GBP/USD": {"feature": 2},
    }
    mock_batch_predict.return_value = {
        "EUR/USD": {"signal": "buy", "confidence": 0.9},
        "GBP/USD": {"signal": "sell", "confidence": 0.8},
    }

    # Act
    response = client.get("/api/v1/predictions")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["predictions"]) == 2
    assert data["predictions"][0]["symbol"] == "EUR/USD"
    assert data["predictions"][0]["signal"] == "buy"
    assert data["predictions"][1]["symbol"] == "GBP/USD"
    assert data["predictions"][1]["signal"] == "sell"
