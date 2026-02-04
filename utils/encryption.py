import logging
from typing import Optional

from cryptography.fernet import Fernet

from api.config import settings

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data using Fernet symmetric encryption.
    """

    def __init__(self, key: Optional[str] = None):
        """
        Initialize the EncryptionManager.

        Args:
            key (Optional[str]): The encryption key. If not provided, it attempts to load
                                 from settings.CRYPTION_KEY.
        """
        self.key = key or settings.CRYPTION_KEY
        self.cipher_suite = None

        if self.key:
            try:
                self.cipher_suite = Fernet(self.key)
            except Exception as e:
                logger.error(f"Error initializing encryption key: {e}")

    def encrypt(self, data: str) -> str:
        """
        Encrypts a string.

        Args:
            data (str): The string to encrypt.

        Returns:
            str: The encrypted string (base64 encoded).

        Raises:
            ValueError: If encryption key is not set or invalid.
        """
        if not self.cipher_suite:
            raise ValueError("Encryption key is not configured.")

        if not data:
            return ""

        encrypted_bytes = self.cipher_suite.encrypt(data.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, token: str) -> str:
        """
        Decrypts an encrypted string.

        Args:
            token (str): The encrypted string.

        Returns:
            str: The decrypted string.

        Raises:
            ValueError: If encryption key is not set or invalid.
            cryptography.fernet.InvalidToken: If the token is invalid.
        """
        if not self.cipher_suite:
            raise ValueError("Encryption key is not configured.")

        if not token:
            return ""

        decrypted_bytes = self.cipher_suite.decrypt(token.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")


# Global instance
encryption_manager = EncryptionManager()
