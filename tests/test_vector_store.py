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

