from __future__ import annotations

from collections.abc import Iterable, Sequence

from openai import OpenAI

from src.schemas import Chunk


def build_embedding_text(chunk: Chunk) -> str:
    concepts = ", ".join(chunk.concepts) if chunk.concepts else "(없음)"
    visual = chunk.visual_description or "(의미 있는 시각 정보 없음)"
    return (
        f"Topic: {chunk.topic}\n"
        f"Concepts: {concepts}\n"
        f"Visual: {visual}\n"
        f"Content: {chunk.content}"
    )


def create_embeddings(
    *,
    client: OpenAI,
    texts: Sequence[str],
    model: str,
    batch_size: int,
) -> list[list[float]]:
    if batch_size < 1:
        raise ValueError("batch_size는 1 이상이어야 합니다.")
    embeddings: list[list[float]] = []
    for batch in _batches(texts, batch_size):
        response = client.embeddings.create(model=model, input=batch)
        ordered = sorted(response.data, key=lambda item: item.index)
        if len(ordered) != len(batch):
            raise RuntimeError("Embedding 응답 개수가 요청 개수와 다릅니다.")
        embeddings.extend(item.embedding for item in ordered)
    return embeddings


def create_query_embedding(*, client: OpenAI, query: str, model: str) -> list[float]:
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("검색 문장은 비어 있을 수 없습니다.")
    response = client.embeddings.create(model=model, input=cleaned)
    return response.data[0].embedding


def _batches(values: Sequence[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield list(values[start : start + size])
