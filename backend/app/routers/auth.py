
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import AppUser, UserRole, Role
from backend.app.core.auth import create_access_token, get_current_user
from backend.app.services.auth_service import verify_azure_token, create_access_token as sso_create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserRead(BaseModel):
    user_id: str
    display_name: str
    email: str
    roles: List[str]

class UserCreate(BaseModel):
    email: str
    display_name: str
    roles: List[str]  # e.g., ["PH"], ["SH"], ["SA"], ["SP"], ["GH"]

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str

class SSOLoginRequest(BaseModel):
    sso_token: str

class DevLoginRequest(BaseModel):
    role_code: str

@router.get("/users", response_model=List[UserRead])
def get_all_users(role: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Get all active users, optionally filtered by role.
    
    Args:
        role: Optional role code to filter by (e.g., 'PH', 'SH', 'SA', 'SP')
        db: Database session
    
    Returns:
        List of users matching the criteria
    """
    query = db.query(AppUser).filter(AppUser.is_active == True)
    
    # If role filter is provided, join with UserRole and Role tables
    if role:
        query = query.join(UserRole).join(Role).filter(Role.role_code == role)
    
    users = query.all()
    result = []
    for u in users:
        role_codes = [ur.role.role_code for ur in u.user_roles]
        result.append({
            "user_id": u.user_id,
            "display_name": u.display_name,
            "email": u.email,
            "roles": role_codes
        })
    return result

@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with specified roles.
    
    Args:
        user: User data including email, display_name, and roles
        db: Database session
    
    Returns:
        Created user data
    """
    # Check if user already exists
    existing = db.query(AppUser).filter(AppUser.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create new user
    new_user = AppUser(
        email=user.email,
        display_name=user.display_name,
        is_active=True
    )
    db.add(new_user)
    db.flush()  # Generate user_id
    
    # Assign roles
    for role_code in user.roles:
        role = db.query(Role).filter(Role.role_code == role_code).first()
        if role:
            user_role = UserRole(user_id=new_user.user_id, role_id=role.role_id)
            db.add(user_role)
    
    db.commit()
    db.refresh(new_user)
    
    # Return formatted response
    role_codes = [ur.role.role_code for ur in new_user.user_roles]
    return {
        "user_id": new_user.user_id,
        "display_name": new_user.display_name,
        "email": new_user.email,
        "roles": role_codes
    }

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Simulated login using just email. Returns a JWT token if email exists.
    """
    user = db.query(AppUser).filter(AppUser.email == login_data.email, AppUser.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or inactive user")
    
    # Still issues old-style JWT if this route is used directly, but we mainly use sso-login now
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/sso-login", response_model=Token)
def sso_login(login_data: SSOLoginRequest, db: Session = Depends(get_db)):
    """
    Accepts an Azure AD SSO token, validates it, and issues a local JWT.
    """
    # 1. Verify SSO token
    payload = verify_azure_token(login_data.sso_token)
    email = payload.get("preferred_username") or payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="SSO token missing email")

    # 2. Find user in the local database
    user = db.query(AppUser).filter(AppUser.email == email, AppUser.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not provisioned in application")

    # 3. Collect role codes
    role_codes = [ur.role.role_code for ur in user.user_roles]

    # 4. Issue local JWT using auth_service logic
    access_token = sso_create_access_token(data={
        "sub": user.email, 
        "user_id": user.user_id, 
        "roles": role_codes
    })
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/dev-login", response_model=Token)
def dev_login(login_data: DevLoginRequest, db: Session = Depends(get_db)):
    """
    Development-only login bypass. Finds the first active user with the requested role
    and issues a valid JWT.
    """
    # Find the first active user with the requested role
    user = db.query(AppUser).join(UserRole).join(Role).filter(
        Role.role_code == login_data.role_code,
        AppUser.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=404, 
            detail=f"No active user found with role {login_data.role_code}"
        )

    # Collect role codes
    role_codes = [ur.role.role_code for ur in user.user_roles]

    # Issue local JWT using auth_service logic
    access_token = sso_create_access_token(data={
        "sub": user.email, 
        "user_id": user.user_id, 
        "roles": role_codes
    })
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def get_token(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Alias for /login to provide a standard token endpoint.
    """
    return login(login_data, db)

@router.get("/me", response_model=UserRead)
def get_me(current_user: AppUser = Depends(get_current_user)):
    """
    Get current logged-in user info based on JWT.
    """
    role_codes = [ur.role.role_code for ur in current_user.user_roles]
    return {
        "user_id": current_user.user_id,
        "display_name": current_user.display_name,
        "email": current_user.email,
        "roles": role_codes
    }
