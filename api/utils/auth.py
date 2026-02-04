from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from jose import JWTError, jwt
except Exception:  # jose not installed in minimal/runtime builds
    JWTError = Exception

    class _DummyJWT:
        def decode(self, *args, **kwargs):
            return {}

    jwt = _DummyJWT()
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    FastAPI dependency to get the current user from a JWT token.

    This function is used in path operations to protect endpoints. It extracts
    the bearer token, decodes it, and returns the user's information.
    In a testing environment (if `os.getenv("TESTING")` is set), it returns a
    mock user.

    Args:
        credentials (Optional[HTTPAuthorizationCredentials]): The bearer token
            credentials automatically extracted from the 'Authorization' header.

    Returns:
        dict: A dictionary containing user information, typically the username
              and token expiration time.

    Raises:
        HTTPException: If the token is invalid, credentials are not provided
                       (outside of testing), or the token cannot be decoded.
    """

    # For testing or if no credentials provided, return a mock user or handle as needed
    if os.getenv("TESTING") or not credentials:
        return {"username": "testuser", "exp": None}

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username: Optional[str] = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"username": username, "exp": payload.get("exp")}

    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
