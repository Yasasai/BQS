import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import AppUser, Role

# --- JWT SETTINGS ---
SECRET_KEY = os.getenv("JWT_SECRET", "bqs-super-secret-key-1234567890")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 # 8 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generate an encoded JWT token.
    (Maintained for legacy / fallback if needed, but sso-login uses auth_service)
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to validate the bearer token and return the application user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        # Support the new token format which includes user_id
        user_id: str = payload.get("user_id")
        
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Query using user_id if present, else fall back to email
    if user_id:
        user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    else:
        user = db.query(AppUser).filter(AppUser.email == email).first()
        
    if user is None:
        raise credentials_exception
    
    # Check if active
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")
        
    return user

def require_role(allowed_roles: List[str]):
    """
    Dependency factory to enforce RBAC.
    """
    async def role_checker(current_user: AppUser = Depends(get_current_user)):
        user_role_codes = [ur.role.role_code for ur in current_user.user_roles]
        if not any(role in user_role_codes for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker
