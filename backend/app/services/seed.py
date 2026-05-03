import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Note, Project, Task


ROOT_DIR = Path(__file__).resolve().parents[3]
MOCK_NOTES_PATH = ROOT_DIR / "frontend" / "src" / "mock" / "notes.json"
MOCK_PROJECTS_PATH = ROOT_DIR / "frontend" / "src" / "mock" / "projects.json"
MOCK_TASKS_PATH = ROOT_DIR / "frontend" / "src" / "mock" / "tasks.json"


def seed_mock_notes(db: Session) -> None:
    _seed_projects(db)
    _seed_tasks(db)

    existing = db.scalar(select(Note).limit(1))
    if existing or not MOCK_NOTES_PATH.exists():
        return

    notes = json.loads(MOCK_NOTES_PATH.read_text(encoding="utf-8"))
    for item in notes:
        db.add(
            Note(
                id=item["id"],
                title=item["title"],
                content=item["content"],
                summary=item.get("summary") or "",
                type=item.get("type") or "note",
                tags=item.get("tags") or [],
                project_id=item.get("projectId"),
                source_url=item.get("sourceUrl"),
                source_type=item.get("sourceType") or "manual",
                action_items=item.get("actionItems") or [],
                created_at=_parse_datetime(item["createdAt"]),
                updated_at=_parse_datetime(item["updatedAt"]),
                classification_provider="mock-seed",
            )
        )
    db.commit()


def _seed_projects(db: Session) -> None:
    existing = db.scalar(select(Project).limit(1))
    if existing or not MOCK_PROJECTS_PATH.exists():
        return

    projects = json.loads(MOCK_PROJECTS_PATH.read_text(encoding="utf-8"))
    for item in projects:
        db.add(
            Project(
                id=item["id"],
                name=item["name"],
                goal=item.get("goal") or "",
                status=item.get("status") or "active",
                notion_project_page_id=item.get("notionProjectPageId"),
                created_at=_parse_datetime(item["createdAt"]),
                updated_at=_parse_datetime(item["updatedAt"]),
            )
        )
    db.commit()


def _seed_tasks(db: Session) -> None:
    existing = db.scalar(select(Task).limit(1))
    if existing or not MOCK_TASKS_PATH.exists():
        return

    tasks = json.loads(MOCK_TASKS_PATH.read_text(encoding="utf-8"))
    for item in tasks:
        db.add(
            Task(
                id=item["id"],
                title=item["title"],
                status=item.get("status") or "todo",
                priority=item.get("priority") or "medium",
                due_date=datetime.fromisoformat(item["dueDate"]).date()
                if item.get("dueDate")
                else None,
                project_id=item.get("projectId"),
                source_note_id=item.get("sourceNoteId"),
                created_at=_parse_datetime(item["createdAt"]),
                updated_at=_parse_datetime(item["updatedAt"]),
            )
        )
    db.commit()


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
