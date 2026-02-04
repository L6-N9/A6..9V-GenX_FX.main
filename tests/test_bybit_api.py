import os

import pytest

# Skip tests if dependencies are not available
try:
    from unittest.mock import Mock, patch

    from core.execution.bybit import BybitAPI

    BYBIT_AVAILABLE = True
except ImportError:
    BYBIT_AVAILABLE = False


@pytest.fixture
def bybit_api():
    """
    Pytest fixture to mock the pybit HTTP session.
    This prevents real API calls during tests.
    """
    if not BYBIT_AVAILABLE:
        pytest.skip("BybitAPI not available")

    # Mock environment variables
    with patch.dict(
        os.environ, {"BYBIT_API_KEY": "test_key", "BYBIT_API_SECRET": "test_secret"}
    ):
        # Mock the HTTP class from pybit.unified_trading
        mock_session = Mock()
        mock_instance = Mock()
        mock_instance.get_kline = Mock()
        mock_session.return_value = mock_instance

        with patch("pybit.unified_trading.HTTP", return_value=mock_instance):
            # Instantiate BybitAPI, which will now use the mocked session
            api = BybitAPI()
            # Attach the mock to the instance for easy access in tests
            api.session = mock_instance
            return api


@pytest.mark.skipif(not BYBIT_AVAILABLE, reason="BybitAPI not available")
def test_get_market_data_success(bybit_api):
    """
    Tests the get_market_data method for a successful API call.
    """
    # Arrange: Set up the mock response
    mock_response = {"retCode": 0, "result": {"list": [1, 2, 3]}}
    bybit_api.session.get_kline.return_value = mock_response

    # Act: Call the method
    result = bybit_api.get_market_data("BTCUSDT", "60")

    # Assert: Check that the mock was called correctly and the result is as expected
    bybit_api.session.get_kline.assert_called_once_with(
        category="spot", symbol="BTCUSDT", interval="60", limit=200
    )
    assert result == mock_response
