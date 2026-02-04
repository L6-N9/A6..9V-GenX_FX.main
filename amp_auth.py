#!/usr/bin/env python3
"""
AMP Authentication Module
Handles user authentication and session management
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class AMPAuth:
    """
    Handles user authentication and session management for the AMP system.

    This class manages a session token by storing it in a local JSON file,
    and provides methods to authenticate, check authentication status,
    and get authentication headers.

    Attributes:
        auth_file (Path): The path to the authentication JSON file.
        session_token (Optional[str]): The current session token.
        user_id (Optional[str]): The current user ID.
        session_hash (Optional[str]): The hash part of the session token.
    """

    def __init__(self):
        """Initializes the AMPAuth manager."""
        self.auth_file = Path("amp_auth.json")
        self.session_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.session_hash: Optional[str] = None

    def parse_token(self, token: str) -> Dict[str, str]:
        """
        Parses a session token into its components.

        Args:
            token (str): The session token to parse.

        Returns:
            Dict[str, str]: A dictionary containing the user ID, session hash,
                            and the full token with prefix. Returns an empty
                            dictionary if parsing fails.
        """
        try:
            if token.startswith("sgamp_user_"):
                token = token[11:]

            parts = token.split("_", 1)
            if len(parts) == 2:
                user_id, session_hash = parts
                return {
                    "user_id": user_id,
                    "session_hash": session_hash,
                    "full_token": f"sgamp_user_{token}",
                }
            else:
                raise ValueError("Invalid token format")
        except Exception as e:
            print(f"Error parsing token: {e}")
            return {}

    def authenticate(self, token: str) -> bool:
        """
        Authenticates a user with the provided token and saves the session.

        Args:
            token (str): The session token for authentication.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        print("🔐 Authenticating with token...")
        token_data = self.parse_token(token)
        if not token_data:
            print("❌ Invalid token format")
            return False

        self.session_token = token_data["full_token"]
        self.user_id = token_data["user_id"]
        self.session_hash = token_data["session_hash"]

        auth_data = {
            "user_id": self.user_id,
            "session_hash": self.session_hash,
            "session_token": self.session_token,
            "authenticated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        }

        with open(self.auth_file, "w") as f:
            json.dump(auth_data, f, indent=2)

        print("✅ Authentication successful!")
        print(f"   User ID: {self.user_id}")
        print(f"   Session: {self.session_hash[:16]}...")
        print(f"   Expires: {auth_data['expires_at']}")
        return True

    def is_authenticated(self) -> bool:
        """
        Checks if a user is currently authenticated and the session is not expired.

        Returns:
            bool: True if authenticated and session is valid, False otherwise.
        """
        if not self.auth_file.exists():
            return False

        try:
            with open(self.auth_file, "r") as f:
                auth_data = json.load(f)

            expires_at = datetime.fromisoformat(auth_data["expires_at"])
            if datetime.now() > expires_at:
                print("⚠️ Session expired")
                self.logout()
                return False

            self.user_id = auth_data["user_id"]
            self.session_hash = auth_data["session_hash"]
            self.session_token = auth_data["session_token"]
            return True
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error checking authentication: {e}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Gets the authentication headers required for API requests.

        Returns:
            Dict[str, str]: A dictionary of authentication headers.
        """
        if not self.is_authenticated():
            return {}

        return {
            "Authorization": f"Bearer {self.session_token}",
            "X-User-ID": self.user_id or "",
            "X-Session-Hash": self.session_hash or "",
        }

    def logout(self):
        """Logs out the user by deleting the session file."""
        if self.auth_file.exists():
            self.auth_file.unlink()

        self.session_token = None
        self.user_id = None
        self.session_hash = None
        print("✅ Logged out successfully")

    def get_user_info(self) -> Dict[str, Any]:
        """
        Gets information about the currently authenticated user.

        Returns:
            Dict[str, Any]: A dictionary with user information.
        """
        if not self.is_authenticated():
            return {"authenticated": False}

        return {
            "user_id": self.user_id,
            "session_hash": self.session_hash,
            "authenticated": True,
        }


# Global auth instance
amp_auth = AMPAuth()


def authenticate_user(token: str) -> bool:
    """A convenience function to authenticate a user with a token."""
    return amp_auth.authenticate(token)


def check_auth() -> bool:
    """A convenience function to check if a user is authenticated."""
    return amp_auth.is_authenticated()


def get_auth_headers() -> Dict[str, str]:
    """A convenience function to get authentication headers."""
    return amp_auth.get_auth_headers()


def logout_user():
    """A convenience function to log out the current user."""
    amp_auth.logout()


def get_user_info() -> Dict[str, Any]:
    """A convenience function to get the current user's information."""
    return amp_auth.get_user_info()
