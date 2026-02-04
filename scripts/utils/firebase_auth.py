#!/usr/bin/env python3
"""Firebase Authentication Helper for GenX FX"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FirebaseAuth:
    """
    A helper class for managing Firebase authentication.
    """

    def __init__(self):
        """
        Initializes the FirebaseAuth class by loading the Firebase Auth UID from environment variables.
        """
        self.auth_uid = os.getenv("FIREBASE_AUTH_UID")

    def get_auth_uid(self) -> str:
        """
        Gets the Firebase authentication UID.

        Returns:
            str: The Firebase authentication UID.
        """
        return self.auth_uid

    def is_authenticated(self) -> bool:
        """
        Checks if Firebase authentication is configured by verifying the presence of the auth UID.

        Returns:
            bool: True if authenticated, False otherwise.
        """
        return bool(self.auth_uid)

    def get_auth_token(self) -> str:
        """
        Gets the authentication token for API calls. In this implementation, it's the same as the UID.

        Returns:
            str: The authentication token.
        """
        return self.auth_uid


if __name__ == "__main__":
    auth = FirebaseAuth()
    print(f"Firebase Auth UID: {auth.get_auth_uid()}")
    print(f"Authenticated: {auth.is_authenticated()}")
