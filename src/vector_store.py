from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.embedding import build_embedding_text
from src.schemas import LectureDocument, SearchHit


class LectureVectorStore:
    def __init__(
        self,
        *,
        path: Path,
        collection_name: str,
        embedding_model: str | None = None,
    ) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "ChromaDB가 설치되지 않았습니다. requirements.txt를 설치하세요."
            ) from exc
        client = chromadb.PersistentClient(path=str(path))
        metadata = {"hnsw:space": "cosine"}
        if embedding_model:
            metadata["embedding_model"] = embedding_model
        existing_names = {collection.name for collection in client.list_collections()}
        if collection_name in existing_names:
            self.collection = client.get_collection(name=collection_name)
        else:
            self.collection = client.create_collection(
                name=collection_name,
                metadata=metadata,
            )
        stored_model = (self.collection.metadata or {}).get("embedding_model")
        if embedding_model and stored_model and stored_model != embedding_model:
            raise RuntimeError(
                "ChromaDB collection의 Embedding 모델이 현재 설정과 다릅니다: "
                f"stored={stored_model}, configured={embedding_model}"
            )
        if embedding_model and not stored_model:
            if self.collection.count() > 0:
                raise RuntimeError(
                    "기존 ChromaDB collection에 Embedding 모델 정보가 없습니다. "
                    "새 collection 이름으로 전체를 다시 인덱싱하세요."
                )
            current_metadata = dict(self.collection.metadata or {})
            current_metadata["embedding_model"] = embedding_model
            current_metadata.setdefault("hnsw:space", "cosine")
            self.collection.modify(metadata=current_metadata)

    def upsert_lecture(
        self,
        lecture: LectureDocument,
        embeddings: list[list[float]],
        metadata_overrides: Mapping[str, Mapping[str, str | int | float | bool]]
        | None = None,
    ) -> int:
        if len(lecture.chunks) != len(embeddings):
            raise ValueError("Chunk 수와 Embedding 수가 다릅니다.")
        if not lecture.chunks:
            return 0

        ids = [chunk.chunk_id for chunk in lecture.chunks]
        documents = [build_embedding_text(chunk) for chunk in lecture.chunks]
        metadata_overrides = metadata_overrides or {}
        unknown_override_ids = sorted(set(metadata_overrides) - set(ids))
        if unknown_override_ids:
            raise ValueError(
                "metadata override의 chunk_id가 LectureDocument에 없습니다: "
                f"{unknown_override_ids}"
            )
        metadatas = []
        for chunk in lecture.chunks:
            metadata: dict[str, str | int | float | bool] = {
                "lecture_id": chunk.lecture_id,
                "lecture_name": chunk.lecture_name,
                "page": chunk.page,
                "topic": chunk.topic,
                "concepts": ", ".join(chunk.concepts),
                "has_visual": bool(chunk.visual_description),
            }
            metadata.update(metadata_overrides.get(chunk.chunk_id, {}))
            metadatas.append(metadata)
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
        results = self.query_many(
            query_embeddings=[query_embedding],
            top_k=top_k,
            lecture_id=lecture_id,
        )
        return results[0] if results else []

    def query_many(
        self,
        *,
        query_embeddings: list[list[float]],
        top_k: int,
        lecture_id: str | None = None,
    ) -> list[list[SearchHit]]:
        if top_k < 1:
            raise ValueError("top_k는 1 이상이어야 합니다.")
        if not query_embeddings:
            return []
        if any(not embedding for embedding in query_embeddings):
            raise ValueError("검색 Embedding은 비어 있을 수 없습니다.")
        collection_size = self.collection.count()
        if collection_size == 0:
            return [[] for _ in query_embeddings]
        kwargs: dict[str, Any] = {
            "query_embeddings": query_embeddings,
            "n_results": min(top_k, collection_size),
            "include": ["documents", "metadatas", "distances"],
        }
        if lecture_id:
            kwargs["where"] = {"lecture_id": lecture_id}
        result = self.collection.query(**kwargs)

        id_rows = result.get("ids") or []
        document_rows = result.get("documents") or []
        metadata_rows = result.get("metadatas") or []
        distance_rows = result.get("distances") or []
        all_hits: list[list[SearchHit]] = []
        for query_index in range(len(query_embeddings)):
            ids = _row(id_rows, query_index)
            documents = _row(document_rows, query_index)
            metadatas = _row(metadata_rows, query_index)
            distances = _row(distance_rows, query_index)
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
            all_hits.append(hits)
        return all_hits


def _row(value: Any, index: int) -> list[Any]:
    if not value or index >= len(value):
        return []
    return value[index]
