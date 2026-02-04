#!/usr/bin/env python3
"""
FXCM Connection Test Script (Credentials Removed)
This script tests the ForexConnect API connection - credentials should be set via environment variables
"""

import os
import sys
import time

import pytest

try:
    import forexconnect as fx
except ImportError:
    fx = None

# FXCM Credentials from environment variables
FXCM_USERNAME = os.getenv("FXCM_USERNAME", "YOUR_USERNAME_HERE")
FXCM_PASSWORD = os.getenv("FXCM_PASSWORD", "YOUR_PASSWORD_HERE")
FXCM_CONNECTION_TYPE = os.getenv("FXCM_CONNECTION_TYPE", "Demo")
FXCM_URL = os.getenv("FXCM_URL", "http://fxcorporate.com/Hosts.jsp")


@pytest.mark.skipif(fx is None, reason="forexconnect not installed")
class FXCMConnectionTest:
    """
    A class to test the connection to the FXCM ForexConnect API.
    """

    def __init__(self):
        """
        Initializes the FXCMConnectionTest class.
        """
        self.forex_connect = None
        self.session = None

    def test_connection(self) -> bool:
        """
        Tests the connection to FXCM using the ForexConnect API and credentials
        from environment variables.

        Returns:
            bool: True if the connection and basic operations are successful, False otherwise.
        """
        try:
            print("=== FXCM Connection Test ===")
            print(f"Username: {FXCM_USERNAME}")
            print(f"Connection Type: {FXCM_CONNECTION_TYPE}")
            print(f"URL: {FXCM_URL}")
            print()

            if FXCM_USERNAME == "YOUR_USERNAME_HERE":
                print("⚠️  Please set environment variables:")
                print("   export FXCM_USERNAME='your_username'")
                print("   export FXCM_PASSWORD='your_password'")
                print("   export FXCM_CONNECTION_TYPE='Demo'")
                print("   export FXCM_URL='http://fxcorporate.com/Hosts.jsp'")
                return False

            # Create ForexConnect instance
            print("Creating ForexConnect instance...")
            self.forex_connect = fx.ForexConnect()
            print("✓ ForexConnect instance created")

            # Attempt to login
            print("Attempting to login to FXCM...")
            self.session = self.forex_connect.login(
                user_id=FXCM_USERNAME,
                password=FXCM_PASSWORD,
                url=FXCM_URL,
                connection=FXCM_CONNECTION_TYPE,
            )

            if self.session:
                print("✓ Successfully logged in to FXCM!")

                # Test basic operations
                self.test_basic_operations()

                # Logout
                try:
                    self.session.logout()
                    print("✓ Successfully logged out from FXCM")
                except:
                    print("- Logout method not available or already disconnected")

            else:
                print("✗ Failed to login to FXCM")
                return False

        except Exception as e:
            print(f"✗ Connection test failed: {e}")
            print(f"Error type: {type(e)}")
            import traceback

            traceback.print_exc()
            return False

        return True

    def test_basic_operations(self):
        """
        Tests basic API operations, such as retrieving tables for offers,
        accounts, trades, orders, and summary.
        """
        try:
            print("\n--- Testing Basic Operations ---")

            # Test get_table method for different table types
            table_types = ["OFFERS", "ACCOUNTS", "TRADES", "ORDERS", "SUMMARY"]

            for table_type in table_types:
                try:
                    table_name = getattr(self.forex_connect, table_type)
                    table = self.forex_connect.get_table(table_name)
                    if table:
                        print(f"✓ Retrieved {table_type} table: {table.size()} rows")

                        # Display sample data for offers (market data)
                        if table_type == "OFFERS" and table.size() > 0:
                            print("  Sample currency pairs:")
                            for i in range(min(5, table.size())):
                                offer = table.get_row(i)
                                instrument = offer.instrument
                                bid = offer.bid
                                ask = offer.ask
                                print(f"    {instrument}: Bid={bid}, Ask={ask}")

                        # Display account information
                        elif table_type == "ACCOUNTS" and table.size() > 0:
                            print("  Account information:")
                            account = table.get_row(0)
                            balance = account.balance
                            account_id = account.account_id
                            currency = account.account_currency
                            print(f"    Account ID: {account_id}")
                            print(f"    Balance: {balance} {currency}")

                    else:
                        print(f"- {table_type} table is empty or not available")

                except Exception as e:
                    print(f"- Failed to retrieve {table_type} table: {e}")

        except Exception as e:
            print(f"✗ Basic operations test failed: {e}")


def main() -> bool:
    """
    The main function to run the FXCM connection test.

    Returns:
        bool: True if the test is successful, False otherwise.
    """
    print("Starting FXCM ForexConnect API test...")
    print("This will test connection and basic data retrieval.")
    print()

    tester = FXCMConnectionTest()
    success = tester.test_connection()

    if success:
        print("\n🎉 FXCM connection test completed successfully!")
        print("The ForexConnect API is working and can retrieve market data.")
    else:
        print("\n❌ FXCM connection test failed!")
        print("Please check your credentials and network connection.")

    return success


if __name__ == "__main__":
    if fx is None:
        print("ForexConnect not installed. Skipping test.")
        sys.exit(0)
    main()
