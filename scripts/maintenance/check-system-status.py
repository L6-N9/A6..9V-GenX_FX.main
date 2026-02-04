#!/usr/bin/env python3
"""
GenX FX System Status Checker
Comprehensive system health and configuration checker
"""

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests


def check_python_version() -> bool:
    """
    Checks if the current Python version is 3.8 or higher.

    Returns:
        bool: True if the Python version is compatible, False otherwise.
    """
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(
            f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+"
        )
        return False


def check_python_packages() -> bool:
    """
    Checks if all required Python packages are installed.

    Returns:
        bool: True if all packages are installed, False otherwise.
    """
    print("\n📦 Checking Python packages...")
    required_packages = ["requests", "fastapi", "uvicorn", "google-generativeai"]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
        return False
    return True


def check_firewall_rules() -> bool:
    """
    Checks for the presence of specific Windows Firewall rules for the application.

    Returns:
        bool: True if the checks could be performed, False on error.
    """
    print("\n🔥 Checking Windows Firewall...")
    try:
        # Check if port 8080 is open
        result = subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "show",
                "rule",
                "name=GenX FX API Port 8080",
            ],
            capture_output=True,
            text=True,
        )

        if "GenX FX API Port 8080" in result.stdout:
            print("✅ Port 8080 firewall rule - OK")
        else:
            print("❌ Port 8080 firewall rule - Missing")

        # Check if port 9090 is open
        result = subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "show",
                "rule",
                "name=GenX FX EA Communication Port 9090",
            ],
            capture_output=True,
            text=True,
        )

        if "GenX FX EA Communication Port 9090" in result.stdout:
            print("✅ Port 9090 firewall rule - OK")
        else:
            print("❌ Port 9090 firewall rule - Missing")

        return True
    except Exception as e:
        print(f"⚠️ Could not check firewall rules: {e}")
        return False


def check_network_connectivity() -> bool:
    """
    Checks for internet, VPS, and local API connectivity.

    Returns:
        bool: True if internet connectivity is OK, False otherwise.
    """
    print("\n🌐 Checking network connectivity...")

    # Test internet connection
    try:
        requests.get("http://8.8.8.8", timeout=5)
        print("✅ Internet connectivity - OK")
    except requests.exceptions.RequestException:
        print("❌ Internet connectivity - Failed")
        return False

    # Test VPS connection
    try:
        response = requests.get("http://34.71.143.222:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ VPS connection - OK")
        else:
            print(f"⚠️ VPS connection - Status {response.status_code}")
    except requests.exceptions.RequestException:
        print("⚠️ VPS connection - Failed (this may be normal if VPS is down)")

    # Test local API
    try:
        response = requests.get("http://localhost:8080/health", timeout=3)
        if response.status_code == 200:
            print("✅ Local API - Running")
        else:
            print(f"⚠️ Local API - Status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Local API - Not running")

    return True


def check_file_structure() -> bool:
    """
    Checks if the required file and directory structure is in place.

    Returns:
        bool: True if all required files/directories exist, False otherwise.
    """
    print("\n📁 Checking file structure...")

    required_files = [
        "genx_robust_backend.py",
        "simple-api-server.py",
        "start-genx-complete.bat",
        "api/main.py",
    ]

    required_dirs = ["api", "logs", "data"]

    all_good = True

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - Found")
        else:
            print(f"❌ {file_path} - Missing")
            all_good = False

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ - Found")
        else:
            print(f"❌ {dir_path}/ - Missing")
            all_good = False

    return all_good


def check_environment_variables() -> bool:
    """
    Checks if essential environment variables are configured.

    Returns:
        bool: True if at least one variable is configured, False otherwise.
    """
    print("\n🔧 Checking environment variables...")

    env_vars = [
        "GEMINI_API_KEY",
        "EXNESS_LOGIN",
        "EXNESS_PASSWORD",
        "EXNESS_SERVER",
        "SECRET_KEY",
    ]

    configured = 0
    for var in env_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"✅ {var} - Configured")
            configured += 1
        else:
            print(f"⚠️ {var} - Not configured")

    if configured == 0:
        print("⚠️ No environment variables configured")
    elif configured < len(env_vars):
        print(f"⚠️ {configured}/{len(env_vars)} environment variables configured")
    else:
        print("✅ All environment variables configured")

    return configured > 0


def check_system_resources() -> bool:
    """
    Checks system resources like CPU, memory, and disk usage.

    Returns:
        bool: True if psutil is available and checks are run, False otherwise.
    """
    print("\n💻 Checking system resources...")

    try:
        import psutil

        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"🖥️ CPU Usage: {cpu_percent}%")

        # Check memory usage
        memory = psutil.virtual_memory()
        print(
            f"🧠 Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)"
        )

        # Check disk space
        disk = psutil.disk_usage(".")
        print(f"💾 Disk Usage: {disk.percent}% ({disk.free // (1024**3)}GB free)")

        if cpu_percent > 90:
            print("⚠️ High CPU usage detected")
        if memory.percent > 90:
            print("⚠️ High memory usage detected")
        if disk.percent > 90:
            print("⚠️ Low disk space detected")

        return True
    except ImportError:
        print("⚠️ psutil not available - install with: pip install psutil")
        return False


def check_logs() -> bool:
    """
    Checks for the existence and size of log files.

    Returns:
        bool: Always returns True after performing checks.
    """
    print("\n📋 Checking log files...")

    log_files = ["genx-backend.log", "api-server.log", "gold-signals.log"]

    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✅ {log_file} - {size} bytes")
        else:
            print(f"⚠️ {log_file} - Not found")

    return True


def generate_report() -> dict:
    """
    Generates and prints a comprehensive system status report.

    Returns:
        dict: A dictionary containing the results of all checks.
    """
    print("\n" + "=" * 50)
    print("GenX FX System Status Report")
    print("=" * 50)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_python_packages),
        ("Firewall Rules", check_firewall_rules),
        ("Network Connectivity", check_network_connectivity),
        ("File Structure", check_file_structure),
        ("Environment Variables", check_environment_variables),
        ("System Resources", check_system_resources),
        ("Log Files", check_logs),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results[name] = False

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 System is ready for 24/7 operation!")
    elif passed >= total * 0.8:
        print("⚠️ System is mostly ready, some issues detected")
    else:
        print("❌ System needs attention before 24/7 operation")

    return results


def main():
    """
    Main entry point for the system status checker script.
    """
    print("GenX FX System Status Checker")
    print("=" * 40)

    generate_report()

    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()
