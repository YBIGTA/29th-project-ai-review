from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.evaluation_api import (
    AssessmentValidationError,
    request_evaluation_assessment,
    request_validated_evaluation_assessment,
)
from src.evaluation_schemas import TopicAssessment


class FakeResponses:
    def __init__(
        self,
        assessment: TopicAssessment | None | list[TopicAssessment | None],
    ) -> None:
        self.assessments = assessment if isinstance(assessment, list) else [assessment]
        self.calls: list[dict[str, object]] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        index = min(len(self.calls) - 1, len(self.assessments) - 1)
        return SimpleNamespace(output_parsed=self.assessments[index])


class FakeClient:
    def __init__(
        self,
        assessment: TopicAssessment | None | list[TopicAssessment | None],
    ) -> None:
        self.responses = FakeResponses(assessment)


def sample_assessment() -> TopicAssessment:
    return TopicAssessment(
        lecture_id="basic_statistics",
        objective_id="stats.hypothesis_uncertainty",
        claim_assessments=[
            {
                "claim_id": "stats.test_steps",
                "judgment": "correct",
                "source_chunk_ids_used": ["basic_statistics_p9_01"],
                "conflict_status": "none",
                "evidence_spans": [
                    {
                        "segment_id": "seg_01",
                        "quote": "가설을 세운다",
                        "relation": "supports",
                    }
                ],
                "rationale": "절차를 설명했다.",
            }
        ],
    )


def test_api_uses_topic_assessment_schema() -> None:
    assessment = sample_assessment()
    client = FakeClient(assessment)
    messages = [{"role": "user", "content": "평가 입력"}]

    result = request_evaluation_assessment(
        client=client,
        model="gpt-5.6-luna",
        input_messages=messages,
        max_retries=1,
    )

    assert result is assessment
    assert client.responses.calls[0]["text_format"] is TopicAssessment


def test_api_rejects_empty_structured_response() -> None:
    with pytest.raises(RuntimeError, match="모두 실패"):
        request_evaluation_assessment(
            client=FakeClient(None),
            model="gpt-5.6-luna",
            input_messages=[{"role": "user", "content": "평가 입력"}],
            max_retries=1,
        )


def test_validated_api_retries_with_validation_feedback(monkeypatch) -> None:
    first = sample_assessment()
    corrected = sample_assessment().model_copy(deep=True)
    corrected.claim_assessments[0].evidence_spans[0].quote = "가설을 세운다"
    client = FakeClient([first, corrected])
    attempts = 0

    def fake_validate(*args, **kwargs) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise ValueError("quote가 지정된 seg_01에 없습니다.")

    monkeypatch.setattr("src.evaluation_api.validate_assessment", fake_validate)

    result = request_validated_evaluation_assessment(
        client=client,
        model="gpt-5.6-luna",
        input_messages=[{"role": "user", "content": "평가 입력"}],
        max_retries=1,
        rubric=object(),  # type: ignore[arg-type]
        valid_segments={"seg_01": "가설을 세운다"},
        transcript="가설을 세운다",
    )

    assert result is corrected
    assert len(client.responses.calls) == 2
    repair_messages = client.responses.calls[1]["input"]
    assert isinstance(repair_messages, list)
    assert "quote가 지정된 seg_01에 없습니다" in repair_messages[-1]["content"]


def test_validated_api_preserves_last_invalid_assessment(monkeypatch) -> None:
    assessment = sample_assessment()
    client = FakeClient(assessment)

    def always_invalid(*args, **kwargs) -> None:
        raise ValueError("계속 잘못된 quote")

    monkeypatch.setattr("src.evaluation_api.validate_assessment", always_invalid)

    with pytest.raises(AssessmentValidationError, match="계속 잘못된 quote") as exc_info:
        request_validated_evaluation_assessment(
            client=client,
            model="gpt-5.6-luna",
            input_messages=[{"role": "user", "content": "평가 입력"}],
            max_retries=1,
            rubric=object(),  # type: ignore[arg-type]
            valid_segments={"seg_01": "가설을 세운다"},
            transcript="가설을 세운다",
            max_validation_retries=1,
        )

    assert exc_info.value.assessment is assessment
    assert len(client.responses.calls) == 2
