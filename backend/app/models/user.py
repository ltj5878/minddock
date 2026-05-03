from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notion_access_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    notion_default_database_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    preferred_llm: Mapped[str] = mapped_column(String(32), default="openai")
    custom_llm_api_base: Mapped[str | None] = mapped_column(String(512), nullable=True)
    custom_llm_api_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    custom_llm_model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
