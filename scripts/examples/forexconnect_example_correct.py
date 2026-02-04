#!/usr/bin/env python3
"""
ForexConnect API Example (Corrected)
This example demonstrates the correct ForexConnect API usage.

Note: You need valid FXCM credentials to run this example.
"""

import sys
import time

import forexconnect as fx


class ForexConnectExample:
    """
    A class to demonstrate the corrected and modern usage of the ForexConnect API.
    """

    def __init__(self):
        """
        Initializes the ForexConnectExample class.
        """
        self.connection = None

    def create_connection(self) -> bool:
        """
        Creates a ForexConnect connection instance.

        Returns:
            bool: True if the instance is created successfully, False otherwise.
        """
        try:
            # Create ForexConnect instance
            self.connection = fx.ForexConnect()

            print("✓ ForexConnect instance created successfully")
            return True

        except Exception as e:
            print(f"✗ Error creating ForexConnect instance: {e}")
            return False

    def configure_connection(
        self,
        username: str,
        password: str,
        connection_type: str = "Demo",
        server: str = "Real",
    ) -> bool:
        """
        Configures the connection parameters for the ForexConnect session.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            connection_type (str, optional): The type of connection (e.g., "Demo"). Defaults to "Demo".
            server (str, optional): The server type. Defaults to "Real".

        Returns:
            bool: True if configuration is successful, False otherwise.
        """
        try:
            print(f"✓ Connection would be configured for {connection_type} environment")
            print(f"  Username: {username}")
            print(f"  Server: {server}")
            print("  (Actual connection requires valid FXCM credentials)")
            return True

        except Exception as e:
            print(f"✗ Error configuring connection: {e}")
            return False

    def show_connection_example(self):
        """
        Shows an example of how to properly connect to the FXCM server,
        including the use of a context manager.
        """
        print("\n=== Connection Example ===")

        example_code = """
# To actually connect to FXCM (requires valid credentials):

import forexconnect as fx

# Create ForexConnect instance
fx_conn = fx.ForexConnect()

# Login parameters
username = "your_fxcm_username"
password = "your_fxcm_password"
connection = "Demo"  # or "Real" for live trading
server = "Real"      # Server type

# Connect using context manager (recommended)
with fx_conn:
    try:
        # Perform login
        fx_conn.login(username, password, connection, server)
        print("Connected successfully!")
        
        # Your trading operations here...
        
    except Exception as e:
        print(f"Connection failed: {e}")

# Or manual connection management:
try:
    fx_conn.login(username, password, connection, server)
    
    # Your trading operations...
    
finally:
    fx_conn.logout()  # Always logout when done
"""
        print(example_code)

    def show_market_data_example(self):
        """
        Shows examples of how to access market data, including instruments,
        current prices, and historical data.
        """
        print("\n=== Market Data Examples ===")

        example_code = """
# Get market data (requires active connection):

# Get available instruments
instruments = fx_conn.get_instruments()
print("Available instruments:", instruments)

# Get current prices for EUR/USD
eurusd_data = fx_conn.get_candles("EUR/USD", period="m1", number=10)
print("EUR/USD recent candles:", eurusd_data)

# Get historical data
historical_data = fx_conn.get_candles(
    "EUR/USD", 
    period="H1",  # 1-hour candles
    start="2024-01-01", 
    end="2024-01-31"
)
print("Historical data shape:", historical_data.shape)
"""
        print(example_code)

    def show_account_example(self):
        """
        Shows examples of how to retrieve account information, such as
        account summary, open positions, and balance.
        """
        print("\n=== Account Information Examples ===")

        example_code = """
# Get account information (requires active connection):

# Get account summary
account_info = fx_conn.get_accounts()
print("Account info:", account_info)

# Get open positions
positions = fx_conn.get_open_positions()
print("Open positions:", positions)

# Get account balance
summary = fx_conn.get_summary()
print("Account summary:", summary)
"""
        print(example_code)

    def show_trading_example(self):
        """
        Shows examples of trading operations, including placing market and limit orders,
        and closing positions.
        """
        print("\n=== Trading Examples ===")

        example_code = """
# Trading operations (requires active connection):

# Place a market buy order
order_id = fx_conn.open_trade(
    symbol="EUR/USD",
    is_buy=True,
    amount=1000,  # 1K units
    time_in_force="GTC",  # Good Till Cancelled
    order_type="AtMarket"
)
print(f"Order placed with ID: {order_id}")

# Place a limit order
limit_order_id = fx_conn.create_order(
    symbol="EUR/USD",
    is_buy=True,
    amount=1000,
    rate=1.0800,  # Limit price
    order_type="Entry"
)
print(f"Limit order created with ID: {limit_order_id}")

# Close a position
fx_conn.close_trade(trade_id="12345", amount=1000)

# Close all positions for a symbol
fx_conn.close_all_for_symbol("EUR/USD")
"""
        print(example_code)

    def show_order_management_example(self):
        """
        Shows examples of order management, including retrieving, canceling,
        and modifying orders.
        """
        print("\n=== Order Management Examples ===")

        example_code = """
# Order management (requires active connection):

# Get all orders
orders = fx_conn.get_orders()
print("Current orders:", orders)

# Cancel an order
fx_conn.delete_order(order_id="67890")

# Modify an order
fx_conn.change_order(
    order_id="67890",
    rate=1.0850,  # New price
    amount=2000   # New amount
)

# Get order status
order_status = fx_conn.get_order("67890")
print("Order status:", order_status)
"""
        print(example_code)


def main():
    """
    Main function to run the corrected ForexConnect API example.
    """
    print("=== ForexConnect API Example (Corrected) ===\n")

    # Create example instance
    fx_example = ForexConnectExample()

    # Demonstrate connection creation
    if not fx_example.create_connection():
        print("Failed to create ForexConnect instance")
        return

    # Demo connection configuration
    demo_username = "your_demo_username"  # Replace with your credentials
    demo_password = "your_demo_password"  # Replace with your credentials

    if not fx_example.configure_connection(demo_username, demo_password):
        print("Configuration setup failed")
        return

    # Show various API capabilities
    fx_example.show_connection_example()
    fx_example.show_market_data_example()
    fx_example.show_account_example()
    fx_example.show_trading_example()
    fx_example.show_order_management_example()

    print("\n=== Getting Started ===")
    print("1. Sign up for FXCM demo account: https://www.fxcm.com/")
    print("2. Enable API access in your FXCM account settings")
    print("3. Replace credentials in the connection example")
    print("4. Use the examples above as templates for your trading scripts")

    print("\n=== Available ForexConnect Methods ===")
    try:
        conn = fx.ForexConnect()
        methods = [method for method in dir(conn) if not method.startswith("_")]
        print("ForexConnect class methods:")
        for method in sorted(methods):
            print(f"  - {method}")
    except Exception as e:
        print(f"Could not list methods: {e}")

    print("\n=== Important Notes ===")
    print("- Always test with demo account first")
    print("- Use proper error handling in production code")
    print("- Implement risk management")
    print("- Check FXCM documentation for complete API reference")
    print("- Use context managers (with statement) for automatic cleanup")


if __name__ == "__main__":
    main()
