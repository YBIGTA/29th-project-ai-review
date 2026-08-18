from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.evaluation_api import request_evaluation_assessment
from src.evaluation_schemas import EvaluationAssessment


class FakeResponses:
    def __init__(self, assessment: EvaluationAssessment | None) -> None:
        self.assessment = assessment
        self.calls: list[dict[str, object]] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.assessment)


class FakeClient:
    def __init__(self, assessment: EvaluationAssessment | None) -> None:
        self.responses = FakeResponses(assessment)


def _empty_assessment() -> EvaluationAssessment:
    return EvaluationAssessment(
        lecture_id="basic_statistics",
        claim_assessments=[],
        objective_assessments=[],
        relation_assessments=[],
        chain_assessments=[],
    )


def test_request_evaluation_uses_responses_parse_and_pydantic_schema() -> None:
    assessment = _empty_assessment()
    client = FakeClient(assessment)
    messages = [
        {"role": "system", "content": "평가 지침"},
        {"role": "user", "content": "평가 입력"},
    ]

    result = request_evaluation_assessment(
        client=client,
        model="gpt-5.6-luna",
        input_messages=messages,
        max_retries=1,
    )

    assert result is assessment
    assert client.responses.calls == [
        {
            "model": "gpt-5.6-luna",
            "input": messages,
            "text_format": EvaluationAssessment,
        }
    ]


def test_request_evaluation_rejects_empty_structured_response() -> None:
    with pytest.raises(RuntimeError, match="모두 실패"):
        request_evaluation_assessment(
            client=FakeClient(None),
            model="gpt-5.6-luna",
            input_messages=[{"role": "user", "content": "평가 입력"}],
            max_retries=1,
        )
