#!/usr/bin/env python3
"""
Script to generate a valid Fernet encryption key.
Users can run this script and add the output to their .env file as CRYPTION_KEY.
"""

import sys

from cryptography.fernet import Fernet


def generate_key():
    try:
        key = Fernet.generate_key().decode()
        print("\n=== GenX-FX Encryption Key Generator ===")
        print("\nHere is your new encryption key:\n")
        print(f"{key}")
        print("\n========================================")
        print("Copy the above key and add it to your .env file:")
        print(f"CRYPTION_KEY={key}")
        print("========================================\n")
        return key
    except Exception as e:
        print(f"Error generating key: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    generate_key()
