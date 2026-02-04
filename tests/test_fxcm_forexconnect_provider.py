from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest

import core.data_sources.fxcm_forexconnect_provider as provider_module

# Create a mock for the 'fx' module and add it to the provider module
# so that the test can find it.
mock_fx = MagicMock()
provider_module.fx = mock_fx

from core.data_sources.fxcm_forexconnect_provider import (
    FXCMForexConnectConfig,
    FXCMForexConnectProvider,
)


@pytest.mark.asyncio
@patch("core.data_sources.fxcm_forexconnect_provider.FOREXCONNECT_AVAILABLE", True)
@patch("core.data_sources.fxcm_forexconnect_provider.aiohttp.ClientSession")
async def test_find_best_server(mock_session):
    # Mock the latency measurements
    async def mock_measure_latency(session, url):
        if "fxcorporate" in url:
            return 0.1
        elif "fxcm.com" in url:
            return 0.2
        else:
            return float("inf")

    # Configure the mock session
    mock_session.get.return_value.__aenter__.return_value.text = AsyncMock()

    # Create an instance of the provider
    config = {
        "username": "testuser",
        "password": "testpassword",
        "connection_type": "Demo",
        "auto_select_server": True,
    }
    provider = FXCMForexConnectProvider(config)
    provider._measure_latency = AsyncMock(side_effect=mock_measure_latency)

    # Run the test
    best_server = await provider.find_best_server()
    assert best_server == "http://www.fxcorporate.com/Hosts.jsp"


@pytest.mark.asyncio
@patch("core.data_sources.fxcm_forexconnect_provider.FOREXCONNECT_AVAILABLE", True)
async def test_connect_with_auto_select():
    # Mock the ForexConnect login

    # Create an instance of the provider
    config = {
        "username": "testuser",
        "password": "testpassword",
        "connection_type": "Demo",
        "auto_select_server": True,
    }
    provider = FXCMForexConnectProvider(config)

    # Mock the find_best_server method
    provider.find_best_server = AsyncMock(return_value="https://best.server.com")

    # Run the test
    await provider.connect()

    # Check that login was called with the best server
    provider.forex_connect.login.assert_called_with(
        user_id="testuser",
        password="testpassword",
        url="https://best.server.com",
        connection="Demo",
        session_id=None,
        pin=None,
    )
