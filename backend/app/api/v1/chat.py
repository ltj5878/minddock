import re

from openai import AsyncOpenAI
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Note
from app.services.embeddings import search_similar_chunks

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    project_id: str | None = None
    model: str = "openai"


class CitationResponse(BaseModel):
    note_id: str
    note_title: str
    chunk_text: str
    similarity: float


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    model_used: str


@router.post("/ask", response_model=AskResponse)
async def ask_knowledge(req: AskRequest, db: Session = Depends(get_db)):
    vector_hits = await search_similar_chunks(db, req.question, req.project_id, limit=6)
    strong_hits = [hit for hit in vector_hits if hit[2] > 0.05]
    if strong_hits:
        citations = [
            CitationResponse(
                note_id=note.id,
                note_title=note.title,
                chunk_text=embedding.chunk_text,
                similarity=max(0.0, min(0.99, score)),
            )
            for embedding, note, score in strong_hits[:4]
        ]
        return AskResponse(
            answer=await _answer_with_context(req.question, strong_hits[:5]),
            citations=citations,
            model_used="openai-rag" if settings.openai_api_key else "local-rag",
        )

    notes = db.scalars(select(Note)).all()
    ranked = _rank_notes(req.question, notes, req.project_id)
    if ranked:
        citations = [
            CitationResponse(
                note_id=note.id,
                note_title=note.title,
                chunk_text=_best_chunk(note.content, req.question),
                similarity=score,
            )
            for note, score in ranked[:4]
        ]
        themes = "、".join(c.note_title for c in citations[:3])
        return AskResponse(
            answer=(
                f"我在本地笔记库里找到了 {len(ranked)} 条相关笔记。最相关的是：{themes}。\n\n"
                f"初步结论：{_compose_local_answer(req.question, [note for note, _ in ranked[:3]])}\n\n"
                "当前是本地关键词检索版本，还没有进入 Phase 3 的 embedding/RAG。"
            ),
            citations=citations,
            model_used="local-keyword",
        )

    return AskResponse(
        answer=(
            "我在本地笔记库里还没有找到足够相关的内容。你可以先在 Inbox 新建一条笔记，"
            "系统会保存到本地数据库并尝试同步到 Notion。"
        ),
        citations=[],
        model_used="local-keyword",
    )


def _rank_notes(question: str, notes: list[Note], project_id: str | None) -> list[tuple[Note, float]]:
    terms = _tokenize(question)
    if not terms:
        return []

    ranked: list[tuple[Note, float]] = []
    for note in notes:
        if project_id and note.project_id != project_id:
            continue
        haystack = " ".join(
            [note.title, note.summary or "", note.content, " ".join(note.tags or [])]
        ).lower()
        hits = sum(1 for term in terms if term in haystack)
        if hits:
            ranked.append((note, min(0.98, 0.55 + hits / max(len(terms), 1) * 0.4)))

    return sorted(ranked, key=lambda item: item[1], reverse=True)


def _tokenize(question: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_\-]+|[\u4e00-\u9fff]{2,}", question.lower())
    stop = {"the", "and", "for", "with", "什么", "如何", "一个", "这个", "你的"}
    return [word for word in words if word not in stop]


def _best_chunk(content: str, question: str) -> str:
    terms = _tokenize(question)
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", content) if p.strip()]
    if not paragraphs:
        return content[:220]
    return max(paragraphs, key=lambda p: sum(1 for term in terms if term in p.lower()))[:260]


def _compose_local_answer(question: str, notes: list[Note]) -> str:
    summaries = [note.summary or note.content[:120] for note in notes]
    return " ".join(summaries)[:520]


async def _answer_with_context(question: str, hits: list[tuple]) -> str:
    context = "\n\n".join(
        f"[{index + 1}] {note.title}\n{embedding.chunk_text}"
        for index, (embedding, note, score) in enumerate(hits)
    )
    if settings.openai_api_key:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You answer questions over the user's personal notes. "
                        "Use only the supplied context, cite sources like [1], and answer in Chinese."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    top_titles = "、".join(note.title for _, note, _ in hits[:3])
    top_summary = " ".join(embedding.chunk_text[:180] for embedding, _, _ in hits[:3])
    return (
        f"根据本地向量检索，最相关的来源是：{top_titles}。\n\n"
        f"{top_summary}\n\n"
        "当前未配置 OPENAI_API_KEY，因此这里使用本地检索摘要；配置后会生成完整 RAG 回答并保留引用。"
    )
