from src.embedding import build_embedding_text
from src.schemas import Chunk


def test_build_embedding_text_contains_search_fields():
    chunk = Chunk(
        chunk_id="basic_statistics_p1_01",
        lecture_id="basic_statistics",
        lecture_name="기초통계",
        page=1,
        topic="평균",
        concepts=["평균", "이상치"],
        raw_text="원문",
        visual_description="평균과 이상치의 관계를 나타낸 그래프",
        content="평균은 이상치의 영향을 받을 수 있다.",
    )

    text = build_embedding_text(chunk)

    assert "Topic: 평균" in text
    assert "Concepts: 평균, 이상치" in text
    assert "Visual: 평균과 이상치의 관계를 나타낸 그래프" in text
    assert "Content: 평균은 이상치의 영향을 받을 수 있다." in text
