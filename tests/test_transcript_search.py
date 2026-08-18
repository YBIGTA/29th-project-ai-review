"""긴 STT 답변 분할 및 검색 테스트."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.config import Settings
from src.schemas import SearchHit
from src.search import search_transcript, segment_transcript


def _hit(chunk_id: str, page: int, distance: float) -> SearchHit:
    return SearchHit(
        rank=1,
        chunk_id=chunk_id,
        lecture_id="basic_statistics",
        lecture_name="기초통계",
        page=page,
        topic=f"주제 {page}",
        content=f"근거 {page}",
        distance=distance,
    )


class FakeEmbeddings:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[str]]] = []

    def create(self, *, model: str, input: list[str]):
        self.calls.append((model, input))
        return SimpleNamespace(
            data=[
                SimpleNamespace(index=index, embedding=[float(index + 1), 0.0])
                for index in range(len(input))
            ]
        )


class FakeClient:
    def __init__(self) -> None:
        self.embeddings = FakeEmbeddings()


class FakeStore:
    def __init__(self, hit_groups: list[list[SearchHit]]) -> None:
        self.hit_groups = hit_groups
        self.query_embeddings: list[list[float]] | None = None
        self.lecture_id: str | None = None

    def query_many(
        self,
        *,
        query_embeddings: list[list[float]],
        top_k: int,
        lecture_id: str | None = None,
    ) -> list[list[SearchHit]]:
        self.query_embeddings = query_embeddings
        self.lecture_id = lecture_id
        return self.hit_groups


def test_segment_transcript_uses_topic_shifts_without_punctuation() -> None:
    transcript = (
        "먼저 평균은 자료의 중심을 나타냅니다 "
        "다음으로 분산은 평균 주변의 퍼짐을 나타냅니다 "
        "마지막으로 표준편차는 분산의 제곱근입니다"
    )

    segments = segment_transcript(
        transcript,
        min_chars=1,
        target_chars=200,
        max_chars=240,
        max_segments=8,
    )

    assert [segment.text.split()[0] for segment in segments] == [
        "먼저",
        "다음으로",
        "마지막으로",
    ]


def test_segment_transcript_preserves_all_text_when_limited() -> None:
    transcript = "첫 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다. 네 번째입니다."

    segments = segment_transcript(
        transcript,
        min_chars=1,
        target_chars=5,
        max_chars=20,
        max_segments=2,
    )

    assert len(segments) == 2
    assert " ".join(segment.text for segment in segments) == transcript


def test_segment_transcript_rejects_empty_text() -> None:
    with pytest.raises(ValueError, match="비어"):
        segment_transcript("  \n ")


def test_search_transcript_batches_segments_and_keeps_diverse_evidence() -> None:
    transcript = (
        "먼저 평균을 설명합니다. "
        "다음으로 분산을 설명합니다. "
        "마지막으로 표준편차를 설명합니다."
    )
    duplicate = _hit("chunk_a", 1, 0.20)
    better_duplicate = _hit("chunk_a", 1, 0.10)
    hit_b = _hit("chunk_b", 2, 0.40)
    hit_c = _hit("chunk_c", 3, 0.30)
    hit_d = _hit("chunk_d", 4, 0.25)
    fake_store = FakeStore(
        [
            [duplicate, hit_b],
            [better_duplicate, hit_c],
            [hit_d],
        ]
    )
    fake_client = FakeClient()

    result = search_transcript(
        client=fake_client,
        settings=Settings.from_env(),
        transcript=transcript,
        lecture_id="basic_statistics",
        top_k_per_segment=2,
        max_evidence=4,
        min_chars=1,
        target_chars=200,
        max_chars=240,
        max_segments=8,
        store=fake_store,
    )

    assert len(result.segment_results) == 3
    assert len(fake_client.embeddings.calls) == 1
    assert len(fake_client.embeddings.calls[0][1]) == 3
    assert fake_store.lecture_id == "basic_statistics"
    assert [hit.chunk_id for hit in result.evidence] == [
        "chunk_a",
        "chunk_d",
        "chunk_c",
        "chunk_b",
    ]
    assert result.evidence[0].best_distance == 0.10
    assert result.evidence[0].matched_segment_ids == ["seg_01", "seg_02"]


def test_search_transcript_fills_remaining_evidence_by_global_distance() -> None:
    fake_store = FakeStore(
        [
            [_hit("anchor_a", 1, 0.20), _hit("weak_early", 2, 0.61)],
            [_hit("anchor_b", 3, 0.25), _hit("strong_late", 4, 0.32)],
        ]
    )

    result = search_transcript(
        client=FakeClient(),
        settings=Settings.from_env(),
        transcript="먼저 평균을 설명합니다. 다음으로 분산을 설명합니다.",
        lecture_id="basic_statistics",
        top_k_per_segment=2,
        max_evidence=3,
        min_chars=1,
        target_chars=200,
        max_chars=240,
        store=fake_store,
    )

    assert [hit.chunk_id for hit in result.evidence] == [
        "anchor_a",
        "anchor_b",
        "strong_late",
    ]


def test_search_transcript_can_filter_weak_evidence() -> None:
    fake_store = FakeStore(
        [[_hit("strong", 1, 0.25), _hit("weak", 2, 0.75)]]
    )

    result = search_transcript(
        client=FakeClient(),
        settings=Settings.from_env(),
        transcript="평균을 설명합니다.",
        lecture_id="basic_statistics",
        max_distance=0.5,
        store=fake_store,
    )

    assert [hit.chunk_id for hit in result.evidence] == ["strong"]
