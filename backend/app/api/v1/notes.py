from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Note, Project
from app.services.classifier import NoteClassification, classify_note
from app.services.embeddings import rebuild_note_embeddings
from app.services.notion import NotionWriteResult, create_notion_note, fetch_notion_notes

NoteType = Literal["note", "idea", "reference", "meeting", "journal", "task_note"]
router = APIRouter()


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    summary: str
    type: NoteType
    tags: list[str]
    projectId: str | None
    sourceUrl: str | None
    sourceType: str
    actionItems: list[str]
    notionPageId: str | None
    notionUrl: str | None
    classificationProvider: str
    createdAt: datetime
    updatedAt: datetime


class NotesListResponse(BaseModel):
    notes: list[NoteResponse]
    total: int


class CaptureNoteRequest(BaseModel):
    content: str = Field(min_length=1, max_length=50000)
    title: str | None = Field(default=None, max_length=160)
    sourceUrl: str | None = None
    sourceType: str = "direct"
    projectId: str | None = None
    writeToNotion: bool = True
    notionDatabaseId: str | None = None


class CaptureNoteResponse(BaseModel):
    note: NoteResponse
    classification: NoteClassification
    notion: NotionWriteResult
    warnings: list[str] = Field(default_factory=list)


class SyncNotionRequest(BaseModel):
    notionDatabaseId: str | None = None
    limit: int = Field(default=50, ge=1, le=100)


class SyncNotionResponse(BaseModel):
    imported: int
    updated: int
    embeddedChunks: int
    warnings: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    summary: str | None = None
    type: NoteType | None = None
    tags: list[str] | None = None
    projectId: str | None = None


@router.get("", response_model=NotesListResponse)
def list_notes(db: Session = Depends(get_db)):
    notes = db.scalars(select(Note).order_by(desc(Note.created_at))).all()
    return NotesListResponse(notes=[_to_response(note) for note in notes], total=len(notes))


@router.post("/capture", response_model=CaptureNoteResponse)
async def capture_note(req: CaptureNoteRequest, db: Session = Depends(get_db)):
    classification_result = await classify_note(req.content, req.title)
    classification = classification_result.classification
    note = Note(
        title=classification.title,
        content=req.content,
        summary=classification.summary,
        type=classification.type,
        tags=classification.tags,
        project_id=req.projectId or _infer_project_id(db, classification, req.content),
        source_url=req.sourceUrl,
        source_type=req.sourceType,
        action_items=classification.action_items,
        classification_provider=classification_result.provider,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    await rebuild_note_embeddings(db, note)

    warnings = [classification_result.warning] if classification_result.warning else []
    notion = NotionWriteResult(synced=False, warning="Notion sync disabled for this request.")
    if req.writeToNotion:
        try:
            notion = await create_notion_note(
                database_id=req.notionDatabaseId,
                classification=classification,
                content=req.content,
                source_url=req.sourceUrl,
            )
            if notion.synced:
                note.notion_page_id = notion.page_id
                note.notion_url = notion.url
                db.commit()
                db.refresh(note)
            elif notion.warning:
                warnings.append(notion.warning)
        except Exception as exc:  # noqa: BLE001
            notion = NotionWriteResult(synced=False, warning=str(exc))
            warnings.append(f"Notion write failed: {exc}")

    return CaptureNoteResponse(
        note=_to_response(note),
        classification=classification,
        notion=notion,
        warnings=warnings,
    )


@router.post("/sync/notion", response_model=SyncNotionResponse)
async def sync_notion(req: SyncNotionRequest, db: Session = Depends(get_db)):
    imported = 0
    updated = 0
    embedded = 0
    warnings: list[str] = []

    pages = await fetch_notion_notes(req.notionDatabaseId, req.limit)
    for page in pages:
        existing = db.scalar(select(Note).where(Note.notion_page_id == page.page_id).limit(1))
        if existing:
            existing.title = page.title
            existing.content = page.content
            existing.source_url = page.source_url
            updated += 1
            note = existing
        else:
            classification_result = await classify_note(page.content, page.title)
            if classification_result.warning:
                warnings.append(classification_result.warning)
            classification = classification_result.classification
            note = Note(
                title=classification.title,
                content=page.content,
                summary=classification.summary,
                type=classification.type,
                tags=classification.tags,
                project_id=_infer_project_id(db, classification, page.content),
                source_url=page.source_url,
                source_type="notion_sync",
                action_items=classification.action_items,
                notion_page_id=page.page_id,
                notion_url=page.url,
                classification_provider=classification_result.provider,
            )
            db.add(note)
            imported += 1

        db.commit()
        db.refresh(note)
        embedded += await rebuild_note_embeddings(db, note)

    return SyncNotionResponse(
        imported=imported,
        updated=updated,
        embeddedChunks=embedded,
        warnings=warnings,
    )


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, req: NoteUpdate, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if req.title is not None:
        note.title = req.title
    if req.content is not None:
        note.content = req.content
    if req.summary is not None:
        note.summary = req.summary
    if req.type is not None:
        note.type = req.type
    if req.tags is not None:
        note.tags = req.tags
    if req.projectId is not None:
        note.project_id = req.projectId
        
    db.commit()
    db.refresh(note)
    
    if req.content is not None:
        await rebuild_note_embeddings(db, note)
        
    return _to_response(note)


@router.delete("/{note_id}")
def delete_note(note_id: str, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"status": "ok"}


def _to_response(note: Note) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        summary=note.summary or "",
        type=note.type,
        tags=note.tags or [],
        projectId=note.project_id,
        sourceUrl=note.source_url,
        sourceType=note.source_type,
        actionItems=note.action_items or [],
        notionPageId=note.notion_page_id,
        notionUrl=note.notion_url,
        classificationProvider=note.classification_provider,
        createdAt=note.created_at,
        updatedAt=note.updated_at,
    )


def _infer_project_id(
    db: Session, classification: NoteClassification, content: str
) -> str | None:
    projects = db.scalars(select(Project).where(Project.status == "active")).all()
    if not projects:
        return None
    haystack = " ".join([classification.title, classification.summary, content, *classification.tags]).lower()
    best_project: Project | None = None
    best_score = 0
    for project in projects:
        keywords = set(project.name.lower().replace("-", " ").split())
        keywords.update(project.goal.lower().replace("/", " ").replace("-", " ").split())
        keywords = {word for word in keywords if len(word) >= 3}
        score = sum(1 for word in keywords if word in haystack)
        if score > best_score:
            best_project = project
            best_score = score
    return best_project.id if best_project and best_score > 0 else None
