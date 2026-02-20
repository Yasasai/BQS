
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import AppUser, UserRole, Role

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
