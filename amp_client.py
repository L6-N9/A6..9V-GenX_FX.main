#!/usr/bin/env python3
"""
AMP Client - Simple client to communicate with AMP services
"""

import json
from typing import Any, Dict, Optional

import requests

from amp_auth import check_auth, get_auth_headers


class AMPClient:
    """
    A simple client for communicating with AMP (Automated Model Pipeline) services.

    This client handles making authenticated requests to the AMP API endpoints.

    Attributes:
        base_url (str): The base URL of the AMP API.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initializes the AMPClient.

        Args:
            base_url (str): The base URL for the AMP API.
        """
        self.base_url = base_url

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Makes an authenticated request to a specified API endpoint.

        Args:
            method (str): The HTTP method to use (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint path.
            data (Optional[Dict]): The JSON payload for POST or PUT requests.

        Returns:
            Dict[str, Any]: The JSON response from the API as a dictionary.
        """
        if not check_auth():
            return {
                "error": "Not authenticated. Please run: python3 amp_cli.py auth --token YOUR_TOKEN"
            }

        headers = get_auth_headers()
        headers["Content-Type"] = "application/json"

        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {"error": f"Unsupported method: {method}"}

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Request failed with status {response.status_code}",
                    "message": response.text,
                }

        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to AMP API. Is the service running?"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def health(self) -> Dict[str, Any]:
        """Checks the health of the API."""
        return self._make_request("GET", "/health")

    def get_system_status(self) -> Dict[str, Any]:
        """Gets the overall system status."""
        return self._make_request("GET", "/api/v1/system/status")

    def get_predictions(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Gets market predictions for a specific symbol.

        Args:
            symbol (str): The trading symbol.

        Returns:
            Dict[str, Any]: The prediction data.
        """
        return self._make_request("GET", f"/api/v1/predictions/{symbol}")

    def get_market_data(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Gets market data for a specific symbol.

        Args:
            symbol (str): The trading symbol.

        Returns:
            Dict[str, Any]: The market data.
        """
        return self._make_request("GET", f"/api/v1/market-data/{symbol}")

    def chat(self, message: str) -> Dict[str, Any]:
        """
        Sends a chat message to the AMP chat endpoint.

        Args:
            message (str): The message to send.

        Returns:
            Dict[str, Any]: The chat response.
        """
        data = {"message": message, "user_id": "cli_user"}
        return self._make_request("POST", "/api/v1/chat", data)

    def get_trading_signals(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Gets trading signals for a specific symbol.

        Args:
            symbol (str): The trading symbol.

        Returns:
            Dict[str, Any]: The trading signal data.
        """
        return self._make_request("GET", f"/api/v1/trading/signals/{symbol}")


def main():
    """
    Runs an interactive command-line client for the AMP API.
    """
    client = AMPClient()

    print("🤖 AMP Client - Interactive Mode")
    print("================================")

    # Check authentication
    if not check_auth():
        print(
            "❌ Not authenticated. Please run: python3 amp_cli.py auth --token YOUR_TOKEN"
        )
        return

    print("✅ Authenticated successfully!")

    # Check API health
    health = client.health()
    if "error" in health:
        print(f"❌ API Health Check Failed: {health['error']}")
        return

    print("✅ API is healthy!")

    while True:
        print("\nAvailable commands:")
        print("1. health - Check API health")
        print("2. status - Get system status")
        print("3. predictions <symbol> - Get predictions (default: BTCUSDT)")
        print("4. market <symbol> - Get market data (default: BTCUSDT)")
        print("5. signals <symbol> - Get trading signals (default: BTCUSDT)")
        print("6. chat <message> - Send a chat message")
        print("7. quit - Exit")

        command = input("\nEnter command: ").strip()

        if command == "quit":
            break
        elif command == "health":
            result = client.health()
        elif command == "status":
            result = client.get_system_status()
        elif command.startswith("predictions"):
            parts = command.split()
            symbol = parts[1] if len(parts) > 1 else "BTCUSDT"
            result = client.get_predictions(symbol)
        elif command.startswith("market"):
            parts = command.split()
            symbol = parts[1] if len(parts) > 1 else "BTCUSDT"
            result = client.get_market_data(symbol)
        elif command.startswith("signals"):
            parts = command.split()
            symbol = parts[1] if len(parts) > 1 else "BTCUSDT"
            result = client.get_trading_signals(symbol)
        elif command.startswith("chat"):
            message = command[5:].strip()  # Remove "chat " prefix
            if message:
                result = client.chat(message)
            else:
                print("❌ Please provide a message after 'chat'")
                continue
        else:
            print("❌ Unknown command")
            continue

        print(f"\nResponse:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
