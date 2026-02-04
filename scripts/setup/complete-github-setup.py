#!/usr/bin/env python3
"""
Complete GitHub Setup - Final step to ensure all secrets and variables are set
"""

import base64
import os

import requests
from nacl import encoding, public

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_OWNER = "Mouy-leng"
REPO_NAME = "GenX_FX"
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


class GitHubSecretsManager:
    """
    Manages secrets and variables in a GitHub repository.
    """

    def __init__(self):
        """
        Initializes the GitHubSecretsManager with authentication headers.
        """
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_public_key(self):
        """
        Retrieves the public key for encrypting secrets.

        Raises:
            Exception: If the public key cannot be retrieved.

        Returns:
            dict: The public key data.
        """
        response = requests.get(
            f"{BASE_URL}/actions/secrets/public-key", headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get public key: {response.text}")

    def encrypt_secret(self, public_key_b64, secret_value):
        """
        Encrypts a secret using the repository's public key.

        Args:
            public_key_b64 (str): The base64-encoded public key.
            secret_value (str): The value of the secret to encrypt.

        Returns:
            str: The encrypted secret, base64-encoded.
        """
        public_key = public.PublicKey(
            public_key_b64.encode("utf-8"), encoding.Base64Encoder()
        )
        box = public.SealedBox(public_key)
        encrypted = box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    def set_secret(self, name, value):
        """
        Sets a secret in the GitHub repository.

        Args:
            name (str): The name of the secret.
            value (str): The value of the secret.

        Returns:
            bool: True if the secret was set successfully, False otherwise.
        """
        key_data = self.get_public_key()
        encrypted_value = self.encrypt_secret(key_data["key"], value)
        data = {"encrypted_value": encrypted_value, "key_id": key_data["key_id"]}
        response = requests.put(
            f"{BASE_URL}/actions/secrets/{name}", headers=self.headers, json=data
        )
        return response.status_code in [201, 204]

    def set_variable(self, name, value):
        """
        Sets a variable in the GitHub repository.

        Args:
            name (str): The name of the variable.
            value (str): The value of the variable.

        Returns:
            bool: True if the variable was set successfully, False otherwise.
        """
        data = {"name": name, "value": value}
        response = requests.post(
            f"{BASE_URL}/actions/variables", headers=self.headers, json=data
        )
        return response.status_code in [201, 204]


def complete_setup():
    """
    Completes the GitHub setup by ensuring all necessary secrets and variables are set.
    """
    manager = GitHubSecretsManager()

    print("Completing GitHub Setup...")
    print("=" * 30)

    # Additional secrets that might be missing
    additional_secrets = {
        "SECRET_KEY": "genx_fx_secret_key_2024",
        "MONGO_PASSWORD": "genx_mongo_password_2024",
        "REDIS_PASSWORD": "genx_redis_password_2024",
        "FXCM_API_TOKEN": "your_fxcm_api_token_here",
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "TELEGRAM_TOKEN": "your_telegram_bot_token_here",
    }

    # Additional variables that might be missing
    additional_variables = {
        "NODE_ENV": "production",
        "LOG_LEVEL": "INFO",
        "PORT": "8000",
        "POSTGRES_DB": "genx_trading",
        "POSTGRES_USER": "genx_user",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
    }

    print("\nSetting additional secrets...")
    for name, value in additional_secrets.items():
        try:
            success = manager.set_secret(name, value)
            print(f"   {'[OK]' if success else '[ERROR]'} {name}")
        except Exception as e:
            print(f"   [ERROR] {name}: {str(e)}")

    print("\nSetting additional variables...")
    for name, value in additional_variables.items():
        try:
            success = manager.set_variable(name, value)
            print(f"   {'[OK]' if success else '[ERROR]'} {name}")
        except Exception as e:
            print(f"   [ERROR] {name}: {str(e)}")

    print("\n[SUCCESS] Setup completion attempted!")


if __name__ == "__main__":
    complete_setup()
