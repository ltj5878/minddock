import hashlib
import math
import re

from openai import AsyncOpenAI
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Embedding, Note

EMBEDDING_DIMENSIONS = 1536
EMBEDDING_MODEL = "text-embedding-3-small"


async def rebuild_note_embeddings(db: Session, note: Note) -> int:
    db.execute(delete(Embedding).where(Embedding.note_id == note.id))
    chunks = chunk_text(note.content)
    vectors = await embed_texts(chunks)
    for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        db.add(
            Embedding(
                note_id=note.id,
                project_id=note.project_id,
                chunk_index=index,
                chunk_text=chunk,
                embedding=vector,
            )
        )
    db.commit()
    return len(chunks)


async def ensure_embeddings(db: Session) -> int:
    notes = db.scalars(select(Note)).all()
    built = 0
    for note in notes:
        existing = db.scalar(select(Embedding).where(Embedding.note_id == note.id).limit(1))
        if not existing:
            built += await rebuild_note_embeddings(db, note)
    return built


async def search_similar_chunks(
    db: Session,
    query: str,
    project_id: str | None = None,
    limit: int = 6,
) -> list[tuple[Embedding, Note, float]]:
    await ensure_embeddings(db)
    query_vector = (await embed_texts([query]))[0]
    statement = select(Embedding, Note).join(Note, Note.id == Embedding.note_id)
    if project_id:
        statement = statement.where(Embedding.project_id == project_id)

    results: list[tuple[Embedding, Note, float]] = []
    for embedding, note in db.execute(statement).all():
        score = cosine_similarity(query_vector, embedding.embedding)
        results.append((embedding, note, score))

    return sorted(results, key=lambda item: item[2], reverse=True)[:limit]


def chunk_text(text: str, chunk_size: int = 1800, overlap: int = 250) -> list[str]:
    clean = re.sub(r"\n{3,}", "\n\n", text.strip())
    if not clean:
        return [""]
    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + chunk_size)
        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(clean):
            break
        start = max(0, end - overlap)
    return chunks


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if settings.openai_api_key:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        return [item.embedding for item in response.data]
    return [_local_embedding(text) for text in texts]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def _local_embedding(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSIONS
    tokens = re.findall(r"[a-zA-Z0-9_\-]+|[\u4e00-\u9fff]{2,}", text.lower())
    for token in tokens or [text[:32]]:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for offset in range(0, 12, 4):
            index = int.from_bytes(digest[offset : offset + 2], "big") % EMBEDDING_DIMENSIONS
            sign = 1.0 if digest[offset + 2] % 2 == 0 else -1.0
            vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]
