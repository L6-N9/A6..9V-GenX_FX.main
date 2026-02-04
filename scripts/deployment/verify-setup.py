import json
import os
import socket
import subprocess
import sys
from datetime import datetime

import requests


def check_endpoint(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)


def check_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception as e:
        return False


def get_service_status(service_name):
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service_name], capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    except Exception:
        return None


def main():
    print(
        f"=== GenX FX VPS Verification Tool ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ==="
    )

    # 1. API Health Checks
    print("\n--- API Health ---")
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    endpoints = ["/", "/health", "/api/v1/health", "/trading-pairs", "/mt5-info"]

    for ep in endpoints:
        success, status = check_endpoint(f"{base_url}{ep}")
        icon = "✅" if success else "❌"
        print(f"{icon} {ep}: {status}")

    # 2. Service Port Checks
    print("\n--- Service Ports ---")
    ports = {
        8000: "FastAPI Backend",
        8080: "24/7 Backend / Monitoring",
        9090: "EA Communication Server",
        6379: "Redis Server",
        5432: "PostgreSQL (optional)",
    }

    for port, name in ports.items():
        is_open = check_port("localhost", port)
        icon = "✅" if is_open else "⚠️" if port in [5432, 8080] else "❌"
        status = "Open" if is_open else "Closed/Unavailable"
        print(f"{icon} {port} ({name}): {status}")

    # 3. Environment Variables
    print("\n--- Environment Variables ---")
    critical_vars = [
        "FXCM_USERNAME",
        "FXCM_PASSWORD",
        "GEMINI_API_KEY",
        "VPS_URL",
        "REDIS_HOST",
        "REDIS_PORT",
    ]
    for var in critical_vars:
        val = os.getenv(var)
        if val:
            masked = val[:4] + "*" * (len(val) - 4) if len(val) > 4 else "***"
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: NOT SET")

    # 4. Critical Files
    print("\n--- Critical Files ---")
    files = [
        "genx_24_7_backend.py",
        "genx_robust_backend.py",
        ".env",
        "requirements.txt",
        "api/main.py",
    ]
    for f in files:
        exists = os.path.exists(f)
        icon = "✅" if exists else "❌"
        print(f"{icon} {f}: {'Exists' if exists else 'Missing'}")

    # 5. Background Services (Systemd) - Only if on Linux
    if sys.platform.startswith("linux"):
        print("\n--- Systemd Services ---")
        services = ["genx-trading", "act_runner", "redis-server", "postgresql"]
        for svc in services:
            status = get_service_status(svc)
            if status is True:
                print(f"✅ {svc}: Active")
            elif status is False:
                print(f"❌ {svc}: Inactive")
            else:
                print(f"⚪ {svc}: Not found or systemctl unavailable")

    print("\n=== Verification Complete ===")


if __name__ == "__main__":
    main()
