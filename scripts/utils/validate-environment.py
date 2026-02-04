#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GenX FX Environment Validation Script
Checks for common issues after Google CLI installation
"""

import importlib
import os
import subprocess
import sys
from pathlib import Path


def check_python_version() -> bool:
    """
    Checks for Python version compatibility.

    Returns:
        bool: True if the Python version is 3.8 or higher, False otherwise.
    """
    print("Python Version Check:")
    print(f"   Current: {sys.version}")

    if sys.version_info < (3, 8):
        print("   [ERROR] Python 3.8+ required")
        return False
    else:
        print("   [OK] Python version OK")
        return True


def check_pip() -> bool:
    """
    Checks for pip installation and version.

    Returns:
        bool: True if pip is installed and accessible, False otherwise.
    """
    print("\nPip Check:")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"], capture_output=True, text=True
        )
        print(f"   {result.stdout.strip()}")
        print("   [OK] Pip OK")
        return True
    except Exception as e:
        print(f"   [ERROR] Pip error: {e}")
        return False


def check_required_packages() -> list:
    """
    Checks if all required Python packages are installed.

    Returns:
        list: A list of missing packages.
    """
    print("\nRequired Packages Check:")

    required_packages = [
        "fastapi",
        "uvicorn",
        "pandas",
        "numpy",
        "requests",
        "pydantic",
        "python-dotenv",
        "aiohttp",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            # Special handling for packages with different import names
            if package == "python-dotenv":
                importlib.import_module("dotenv")
            else:
                importlib.import_module(package.replace("-", "_"))
            print(f"   [OK] {package}")
        except ImportError:
            print(f"   [MISSING] {package}")
            missing_packages.append(package)

    return missing_packages


def check_gcloud() -> bool:
    """
    Checks for the Google Cloud CLI installation.

    Returns:
        bool: True if the gcloud CLI is found, False otherwise.
    """
    print("\nGoogle Cloud CLI Check:")
    try:
        # Try different gcloud paths
        gcloud_paths = [
            "gcloud",
            os.path.expandvars(
                "%LOCALAPPDATA%\\Google\\Cloud SDK\\google-cloud-sdk\\bin\\gcloud.cmd"
            ),
        ]

        for gcloud_path in gcloud_paths:
            try:
                result = subprocess.run(
                    [gcloud_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    version_line = result.stdout.strip().split("\n")[0]
                    print(f"   {version_line}")
                    print("   [OK] GCloud CLI OK")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        print("   [ERROR] GCloud CLI not found in PATH")
        return False
    except Exception as e:
        print(f"   [ERROR] GCloud CLI error: {e}")
        return False


def check_vscode_settings() -> bool:
    """
    Checks for the presence of VS Code settings files.

    Returns:
        bool: True if the settings files are found, False otherwise.
    """
    print("\nVS Code Settings Check:")

    vscode_dir = Path(".vscode")
    settings_file = vscode_dir / "settings.json"

    if vscode_dir.exists():
        print("   [OK] .vscode directory exists")
    else:
        print("   [ERROR] .vscode directory missing")
        return False

    if settings_file.exists():
        print("   [OK] settings.json exists")
        return True
    else:
        print("   [ERROR] settings.json missing")
        return False


def check_workspace_structure() -> list:
    """
    Checks the workspace for the required directory structure.

    Returns:
        list: A list of missing directories.
    """
    print("\nWorkspace Structure Check:")

    required_dirs = ["api", "core", "utils", "expert-advisors"]
    missing_dirs = []

    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"   [OK] {dir_name}/")
        else:
            print(f"   [MISSING] {dir_name}/")
            missing_dirs.append(dir_name)

    return missing_dirs


def main():
    """
    The main function to run all environment validation checks and print a summary.
    """
    print("GenX FX Environment Validation")
    print("=" * 40)

    # Run all checks
    python_ok = check_python_version()
    pip_ok = check_pip()
    missing_packages = check_required_packages()
    gcloud_ok = check_gcloud()
    vscode_ok = check_vscode_settings()
    missing_dirs = check_workspace_structure()

    # Summary
    print("\nSUMMARY:")
    print("=" * 20)

    if (
        python_ok
        and pip_ok
        and not missing_packages
        and gcloud_ok
        and vscode_ok
        and not missing_dirs
    ):
        print("[SUCCESS] All checks passed! Your environment is ready.")
    else:
        print("[WARNING] Issues found:")

        if not python_ok:
            print("   - Upgrade Python to 3.8+")

        if not pip_ok:
            print("   - Fix pip installation")

        if missing_packages:
            print(f"   - Install missing packages: {', '.join(missing_packages)}")
            print("     Run: pip install " + " ".join(missing_packages))

        if not gcloud_ok:
            print("   - Fix Google Cloud CLI installation")

        if not vscode_ok:
            print("   - VS Code settings need configuration")

        if missing_dirs:
            print(f"   - Missing directories: {', '.join(missing_dirs)}")

    print("\nTo fix issues, run: fix-vscode-issues.bat")


if __name__ == "__main__":
    main()
