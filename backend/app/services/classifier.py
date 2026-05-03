import json
import re
from typing import Literal

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings

NoteType = Literal["note", "idea", "reference", "meeting", "journal", "task_note"]


class NoteClassification(BaseModel):
    title: str = Field(max_length=120)
    summary: str = Field(max_length=600)
    type: NoteType
    tags: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    classification: NoteClassification
    provider: str
    warning: str | None = None


async def classify_note(content: str, title: str | None = None) -> ClassificationResult:
    if settings.openai_api_key:
        try:
            return await _classify_with_openai(content, title)
        except Exception as exc:  # noqa: BLE001
            fallback = _classify_heuristically(content, title)
            return ClassificationResult(
                classification=fallback,
                provider="heuristic",
                warning=f"OpenAI classification failed, used heuristic fallback: {exc}",
            )

    return ClassificationResult(
        classification=_classify_heuristically(content, title),
        provider="heuristic",
        warning="OPENAI_API_KEY is not configured, used heuristic classification.",
    )


async def _classify_with_openai(content: str, title: str | None) -> ClassificationResult:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    prompt = {
        "provided_title": title or "",
        "content": content[:12000],
        "allowed_types": ["note", "idea", "reference", "meeting", "journal", "task_note"],
        "instructions": (
            "Return concise JSON with title, summary, type, tags, action_items. "
            "Use Chinese if the source content is Chinese. tags should be 3-6 short labels."
        ),
    }
    response = await client.chat.completions.create(
        model=settings.openai_chat_model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You classify personal knowledge-base notes for MindDock.",
            },
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ],
        temperature=0.2,
    )
    raw = response.choices[0].message.content or "{}"
    try:
        parsed = NoteClassification.model_validate_json(raw)
    except ValidationError:
        parsed = NoteClassification.model_validate(json.loads(raw))
    return ClassificationResult(classification=_normalize_classification(parsed), provider="openai")


def _classify_heuristically(content: str, title: str | None) -> NoteClassification:
    text = content.strip()
    lower = text.lower()
    derived_title = title or _derive_title(text)

    note_type: NoteType = "note"
    if any(word in lower for word in ["todo", "next action", "任务", "待办", "行动项"]):
        note_type = "task_note"
    elif any(word in lower for word in ["meeting", "会议", "纪要"]):
        note_type = "meeting"
    elif any(word in lower for word in ["idea", "灵感", "想法", "可以做"]):
        note_type = "idea"
    elif any(word in lower for word in ["http://", "https://", "引用", "reference"]):
        note_type = "reference"
    elif any(word in lower for word in ["今天", "复盘", "日记", "journal"]):
        note_type = "journal"

    tags = _extract_tags(lower)
    action_items = _extract_action_items(text)
    summary = _summarize(text)

    return _normalize_classification(
        NoteClassification(
            title=derived_title,
            summary=summary,
            type=note_type,
            tags=tags,
            action_items=action_items,
        )
    )


def _derive_title(content: str) -> str:
    first_line = next((line.strip("# -\t ") for line in content.splitlines() if line.strip()), "")
    if not first_line:
        return "Untitled note"
    return first_line[:80]


def _summarize(content: str) -> str:
    collapsed = re.sub(r"\s+", " ", content).strip()
    return collapsed[:220] + ("..." if len(collapsed) > 220 else "")


def _extract_tags(lower: str) -> list[str]:
    candidates = [
        ("minddock", "MindDock"),
        ("notion", "Notion"),
        ("rag", "RAG"),
        ("ai", "AI"),
        ("embedding", "Embedding"),
        ("项目", "项目"),
        ("求职", "求职"),
        ("复盘", "复盘"),
        ("周报", "周报"),
        ("任务", "任务"),
    ]
    tags = [label for needle, label in candidates if needle in lower]
    return tags[:6] or ["Inbox"]


def _extract_action_items(content: str) -> list[str]:
    items: list[str] = []
    for line in content.splitlines():
        clean = line.strip(" -\t")
        lowered = clean.lower()
        if lowered.startswith(("todo", "next", "action")) or clean.startswith(("待办", "下一步", "任务")):
            items.append(clean[:160])
    return items[:8]


def _normalize_classification(classification: NoteClassification) -> NoteClassification:
    tags = []
    for tag in classification.tags:
        normalized = str(tag).strip()
        if normalized and normalized not in tags:
            tags.append(normalized[:32])

    return classification.model_copy(
        update={
            "title": classification.title.strip()[:120] or "Untitled note",
            "summary": classification.summary.strip()[:600],
            "tags": tags[:6],
            "action_items": [item.strip()[:200] for item in classification.action_items if item.strip()][:8],
        }
    )
