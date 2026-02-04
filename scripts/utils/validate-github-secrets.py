#!/usr/bin/env python3
"""
GitHub Secrets Validation Script
Validates that all required secrets and variables are properly set
"""

import os

import requests

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_OWNER = "Mouy-leng"
REPO_NAME = "GenX_FX"
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


def check_token_permissions() -> tuple:
    """
    Checks if the provided GitHub token has the required permissions.

    Returns:
        tuple: A tuple containing a boolean indicating success and a message.
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Test repository access
    response = requests.get(f"{BASE_URL}", headers=headers)
    if response.status_code != 200:
        return False, "No repository access"

    # Test secrets access
    response = requests.get(f"{BASE_URL}/actions/secrets", headers=headers)
    if response.status_code == 403:
        return False, "No secrets access - need 'repo' and 'workflow' permissions"

    return True, "Token has required permissions"


def list_repository_secrets() -> list:
    """
    Lists all repository secrets.

    Returns:
        list: A list of secret names.
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(f"{BASE_URL}/actions/secrets", headers=headers)

    if response.status_code == 200:
        return [secret["name"] for secret in response.json().get("secrets", [])]
    return []


def list_repository_variables() -> list:
    """
    Lists all repository variables.

    Returns:
        list: A list of variable names.
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(f"{BASE_URL}/actions/variables", headers=headers)

    if response.status_code == 200:
        return [var["name"] for var in response.json().get("variables", [])]
    return []


def list_environments() -> list:
    """
    Lists all environments for the repository.

    Returns:
        list: A list of environment names.
    """
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(f"{BASE_URL}/environments", headers=headers)

    if response.status_code == 200:
        return [env["name"] for env in response.json().get("environments", [])]
    return []


def main():
    """
    The main validation function, which checks for token permissions,
    required secrets, variables, and environments.
    """
    print("GitHub Secrets Validation")
    print("=" * 40)

    # Check token permissions
    print("\nToken Permissions Check:")
    has_permissions, message = check_token_permissions()
    print(f"   {'[OK]' if has_permissions else '[ERROR]'} {message}")

    if not has_permissions:
        print("\n[CRITICAL] Token lacks required permissions!")
        print("Create a new token with 'repo' and 'workflow' scopes:")
        print("https://github.com/settings/tokens/new?scopes=repo,workflow")
        return

    # Required secrets
    required_secrets = [
        "SECRET_KEY",
        "DB_PASSWORD",
        "MONGO_PASSWORD",
        "REDIS_PASSWORD",
        "BYBIT_API_KEY",
        "BYBIT_API_SECRET",
        "FXCM_API_TOKEN",
        "GEMINI_API_KEY",
        "DISCORD_TOKEN",
        "TELEGRAM_TOKEN",
        "AMP_TOKEN",
    ]

    # Required variables
    required_variables = [
        "NODE_ENV",
        "LOG_LEVEL",
        "PORT",
        "API_PORT",
        "GEMINI_MODEL",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "REDIS_HOST",
        "REDIS_PORT",
    ]

    # Required environments
    required_environments = ["development", "staging", "production"]

    # Check secrets
    print("\nRepository Secrets Check:")
    current_secrets = list_repository_secrets()
    for secret in required_secrets:
        exists = secret in current_secrets
        print(f"   {'[OK]' if exists else '[MISSING]'} {secret}")

    # Check variables
    print("\nRepository Variables Check:")
    current_variables = list_repository_variables()
    for variable in required_variables:
        exists = variable in current_variables
        print(f"   {'[OK]' if exists else '[MISSING]'} {variable}")

    # Check environments
    print("\nEnvironments Check:")
    current_environments = list_environments()
    for env in required_environments:
        exists = env in current_environments
        print(f"   {'[OK]' if exists else '[MISSING]'} {env}")

    # Summary
    missing_secrets = [s for s in required_secrets if s not in current_secrets]
    missing_variables = [v for v in required_variables if v not in current_variables]
    missing_environments = [
        e for e in required_environments if e not in current_environments
    ]

    print("\nSummary:")
    print("=" * 20)

    if not missing_secrets and not missing_variables and not missing_environments:
        print("[SUCCESS] All secrets, variables, and environments are configured!")
    else:
        print("[WARNING] Missing configuration:")
        if missing_secrets:
            print(f"   Secrets: {', '.join(missing_secrets)}")
        if missing_variables:
            print(f"   Variables: {', '.join(missing_variables)}")
        if missing_environments:
            print(f"   Environments: {', '.join(missing_environments)}")

    print("\nNext Steps:")
    print("1. Run: setup-github-secrets-manual.bat")
    print("2. Follow: GITHUB_SECRETS_SETUP_GUIDE.md")
    print("3. Test CI/CD pipeline")


if __name__ == "__main__":
    main()
