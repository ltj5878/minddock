from typing import Any

import httpx
from pydantic import BaseModel

from app.core.config import settings
from app.services.classifier import NoteClassification


NOTION_VERSION = "2022-06-28"


class NotionWriteResult(BaseModel):
    synced: bool
    page_id: str | None = None
    url: str | None = None
    warning: str | None = None


class NotionPageContent(BaseModel):
    page_id: str
    url: str | None
    title: str
    content: str
    source_url: str | None = None


async def create_notion_note(
    *,
    database_id: str | None,
    classification: NoteClassification,
    content: str,
    source_url: str | None = None,
) -> NotionWriteResult:
    token = settings.notion_integration_token
    target_database_id = database_id or settings.notion_notes_database_id
    if not token or not target_database_id:
        return NotionWriteResult(
            synced=False,
            warning="Notion token or notes database id is not configured.",
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(base_url="https://api.notion.com/v1", timeout=30) as client:
        db_response = await client.get(f"/databases/{target_database_id}", headers=headers)
        db_response.raise_for_status()
        database = db_response.json()
        properties = _build_properties(database.get("properties", {}), classification, source_url)
        if not properties:
            return NotionWriteResult(
                synced=False,
                warning="Could not find a title property in the Notion database.",
            )

        page_response = await client.post(
            "/pages",
            headers=headers,
            json={
                "parent": {"database_id": target_database_id},
                "properties": properties,
                "children": _build_children(classification, content),
            },
        )
        page_response.raise_for_status()
        page = page_response.json()
        return NotionWriteResult(synced=True, page_id=page.get("id"), url=page.get("url"))


async def fetch_notion_notes(database_id: str | None = None, limit: int = 50) -> list[NotionPageContent]:
    token = settings.notion_integration_token
    target_database_id = database_id or settings.notion_notes_database_id
    if not token or not target_database_id:
        raise RuntimeError("Notion token or notes database id is not configured.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(base_url="https://api.notion.com/v1", timeout=30) as client:
        response = await client.post(
            f"/databases/{target_database_id}/query",
            headers=headers,
            json={"page_size": min(limit, 100)},
        )
        response.raise_for_status()
        pages = response.json().get("results", [])

        notes: list[NotionPageContent] = []
        for page in pages:
            blocks = await _fetch_blocks(client, headers, page["id"])
            notes.append(
                NotionPageContent(
                    page_id=page["id"],
                    url=page.get("url"),
                    title=_extract_page_title(page),
                    content="\n\n".join(blocks).strip() or _extract_page_title(page),
                    source_url=page.get("url"),
                )
            )
        return notes


def _build_properties(
    schema: dict[str, Any],
    classification: NoteClassification,
    source_url: str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for name, spec in schema.items():
        prop_type = spec.get("type")
        normalized = _normalize_name(name)
        if prop_type == "title":
            result[name] = {"title": [_text(classification.title)]}
        elif prop_type == "rich_text" and normalized in {"summary", "摘要", "description", "描述"}:
            result[name] = {"rich_text": [_text(classification.summary)]}
        elif prop_type == "select" and normalized in {"type", "类型", "category", "分类"}:
            result[name] = {"select": {"name": classification.type}}
        elif prop_type == "multi_select" and normalized in {"tags", "标签", "tag"}:
            result[name] = {"multi_select": [{"name": tag} for tag in classification.tags]}
        elif prop_type == "url" and source_url and normalized in {"url", "source", "sourceurl", "来源"}:
            result[name] = {"url": source_url}

    return result


async def _fetch_blocks(
    client: httpx.AsyncClient, headers: dict[str, str], block_id: str
) -> list[str]:
    response = await client.get(f"/blocks/{block_id}/children", headers=headers)
    response.raise_for_status()
    blocks = response.json().get("results", [])
    texts: list[str] = []
    for block in blocks:
        block_type = block.get("type")
        value = block.get(block_type, {}) if block_type else {}
        rich_text = value.get("rich_text", [])
        plain = "".join(part.get("plain_text", "") for part in rich_text).strip()
        if plain:
            texts.append(plain)
    return texts


def _extract_page_title(page: dict[str, Any]) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            title = "".join(part.get("plain_text", "") for part in prop.get("title", []))
            if title.strip():
                return title.strip()
    return "Untitled Notion note"


def _build_children(classification: NoteClassification, content: str) -> list[dict[str, Any]]:
    children = [
        _paragraph(f"Summary: {classification.summary}"),
        _paragraph(f"Type: {classification.type}"),
    ]
    if classification.tags:
        children.append(_paragraph(f"Tags: {', '.join(classification.tags)}"))
    if classification.action_items:
        children.append(_paragraph("Action items:\n" + "\n".join(classification.action_items)))

    for chunk in _chunk_text(content, 1800):
        children.append(_paragraph(chunk))
    return children[:100]


def _paragraph(content: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [_text(content[:2000])]},
    }


def _text(content: str) -> dict[str, Any]:
    return {"type": "text", "text": {"content": content}}


def _chunk_text(content: str, size: int) -> list[str]:
    text = content.strip()
    return [text[index : index + size] for index in range(0, len(text), size)] or [""]


def _normalize_name(name: str) -> str:
    return name.replace(" ", "").replace("_", "").lower()
