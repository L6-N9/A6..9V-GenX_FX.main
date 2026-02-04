import json
import os
import sqlite3


def setup_database():
    """
    Sets up the SQLite database by creating tables and seeding initial data.
    This function is idempotent and can be run multiple times safely.
    """
    conn = sqlite3.connect("genxdb_fx.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Create trading_pairs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trading_pairs (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL UNIQUE,
        base_currency TEXT NOT NULL,
        quote_currency TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Seed initial data (if tables are empty)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            ("testuser", "test@example.com"),
        )

    # Load trading pairs from config
    config_path = "config/trading_config.json"
    if not os.path.exists(config_path):
        # Fallback for when running from scripts/setup/
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "trading_config.json",
        )

    symbols = []
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            symbols = config.get("trading", {}).get("symbols", [])
    except Exception as e:
        print(f"Warning: Could not load config from {config_path}: {e}")
        # Fallback defaults if config fails
        symbols = ["EURUSD", "GBPUSD"]

    cursor.execute("SELECT COUNT(*) FROM trading_pairs")
    if cursor.fetchone()[0] == 0:
        for symbol in symbols:
            # Simple heuristic for base/quote splitting (assuming 3+3 chars for standard pairs)
            if len(symbol) >= 6:
                base = symbol[:3]
                quote = symbol[3:]
            else:
                base = symbol
                quote = "USD"  # Default fallback

            try:
                cursor.execute(
                    "INSERT INTO trading_pairs (symbol, base_currency, quote_currency) VALUES (?, ?, ?)",
                    (symbol, base, quote),
                )
            except sqlite3.IntegrityError:
                print(f"Skipping duplicate symbol: {symbol}")

    conn.commit()
    conn.close()
    print("Database setup complete.")


if __name__ == "__main__":
    setup_database()
