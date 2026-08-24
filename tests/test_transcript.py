from __future__ import annotations

import pytest

from src.transcript import segment_transcript


def test_segment_transcript_keeps_full_text_and_stable_ids() -> None:
    transcript = (
        "가설검정은 귀무가설과 대립가설을 세우는 것에서 시작합니다. "
        "유의수준을 정하고 검정통계량과 p-value를 계산합니다. "
        "다음으로 신뢰구간은 반복 표집 절차의 불확실성을 보여줍니다."
    )
    segments = segment_transcript(
        transcript,
        min_chars=20,
        target_chars=60,
        max_chars=100,
    )

    assert [item.segment_id for item in segments] == [
        f"seg_{index:02d}" for index in range(1, len(segments) + 1)
    ]
    assert " ".join(item.text for item in segments) == transcript


def test_segment_transcript_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="비어"):
        segment_transcript("  ")
