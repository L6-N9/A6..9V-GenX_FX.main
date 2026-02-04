#!/usr/bin/env python3
"""
AMP CLI Wrapper - A simple wrapper to execute the AMP CLI.

This script ensures that the current directory is in the Python path and then
imports and runs the main Typer application from 'amp_cli.py'.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path.cwd()))

try:
    from amp_cli import app

    app()
except ImportError as e:
    print(f"Error importing AMP CLI: {e}")
    print("Make sure you're in the correct directory and amp_cli.py exists")
    sys.exit(1)
