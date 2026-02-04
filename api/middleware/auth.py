from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

try:
    from jose import JWTError, jwt
except Exception:
    JWTError = Exception

    class _DummyJWT:
        def decode(self, *args, **kwargs):
            return {}

        def encode(self, *args, **kwargs):
            return ""

    jwt = _DummyJWT()
import logging
from datetime import datetime, timedelta
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthMiddleware:
    """
    Authentication middleware for FastAPI to handle JWT-based security.

    This class provides methods to create and verify JWTs and acts as a
    middleware to protect endpoints.

    Attributes:
        secret_key (str): The secret key for encoding and decoding JWTs.
        algorithm (str): The algorithm used for JWT operations (e.g., 'HS256').
        access_token_expire_minutes (int): The default expiry time for access tokens.
    """

    def __init__(self):
        """Initializes the AuthMiddleware with settings from the config."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Creates a new JWT access token.

        Args:
            data (dict): The data to be encoded in the token (payload).
            expires_delta (Optional[timedelta]): An optional timedelta object to
                set a custom expiration time. If None, the default is used.

        Returns:
            str: The encoded JWT as a string.
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """
        Verifies a JWT token and extracts its payload.

        Args:
            token (str): The JWT token to verify.

        Returns:
            dict: A dictionary containing the username and expiration time from the token.

        Raises:
            HTTPException: If the token is invalid, expired, or the credentials
                           cannot be validated.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
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

    async def __call__(self, request: Request):
        """
        Executes the middleware logic for each incoming request.

        This method checks for a bearer token in the request's 'Authorization'
        header, verifies it, and attaches the user information to the request state.
        It skips authentication for predefined public endpoints.

        Args:
            request (Request): The incoming FastAPI request object.

        Raises:
            HTTPException: If authentication fails.
        """
        # Skip auth for public endpoints
        public_endpoints = ["/", "/docs", "/redoc", "/openapi.json", "/health"]

        if request.url.path in public_endpoints:
            return

        try:
            authorization: HTTPAuthorizationCredentials = await security(request)
            user = self.verify_token(authorization.credentials)
            request.state.current_user = user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication middleware error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )


auth_middleware = AuthMiddleware()
