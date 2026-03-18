from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
from backend.app.core.database import get_db
from backend.app.models import AppUser, Role, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

# --- Pydantic Models ---
class UserRoleInput(BaseModel):
    role_code: str

class UserCreate(BaseModel):
    email: str
    display_name: str
    roles: List[str]  # e.g. ["SA", "PRACTICE_HEAD"]
    manager_email: Optional[str] = None
    geo_region: Optional[str] = None
    practice_name: Optional[str] = None

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None
    manager_email: Optional[str] = None
    geo_region: Optional[str] = None
    practice_name: Optional[str] = None

class UserRead(BaseModel):
    user_id: str
    email: str
    display_name: str
    is_active: bool
    roles: List[str]
    manager_email: Optional[str] = None
    geo_region: Optional[str] = None
    practice_name: Optional[str] = None

# --- Endpoints ---

@router.get("/", response_model=List[UserRead])
def list_users(role: Optional[str] = None, db: Session = Depends(get_db)):
    try:
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
                "roles": role_codes,
                "manager_email": u.manager_email,
                "geo_region": u.geo_region,
                "practice_name": u.practice_name
            })
        return results
    except Exception as e:
        logger.error(f"Users API Crashed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- Administrative CRUD (Restricted to GH) ---
from backend.app.core.auth import require_role

admin_router = APIRouter(prefix="/api/admin/users", tags=["admin_users"])

@admin_router.get("/", response_model=List[UserRead], dependencies=[Depends(require_role(["GH"]))])
def admin_list_users(db: Session = Depends(get_db)):
    users = db.query(AppUser).all()
    results = []
    for u in users:
        role_codes = [ur.role.role_code for ur in u.user_roles]
        results.append({
            "user_id": u.user_id,
            "email": u.email,
            "display_name": u.display_name,
            "is_active": u.is_active,
            "roles": role_codes,
            "manager_email": u.manager_email,
            "geo_region": u.geo_region,
            "practice_name": u.practice_name
        })
    return results

@admin_router.post("/", response_model=UserRead, dependencies=[Depends(require_role(["GH"]))])
def admin_create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(AppUser).filter(AppUser.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = AppUser(
        email=user.email,
        display_name=user.display_name,
        manager_email=user.manager_email,
        geo_region=user.geo_region,
        practice_name=user.practice_name
    )
    db.add(new_user)
    db.flush()

    for r_code in user.roles:
        role = db.query(Role).filter(Role.role_code == r_code).first()
        if role:
            db.add(UserRole(user_id=new_user.user_id, role_id=role.role_id))
    
    db.commit()
    db.refresh(new_user)
    
    return {
        "user_id": new_user.user_id,
        "email": new_user.email,
        "display_name": new_user.display_name,
        "is_active": new_user.is_active,
        "roles": [ur.role.role_code for ur in new_user.user_roles],
        "manager_email": new_user.manager_email,
        "geo_region": new_user.geo_region,
        "practice_name": new_user.practice_name
    }

@admin_router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(require_role(["GH"]))])
def admin_update_user(user_id: str, updates: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if updates.display_name is not None: db_user.display_name = updates.display_name
    if updates.is_active is not None: db_user.is_active = updates.is_active
    if updates.manager_email is not None: db_user.manager_email = updates.manager_email
    if updates.geo_region is not None: db_user.geo_region = updates.geo_region
    if updates.practice_name is not None: db_user.practice_name = updates.practice_name
    
    if updates.roles is not None:
        db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        for r_code in updates.roles:
            role = db.query(Role).filter(Role.role_code == r_code).first()
            if role:
                db.add(UserRole(user_id=user_id, role_id=role.role_id))

    db.commit()
    db.refresh(db_user)

    return {
        "user_id": db_user.user_id,
        "email": db_user.email,
        "display_name": db_user.display_name,
        "is_active": db_user.is_active,
        "roles": [ur.role.role_code for ur in db_user.user_roles],
        "manager_email": db_user.manager_email,
        "geo_region": db_user.geo_region,
        "practice_name": db_user.practice_name
    }

@admin_router.delete("/{user_id}", dependencies=[Depends(require_role(["GH"]))])
def admin_delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is referenced elsewhere (e.g. opportunities)
    # For now, let's just mark as inactive or hard delete if no constraints
    # AppUser.user_roles has no cascade delete in models.py, so we delete user_roles first
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
