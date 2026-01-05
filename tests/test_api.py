import pytest
from contextlib import ExitStack
from unittest.mock import patch
import os

# Skip tests if FastAPI is not available
try:
    from fastapi.testclient import TestClient
    from api.main import app, lifespan
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    # Set test environment variables
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
    os.environ["REDIS_URL"] = "redis://localhost:6379"

@pytest.fixture(scope="module")
def client():
    """
    Create a test client that respects the application's lifespan.
    This ensures the database connection is created for the tests.
    """
    with ExitStack():
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
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

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
    from typing import Dict
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
