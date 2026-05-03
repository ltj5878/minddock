"""Migrate data from SQLite (minddock.db) to MySQL (minddock)."""

import json
import sys
from pathlib import Path

import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
SQLITE_PATH = BACKEND_DIR / "minddock.db"
MYSQL_URL = "mysql+pymysql://root@localhost:3306/minddock"

sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base
from app.models.user import User
from app.models.note import Note
from app.models.project import Project, Task
from app.models.embedding import Embedding


def ensure_mysql_database():
    conn = pymysql.connect(host="localhost", user="root", port=3306)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE DATABASE IF NOT EXISTS minddock "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        print("[OK] Database 'minddock' ready.")
    finally:
        conn.close()


def migrate():
    if not SQLITE_PATH.exists():
        print(f"[SKIP] SQLite file not found: {SQLITE_PATH}")
        print("       Will create empty tables in MySQL.")
        ensure_mysql_database()
        mysql_engine = create_engine(MYSQL_URL)
        Base.metadata.create_all(bind=mysql_engine)
        print("[OK] MySQL tables created.")
        return

    ensure_mysql_database()

    sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
    sqlite_session = sessionmaker(bind=sqlite_engine)()

    mysql_engine = create_engine(
        MYSQL_URL, pool_size=5, max_overflow=10, pool_recycle=1800
    )
    Base.metadata.create_all(bind=mysql_engine)
    print("[OK] MySQL tables created.")

    mysql_session = sessionmaker(bind=mysql_engine)()

    try:
        # 1. Migrate users
        result = sqlite_session.execute(text("SELECT * FROM users"))
        cols = list(result.keys())
        users = result.fetchall()
        for row in users:
            data = dict(zip(cols, row))
            mysql_session.merge(User(**data))
        mysql_session.commit()
        print(f"[OK] Migrated {len(users)} users.")

        # 2. Migrate projects (before notes, due to FK)
        result = sqlite_session.execute(text("SELECT * FROM projects"))
        cols = list(result.keys())
        projects = result.fetchall()
        for row in projects:
            data = dict(zip(cols, row))
            mysql_session.merge(Project(**data))
        mysql_session.commit()
        print(f"[OK] Migrated {len(projects)} projects.")

        # 3. Migrate notes
        result = sqlite_session.execute(text("SELECT * FROM notes"))
        cols = list(result.keys())
        notes = result.fetchall()
        for row in notes:
            data = dict(zip(cols, row))
            if isinstance(data.get("tags"), str):
                data["tags"] = json.loads(data["tags"])
            if isinstance(data.get("action_items"), str):
                data["action_items"] = json.loads(data["action_items"])
            mysql_session.merge(Note(**data))
        mysql_session.commit()
        print(f"[OK] Migrated {len(notes)} notes.")

        # 4. Migrate tasks
        result = sqlite_session.execute(text("SELECT * FROM tasks"))
        cols = list(result.keys())
        tasks = result.fetchall()
        for row in tasks:
            data = dict(zip(cols, row))
            mysql_session.merge(Task(**data))
        mysql_session.commit()
        print(f"[OK] Migrated {len(tasks)} tasks.")

        # 5. Migrate embeddings
        result = sqlite_session.execute(text("SELECT * FROM embeddings"))
        cols = list(result.keys())
        embeddings = result.fetchall()
        for row in embeddings:
            data = dict(zip(cols, row))
            if isinstance(data.get("embedding"), str):
                data["embedding"] = json.loads(data["embedding"])
            mysql_session.merge(Embedding(**data))
        mysql_session.commit()
        print(f"[OK] Migrated {len(embeddings)} embeddings.")

        print("\nMigration complete!")

    except Exception as e:
        mysql_session.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        sqlite_session.close()
        mysql_session.close()


if __name__ == "__main__":
    migrate()
