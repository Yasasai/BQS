
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models import AppUser

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserRead(BaseModel):
    user_id: str
    display_name: str
    email: str
    roles: List[str]

@router.get("/users", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(AppUser).filter(AppUser.is_active == True).all()
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
