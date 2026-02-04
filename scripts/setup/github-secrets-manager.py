#!/usr/bin/env python3
"""
GenX FX GitHub Secrets Manager
Comprehensive secrets and environment management for GitHub Actions
"""

import base64
import json
import os
from pathlib import Path

import requests
from nacl import encoding, public

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_OWNER = "Mouy-leng"
REPO_NAME = "GenX_FX"
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


class GitHubSecretsManager:
    """
    A class to manage GitHub secrets and variables for a repository and its environments.
    """

    def __init__(self):
        """
        Initializes the GitHubSecretsManager with authentication headers.
        """
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        }

    def get_public_key(self) -> dict:
        """
        Gets the repository's public key for encrypting secrets.

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

    def encrypt_secret(self, public_key_b64: str, secret_value: str) -> str:
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

    def set_secret(self, name: str, value: str) -> bool:
        """
        Sets a secret for the repository.

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

    def set_environment_secret(
        self, env_name: str, secret_name: str, value: str
    ) -> bool:
        """
        Sets a secret for a specific environment.

        Args:
            env_name (str): The name of the environment.
            secret_name (str): The name of the secret.
            value (str): The value of the secret.

        Returns:
            bool: True if the secret was set successfully, False otherwise.
        """
        key_data = self.get_environment_public_key(env_name)
        encrypted_value = self.encrypt_secret(key_data["key"], value)

        data = {"encrypted_value": encrypted_value, "key_id": key_data["key_id"]}

        response = requests.put(
            f"{BASE_URL}/environments/{env_name}/secrets/{secret_name}",
            headers=self.headers,
            json=data,
        )
        return response.status_code in [201, 204]

    def get_environment_public_key(self, env_name: str) -> dict:
        """
        Gets the public key for a specific environment.

        Args:
            env_name (str): The name of the environment.

        Raises:
            Exception: If the public key cannot be retrieved.

        Returns:
            dict: The public key data for the environment.
        """
        response = requests.get(
            f"{BASE_URL}/environments/{env_name}/secrets/public-key",
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get environment public key: {response.text}")

    def create_environment(self, env_name: str) -> bool:
        """
        Creates a new environment if it doesn't already exist.

        Args:
            env_name (str): The name of the environment to create.

        Returns:
            bool: True if the environment was created or already exists, False otherwise.
        """
        data = {"wait_timer": 0, "reviewers": [], "deployment_branch_policy": None}
        response = requests.put(
            f"{BASE_URL}/environments/{env_name}", headers=self.headers, json=data
        )
        return response.status_code in [200, 201]

    def set_variable(self, name: str, value: str) -> bool:
        """
        Sets a variable for the repository.

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


def collect_secrets_from_files() -> dict:
    """
    Collects secret names from various configuration files.

    Returns:
        dict: A dictionary of secret names with empty values.
    """
    secrets = {}

    # From .env.example
    env_file = Path(".env.example")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if (
                    "=" in line
                    and not line.startswith("#")
                    and not line.startswith("DATABASE_URL")
                ):
                    key = line.split("=")[0].strip()
                    if key and not any(
                        x in key.lower()
                        for x in ["url", "host", "port", "env", "level"]
                    ):
                        secrets[key] = ""

    # Add specific secrets needed for GenX FX
    trading_secrets = {
        "BYBIT_API_KEY": "",
        "BYBIT_API_SECRET": "",
        "FXCM_API_TOKEN": "",
        "FXCM_API_KEY": "",
        "FXCM_SECRET_KEY": "",
        "GEMINI_API_KEY": "",
        "OPENAI_API_KEY": "",
        "ALPHA_VANTAGE_API_KEY": "",
        "NEWS_API_KEY": "",
        "DISCORD_TOKEN": "",
        "TELEGRAM_TOKEN": "",
        "AMP_TOKEN": "",
        "SECRET_KEY": "",
        "DB_PASSWORD": "",
        "MONGO_PASSWORD": "",
        "REDIS_PASSWORD": "",
        "GRAFANA_PASSWORD": "",
        "POSTGRES_PASSWORD": "",
    }

    secrets.update(trading_secrets)
    return secrets


def collect_variables() -> dict:
    """
    Collects non-sensitive variables for the repository.

    Returns:
        dict: A dictionary of non-sensitive variables.
    """
    return {
        "NODE_ENV": "production",
        "LOG_LEVEL": "INFO",
        "PORT": "8000",
        "API_PORT": "8000",
        "GRAFANA_PORT": "3000",
        "GEMINI_MODEL": "gemini-1.5-flash",
        "GEMINI_MAX_TOKENS": "2048",
        "GEMINI_RATE_LIMIT_RPM": "30",
        "FXCM_URL": "https://api-fxpractice.fxcm.com",
        "POSTGRES_DB": "genx_trading",
        "POSTGRES_USER": "genx_user",
        "POSTGRES_HOST": "postgres",
        "POSTGRES_PORT": "5432",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
        "MONGODB_URL": "mongodb://mongo:27017/genx_trading",
    }


def main():
    """
    The main execution function for the GitHub Secrets Manager.
    It creates environments, and sets repository and environment-specific secrets and variables.
    """
    print("GenX FX GitHub Secrets Manager")
    print("=" * 50)

    manager = GitHubSecretsManager()

    # Create environments
    environments = ["development", "staging", "production"]
    print("\nCreating environments...")
    for env in environments:
        try:
            success = manager.create_environment(env)
            print(f"   {'[OK]' if success else '[WARN]'} {env}")
        except Exception as e:
            print(f"   [ERROR] {env}: {str(e)}")

    # Set repository secrets
    print("\nSetting repository secrets...")
    secrets = collect_secrets_from_files()

    for name, value in secrets.items():
        try:
            # Use placeholder for empty secrets
            secret_value = value if value else f"your_{name.lower()}_here"
            success = manager.set_secret(name, secret_value)
            print(f"   {'[OK]' if success else '[ERROR]'} {name}")
        except Exception as e:
            print(f"   [ERROR] {name}: {str(e)}")

    # Set repository variables
    print("\nSetting repository variables...")
    variables = collect_variables()

    for name, value in variables.items():
        try:
            success = manager.set_variable(name, value)
            print(f"   {'[OK]' if success else '[ERROR]'} {name}")
        except Exception as e:
            print(f"   [ERROR] {name}: {str(e)}")

    # Set environment-specific secrets
    print("\nSetting environment secrets...")
    env_secrets = {
        "production": {
            "DATABASE_URL": "postgresql://genx_user:${DB_PASSWORD}@postgres:5432/genx_trading",
            "REDIS_URL": "redis://:${REDIS_PASSWORD}@redis:6379",
        },
        "staging": {
            "DATABASE_URL": "postgresql://genx_user:${DB_PASSWORD}@postgres-staging:5432/genx_trading_staging",
            "REDIS_URL": "redis://:${REDIS_PASSWORD}@redis-staging:6379",
        },
    }

    for env_name, env_secrets_dict in env_secrets.items():
        print(f"\n   Environment: {env_name}")
        for secret_name, secret_value in env_secrets_dict.items():
            try:
                success = manager.set_environment_secret(
                    env_name, secret_name, secret_value
                )
                print(f"     {'[OK]' if success else '[ERROR]'} {secret_name}")
            except Exception as e:
                print(f"     [ERROR] {secret_name}: {str(e)}")

    print("\n[SUCCESS] GitHub secrets management completed!")
    print("\nNext steps:")
    print("   1. Update actual secret values in GitHub repository settings")
    print("   2. Review and update CI/CD pipeline")
    print("   3. Test deployment workflows")


if __name__ == "__main__":
    main()
