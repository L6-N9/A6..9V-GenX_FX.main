import sqlite3

import pytest
from fastapi.testclient import TestClient

from api.main import app, get_db


# Pytest fixture to set up and tear down an in-memory database for testing
@pytest.fixture(scope="module")
def db_override():
    """
    Pytest fixture to override the 'get_db' dependency with an in-memory SQLite database.
    This ensures tests are isolated and don't depend on an external database.
    """
    # Use in-memory SQLite database for tests, allowing connections from multiple threads
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()

    # Create the necessary table for the billing endpoint
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY,
            cardholder_name TEXT,
            masked_card_number TEXT
        )
    """)
    conn.commit()

    # Define the dependency override function
    def get_test_db():
        try:
            yield conn
        finally:
            # The connection will be closed at the end of the test module
            pass

    # Apply the override to the FastAPI app instance
    app.dependency_overrides[get_db] = get_test_db

    # Yield control to the tests
    yield

    # Teardown: clear the dependency override and close the connection
    app.dependency_overrides.clear()
    conn.close()


client = TestClient(app)


def test_add_payment_method_success(db_override):
    """Test successful addition of a valid payment method."""
    valid_data = {
        "cardholderName": "John Doe",
        "cardNumber": "1234-5678-9012-3456",
        "expiryDate": "12/25",
        "cvc": "123",
    }
    response = client.post("/api/v1/billing", json=valid_data)
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code} with body: {response.text}"
    response_json = response.json()
    assert response_json["status"] == "success"


def test_add_payment_method_invalid_data(db_override):
    """Test that invalid payment method data returns a 422 Unprocessable Entity error."""
    invalid_payloads = [
        # Case 1: Empty cardholder name
        (
            {
                "cardholderName": "",
                "cardNumber": "1234-5678-9012-3456",
                "expiryDate": "12/25",
                "cvc": "123",
            },
            "empty cardholderName",
        ),
        # Case 2: Invalid card number format
        (
            {
                "cardholderName": "John Doe",
                "cardNumber": "1234",
                "expiryDate": "12/25",
                "cvc": "123",
            },
            "invalid cardNumber",
        ),
        # Case 3: Invalid expiry date format (month > 12)
        (
            {
                "cardholderName": "John Doe",
                "cardNumber": "1234-5678-9012-3456",
                "expiryDate": "13/25",
                "cvc": "123",
            },
            "invalid expiryDate",
        ),
        # Case 4: Invalid CVC format (too long)
        (
            {
                "cardholderName": "John Doe",
                "cardNumber": "1234-5678-9012-3456",
                "expiryDate": "12/25",
                "cvc": "12345",
            },
            "invalid cvc",
        ),
    ]

    for payload, description in invalid_payloads:
        response = client.post("/api/v1/billing", json=payload)
        assert (
            response.status_code == 422
        ), f"Failed on payload: {description}. Got {response.status_code} with body: {response.text}"
