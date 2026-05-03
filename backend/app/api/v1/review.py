from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.review import generate_weekly_review
from pydantic import BaseModel

router = APIRouter()

class ReviewResponse(BaseModel):
    summary: str

@router.get("/weekly", response_model=ReviewResponse)
async def get_weekly_review(db: Session = Depends(get_db)):
    summary = await generate_weekly_review(db)
    return ReviewResponse(summary=summary)
