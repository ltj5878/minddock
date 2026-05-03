from fastapi import APIRouter
from app.api.v1 import chat, notes, projects, settings, review

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
