from __future__ import annotations

from pathlib import Path
from typing import Any

from src.embedding import build_embedding_text
from src.schemas import LectureDocument, SearchHit


class LectureVectorStore:
    def __init__(self, *, path: Path, collection_name: str) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "ChromaDB가 설치되지 않았습니다. requirements.txt를 설치하세요."
            ) from exc
        client = chromadb.PersistentClient(path=str(path))
        self.collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_lecture(
        self, lecture: LectureDocument, embeddings: list[list[float]]
    ) -> int:
        if len(lecture.chunks) != len(embeddings):
            raise ValueError("Chunk 수와 Embedding 수가 다릅니다.")
        if not lecture.chunks:
            return 0

        ids = [chunk.chunk_id for chunk in lecture.chunks]
        documents = [build_embedding_text(chunk) for chunk in lecture.chunks]
        metadatas = [
            {
                "lecture_id": chunk.lecture_id,
                "lecture_name": chunk.lecture_name,
                "page": chunk.page,
                "topic": chunk.topic,
                "concepts": ", ".join(chunk.concepts),
                "has_visual": bool(chunk.visual_description),
            }
            for chunk in lecture.chunks
        ]
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        existing = self.collection.get(
            where={"lecture_id": lecture.lecture_id}, include=[]
        )
        stale_ids = sorted(set(existing.get("ids", [])) - set(ids))
        if stale_ids:
            self.collection.delete(ids=stale_ids)
        return len(ids)

    def query(
        self,
        *,
        query_embedding: list[float],
        top_k: int,
        lecture_id: str | None = None,
    ) -> list[SearchHit]:
        if top_k < 1:
            raise ValueError("top_k는 1 이상이어야 합니다.")
        collection_size = self.collection.count()
        if collection_size == 0:
            return []
        kwargs: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, collection_size),
            "include": ["documents", "metadatas", "distances"],
        }
        if lecture_id:
            kwargs["where"] = {"lecture_id": lecture_id}
        result = self.collection.query(**kwargs)

        ids = _first(result.get("ids"))
        documents = _first(result.get("documents"))
        metadatas = _first(result.get("metadatas"))
        distances = _first(result.get("distances"))
        hits: list[SearchHit] = []
        for index, chunk_id in enumerate(ids):
            metadata = metadatas[index]
            hits.append(
                SearchHit(
                    rank=index + 1,
                    chunk_id=chunk_id,
                    lecture_id=str(metadata["lecture_id"]),
                    lecture_name=str(metadata["lecture_name"]),
                    page=int(metadata["page"]),
                    topic=str(metadata["topic"]),
                    content=str(documents[index]),
                    distance=float(distances[index]),
                )
            )
        return hits


def _first(value: Any) -> list[Any]:
    if not value:
        return []
    return value[0]
