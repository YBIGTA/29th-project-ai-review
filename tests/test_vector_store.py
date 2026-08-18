import pytest

from src.schemas import Chunk, LectureDocument
from src.vector_store import LectureVectorStore


def _chunk(chunk_id: str, page: int, topic: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        lecture_id="basic_statistics",
        lecture_name="기초통계",
        page=page,
        topic=topic,
        concepts=[topic],
        raw_text=f"{topic} 원문",
        content=f"{topic} 설명",
    )


def test_upsert_query_and_remove_stale_chunks(tmp_path):
    store = LectureVectorStore(path=tmp_path, collection_name="test_chunks")
    first = _chunk("basic_statistics_p1_01", 1, "평균")
    second = _chunk("basic_statistics_p2_01", 2, "분산")
    document = LectureDocument(
        lecture_id="basic_statistics",
        lecture_name="기초통계",
        source_file="기초통계.pdf",
        chunks=[first, second],
    )

    assert store.upsert_lecture(document, [[1.0, 0.0], [0.0, 1.0]]) == 2
    hits = store.query(query_embedding=[1.0, 0.0], top_k=5)
    assert hits[0].chunk_id == first.chunk_id
    assert hits[0].lecture_id == "basic_statistics"

    updated = document.model_copy(update={"chunks": [first]})
    store.upsert_lecture(updated, [[1.0, 0.0]])
    stored = store.collection.get(where={"lecture_id": "basic_statistics"})
    assert stored["ids"] == [first.chunk_id]


def test_query_many_returns_one_ranked_list_per_embedding(tmp_path):
    store = LectureVectorStore(path=tmp_path, collection_name="many_queries")
    first = _chunk("basic_statistics_p1_01", 1, "평균")
    second = _chunk("basic_statistics_p2_01", 2, "분산")
    document = LectureDocument(
        lecture_id="basic_statistics",
        lecture_name="기초통계",
        source_file="기초통계.pdf",
        chunks=[first, second],
    )
    store.upsert_lecture(document, [[1.0, 0.0], [0.0, 1.0]])

    results = store.query_many(
        query_embeddings=[[1.0, 0.0], [0.0, 1.0]],
        top_k=2,
        lecture_id="basic_statistics",
    )

    assert len(results) == 2
    assert results[0][0].chunk_id == first.chunk_id
    assert results[1][0].chunk_id == second.chunk_id


def test_embedding_model_and_review_metadata_are_recorded(tmp_path):
    store = LectureVectorStore(
        path=tmp_path,
        collection_name="model_aware_chunks",
        embedding_model="text-embedding-3-small",
    )
    chunk = _chunk("basic_statistics_p6_01", 6, "공분산")
    document = LectureDocument(
        lecture_id="basic_statistics",
        lecture_name="기초통계",
        source_file="기초통계.pdf",
        chunks=[chunk],
    )

    store.upsert_lecture(
        document,
        [[1.0, 0.0]],
        metadata_overrides={
            chunk.chunk_id: {
                "review_status": "source_claim_needs_review",
                "review_note": "평가 rubric 우선",
            }
        },
    )
    stored = store.collection.get(ids=[chunk.chunk_id], include=["metadatas"])

    assert store.collection.metadata["embedding_model"] == "text-embedding-3-small"
    assert stored["metadatas"][0]["review_status"] == "source_claim_needs_review"
    assert stored["metadatas"][0]["review_note"] == "평가 rubric 우선"


def test_existing_collection_rejects_a_different_embedding_model(tmp_path):
    LectureVectorStore(
        path=tmp_path,
        collection_name="model_mismatch_chunks",
        embedding_model="text-embedding-3-small",
    )

    with pytest.raises(RuntimeError, match="Embedding 모델"):
        LectureVectorStore(
            path=tmp_path,
            collection_name="model_mismatch_chunks",
            embedding_model="text-embedding-3-large",
        )
