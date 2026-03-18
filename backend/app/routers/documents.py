from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models import DocumentCategory, AppUser
from backend.app.core.auth import get_current_user

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/categories")
def get_document_categories(db: Session = Depends(get_db), current_user: AppUser = Depends(get_current_user)):
    categories = db.query(DocumentCategory).filter(DocumentCategory.is_active == True).all()
    if not categories:
        # Default fallback if no categories exist in DB
        return [
            {"category_id": "1", "label_name": "RFP"},
            {"category_id": "2", "label_name": "Proposal"},
            {"category_id": "3", "label_name": "RLS"},
            {"category_id": "4", "label_name": "Pricing Worksheet"},
            {"category_id": "5", "label_name": "Customer Contract"}
        ]
    return [{"category_id": c.category_id, "label_name": c.label_name} for c in categories]
