from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import AppUser, Role, UserRole

router = APIRouter(prefix="/api/users", tags=["users"])

# --- Pydantic Models ---
class UserRoleInput(BaseModel):
    role_code: str

class UserCreate(BaseModel):
    email: str
    display_name: str
    roles: List[str]  # e.g. ["SA", "PRACTICE_HEAD"]

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None

class UserRead(BaseModel):
    user_id: str
    email: str
    display_name: str
    is_active: bool
    roles: List[str]

# --- Endpoints ---

@router.get("/", response_model=List[UserRead])
def list_users(role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AppUser)
    
    if role:
        query = query.join(UserRole).join(Role).filter(Role.role_code == role)
        
    users = query.all()
    results = []
    for u in users:
        role_codes = [ur.role.role_code for ur in u.user_roles]
        results.append({
            "user_id": u.user_id,
            "email": u.email,
            "display_name": u.display_name,
            "is_active": u.is_active,
            "roles": role_codes
        })
    return results

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(AppUser).filter(AppUser.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = AppUser(
        email=user.email,
        display_name=user.display_name
    )
    db.add(new_user)
    db.flush() # Generate ID

    # Assign Roles
    for r_code in user.roles:
        role = db.query(Role).filter(Role.role_code == r_code).first()
        if role:
            user_role = UserRole(user_id=new_user.user_id, role_id=role.role_id)
            db.add(user_role)
    
    db.commit()
    db.refresh(new_user)
    
    # Return formatted
    role_codes = [ur.role.role_code for ur in new_user.user_roles]
    return {
        "user_id": new_user.user_id,
        "email": new_user.email,
        "display_name": new_user.display_name,
        "is_active": new_user.is_active,
        "roles": role_codes
    }

@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: str, updates: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if updates.display_name is not None:
        db_user.display_name = updates.display_name
    if updates.is_active is not None:
        db_user.is_active = updates.is_active
    
    if updates.roles is not None:
        # Clear existing roles
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        # Add new roles
        for r_code in updates.roles:
            role = db.query(Role).filter(Role.role_code == r_code).first()
            if role:
                db.add(UserRole(user_id=user_id, role_id=role.role_id))

    db.commit()
    db.refresh(db_user)

    role_codes = [ur.role.role_code for ur in db_user.user_roles]
    return {
        "user_id": db_user.user_id,
        "email": db_user.email,
        "display_name": db_user.display_name,
        "is_active": db_user.is_active,
        "roles": role_codes
    }
