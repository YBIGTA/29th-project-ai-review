from __future__ import annotations

from openai import OpenAI

from src.config import Settings
from src.embedding import create_query_embedding
from src.schemas import SearchHit
from src.vector_store import LectureVectorStore


def search(
    *,
    client: OpenAI,
    settings: Settings,
    query: str,
    top_k: int | None = None,
    lecture_id: str | None = None,
) -> list[SearchHit]:
    embedding = create_query_embedding(
        client=client, query=query, model=settings.embedding_model
    )
    store = LectureVectorStore(
        path=settings.vector_db_path,
        collection_name=settings.collection_name,
    )
    return store.query(
        query_embedding=embedding,
        top_k=top_k or settings.top_k,
        lecture_id=lecture_id,
    )

