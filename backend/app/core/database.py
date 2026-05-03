from collections.abc import Generator
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


DEFAULT_DATABASE_URL = "mysql+pymysql://root@localhost:3306/minddock"


class Base(DeclarativeBase):
    pass


database_url = settings.database_url or DEFAULT_DATABASE_URL

connect_args: dict = {}
engine_kwargs: dict = {}

if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif database_url.startswith("mysql"):
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_recycle"] = 1800

engine = create_engine(database_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
