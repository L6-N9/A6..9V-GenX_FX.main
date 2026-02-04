#!/usr/bin/env python3
"""
ForexConnect API Test Script
This script tests the ForexConnect installation and shows basic usage examples.
"""

import pytest


def test_forexconnect_import():
    """
    Tests if the ForexConnect module can be imported successfully and prints
    version information if available.
    """
    try:
        import forexconnect as fx
    except ImportError:
        pytest.skip("ForexConnect not installed")

    print("✓ ForexConnect imported successfully!")

    # Show version info
    if hasattr(fx, "__version__"):
        print(f"✓ ForexConnect version: {fx.__version__}")

    # Show available attributes (first 10)
    attributes = [attr for attr in dir(fx) if not attr.startswith("_")]
    print(f"✓ Available modules/classes: {attributes[:10]}")


def show_basic_usage():
    """
    Shows basic usage examples for the ForexConnect API, including how to
    create a session and set up connection parameters.
    """
    try:
        import forexconnect as fx

        print("\n=== Basic ForexConnect Usage Examples ===")

        # Try to show basic API structure
        if hasattr(fx, "O2GSession"):
            print("✓ O2GSession class available")

        if hasattr(fx, "O2GSessionDescriptor"):
            print("✓ O2GSessionDescriptor class available")

        if hasattr(fx, "O2GLoginDescriptor"):
            print("✓ O2GLoginDescriptor class available")

        # Basic connection example (without actual connection)
        print("\n=== Example Connection Code (not executed) ===")
        example_code = """
# Basic ForexConnect connection example:
import forexconnect as fx

# Create session
session = fx.O2GSession()

# Set up login parameters
session_descriptor = fx.O2GSessionDescriptor()
session_descriptor.setUrl("http://www.fxcorporate.com/Hosts.jsp")  # Demo server
session_descriptor.setUser("your_username")
session_descriptor.setPassword("your_password")
session_descriptor.setConnection("Demo")  # or "Real"

# Login (this would actually connect)
# session.login(session_descriptor)

print("Connection setup complete")
"""
        print(example_code)

    except Exception as e:
        print(f"Error showing usage examples: {e}")


if __name__ == "__main__":
    print("=== ForexConnect Installation Test ===")

    # Test import
    if test_forexconnect_import():
        show_basic_usage()
        print("\n✓ ForexConnect is properly installed and ready to use!")
        print("\nNext steps:")
        print("1. Get FXCM demo or live account credentials")
        print("2. Use the connection example above to start trading")
        print("3. Check FXCM documentation for advanced features")
    else:
        print("\n✗ ForexConnect installation test failed")
        print("Please check the installation steps or contact FXCM support")
