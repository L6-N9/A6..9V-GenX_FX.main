#!/usr/bin/env python3
"""
Test runner for GenX Trading Platform
"""

import os
import subprocess
import sys


def run_tests() -> bool:
    """
    Runs the complete test suite for the GenX Trading Platform.

    This function sets up the necessary environment variables for testing
    and then executes pytest to run all tests in the 'tests/' directory.

    Returns:
        bool: True if all tests pass, False otherwise.
    """

    # Set test environment
    os.environ["TESTING"] = "1"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
    os.environ["REDIS_URL"] = "redis://localhost:6379"

    # Mock required Exness credentials for config validation
    os.environ["EXNESS_LOGIN"] = "12345678"
    os.environ["EXNESS_PASSWORD"] = "mock_password_123"
    os.environ["EXNESS_SERVER"] = "Exness-MT5Trial"

    print("Running GenX Trading Platform Tests...")
    print("=" * 50)

    # Run pytest
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"Error running tests: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
