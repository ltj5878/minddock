from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User
from sqlalchemy import select

router = APIRouter()

class UserSettingsUpdate(BaseModel):
    notion_access_token: str | None = None
    notion_default_database_id: str | None = None
    preferred_llm: str | None = None
    custom_llm_api_base: str | None = None
    custom_llm_api_key: str | None = None
    custom_llm_model_name: str | None = None

class UserSettingsResponse(BaseModel):
    email: str
    notion_connected: bool
    notion_default_database_id: str | None
    preferred_llm: str
    custom_llm_api_base: str | None
    custom_llm_model_name: str | None

@router.get("", response_model=UserSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    # For now, we assume a single user as per current dev state
    user = db.scalar(select(User).limit(1))
    if not user:
        # Create a default user if none exists (for dev)
        user = User(email="dev@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return UserSettingsResponse(
        email=user.email,
        notion_connected=bool(user.notion_access_token),
        notion_default_database_id=user.notion_default_database_id,
        preferred_llm=user.preferred_llm,
        custom_llm_api_base=user.custom_llm_api_base,
        custom_llm_model_name=user.custom_llm_model_name
    )

@router.patch("", response_model=UserSettingsResponse)
def update_settings(req: UserSettingsUpdate, db: Session = Depends(get_db)):
    user = db.scalar(select(User).limit(1))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if req.notion_access_token is not None:
        user.notion_access_token = req.notion_access_token
    if req.notion_default_database_id is not None:
        user.notion_default_database_id = req.notion_default_database_id
    if req.preferred_llm is not None:
        user.preferred_llm = req.preferred_llm
    if req.custom_llm_api_base is not None:
        user.custom_llm_api_base = req.custom_llm_api_base
    if req.custom_llm_api_key is not None:
        user.custom_llm_api_key = req.custom_llm_api_key
    if req.custom_llm_model_name is not None:
        user.custom_llm_model_name = req.custom_llm_model_name
        
    db.commit()
    db.refresh(user)
    
    return UserSettingsResponse(
        email=user.email,
        notion_connected=bool(user.notion_access_token),
        notion_default_database_id=user.notion_default_database_id,
        preferred_llm=user.preferred_llm,
        custom_llm_api_base=user.custom_llm_api_base,
        custom_llm_model_name=user.custom_llm_model_name
    )
