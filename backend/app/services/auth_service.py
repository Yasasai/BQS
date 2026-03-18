import os
import jwt
from jwt import PyJWKClient
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from backend.app.core.logging_config import get_logger
from typing import Optional

logger = get_logger("auth_service")

# --- Azure AD Settings ---
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "common")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "mock-client-id")
AZURE_JWKS_URI = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"

# Used to fetch keys to decode Azure's token
try:
    jwks_client = PyJWKClient(AZURE_JWKS_URI)
except Exception:
    jwks_client = None

# --- Local JWT Settings ---
SECRET_KEY = os.getenv("JWT_SECRET", "bqs-super-secret-key-1234567890")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

def verify_azure_token(token: str) -> dict:
    """
    Decodes and validates an incoming Azure AD RS256 token.
    Provides a bypass for development mode 'mock_azure_token_'.
    Returns the decoded token payload.
    """
    # 1) Development bypass
    if os.getenv("VITE_DEV_MODE", "true").lower() == "true" or token.startswith("mock_azure_token_"):
        logger.info("Using mock Azure AD bypass for SSO token.")
        email = token.replace("mock_azure_token_", "") if token.startswith("mock_azure_token_") else token
        return {"preferred_username": email, "email": email}

    # 2) Real Azure Token Verification
    if not jwks_client:
        raise HTTPException(status_code=500, detail="SSO configuration is incomplete.")

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        data = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AZURE_CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0"
        )
        return dict(data)
    except jwt.PyJWTError as e:
        logger.error(f"Azure token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid SSO token")
    except Exception as e:
        logger.error(f"Unexpected error validating token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid SSO token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate an encoded local JWT token containing the user_id and role_codes.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
