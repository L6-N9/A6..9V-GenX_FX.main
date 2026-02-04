# Qodo Task 3: Start backend and run tests
import os
import subprocess

print("Qodo: Starting backend server and running tests")

# Start backend server
print("1. Start backend: python api/main.py")
print("2. Run tests: python -m pytest tests/ -v")
print("3. Check endpoints: curl http://localhost:8080/health")
print(
    '4. Validate database: python -c \'import sqlite3; print(sqlite3.connect("genxdb_fx.db").execute("SELECT 1").fetchone())\''
)

# Test commands
test_commands = [
    "python -m pytest tests/test_bybit_api.py -v",
    "python -m pytest tests/test_api.py -v",
    "python -m pytest tests/test_edge_cases.py -v",
]

for cmd in test_commands:
    print(f"Run: {cmd}")
