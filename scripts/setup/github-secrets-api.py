import base64
import json
import os

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# GitHub API setup
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "Mouy-leng"
REPO_NAME = "GenX_FX"


def get_public_key() -> dict:
    """
    Retrieves the public key for the repository from the GitHub API.

    Returns:
        dict: A dictionary containing the public key and its ID.
    """
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """
    Encrypts a secret using the repository's public key.

    Args:
        public_key (str): The public key to use for encryption.
        secret_value (str): The secret value to encrypt.

    Returns:
        str: The encrypted secret, base64-encoded.
    """
    public_key_obj = serialization.load_pem_public_key(public_key.encode())
    encrypted_bytes = public_key_obj.encrypt(secret_value.encode(), padding.PKCS1v15())
    return base64.b64encode(encrypted_bytes).decode()


def set_secret(name: str, value: str, key_id: str, public_key: str) -> bool:
    """
    Sets a secret in the GitHub repository.

    Args:
        name (str): The name of the secret.
        value (str): The value of the secret.
        key_id (str): The ID of the public key used for encryption.
        public_key (str): The public key to use for encryption.

    Returns:
        bool: True if the secret was set successfully, False otherwise.
    """
    encrypted_value = encrypt_secret(public_key, value)
    url = (
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{name}"
    )
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {"encrypted_value": encrypted_value, "key_id": key_id}
    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 201 or response.status_code == 204


# Load .env file
secrets = {}
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                secrets[key] = value

# Get GitHub public key
try:
    key_data = get_public_key()
    public_key = key_data["key"]
    key_id = key_data["key_id"]

    # Set secrets
    for name, value in secrets.items():
        if value and name not in ["NODE_ENV", "PORT"]:
            success = set_secret(name, value, key_id, public_key)
            print(f"{'✓' if success else '✗'} {name}")

except Exception as e:
    print(f"Error: {e}")
    print("Set GITHUB_TOKEN environment variable with repo access")
