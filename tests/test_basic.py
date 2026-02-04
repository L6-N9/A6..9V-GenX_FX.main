import sys

import pytest


def test_python_version():
    """Test that we're running on a supported Python version"""
    assert sys.version_info >= (3, 8)


def test_imports():
    """Test that basic imports work"""
    try:
        import asyncio
        import json
        import os

        assert True
    except ImportError as e:
        pytest.fail(f"Basic imports failed: {e}")


def test_environment():
    """Test basic environment setup"""
    import os

    # Test that we can set and get environment variables
    os.environ["TEST_VAR"] = "test_value"
    assert os.environ.get("TEST_VAR") == "test_value"


def test_json_handling():
    """Test basic JSON operations"""
    import json

    test_data = {"key": "value", "number": 42}
    json_str = json.dumps(test_data)
    parsed_data = json.loads(json_str)
    assert parsed_data == test_data


def test_math_operations():
    """Test basic math operations"""
    assert 2 + 2 == 4
    assert 10 * 5 == 50
    assert 100 / 10 == 10


def test_string_operations():
    """Test basic string operations"""
    test_string = "Hello, World!"
    assert len(test_string) == 13
    assert test_string.upper() == "HELLO, WORLD!"
    assert test_string.lower() == "hello, world!"
