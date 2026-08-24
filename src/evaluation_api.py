from __future__ import annotations

import logging
import time
from typing import Any

from openai import OpenAI

from src.evaluation import validate_assessment
from src.evaluation_schemas import LectureRubric, TopicAssessment


LOGGER = logging.getLogger(__name__)


class AssessmentValidationError(ValueError):
    """Raised after an LLM assessment still fails deterministic validation."""

    def __init__(self, message: str, assessment: TopicAssessment) -> None:
        super().__init__(message)
        self.assessment = assessment


def request_evaluation_assessment(
    *,
    client: OpenAI,
    model: str,
    input_messages: list[dict[str, Any]],
    max_retries: int,
) -> TopicAssessment:
    if not model.strip():
        raise ValueError("평가 모델 이름이 비어 있습니다.")
    if not input_messages:
        raise ValueError("평가 LLM 입력 메시지가 비어 있습니다.")
    if max_retries < 1:
        raise ValueError("max_retries는 1 이상이어야 합니다.")

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.responses.parse(
                model=model,
                input=input_messages,
                text_format=TopicAssessment,
            )
            if response.output_parsed is None:
                raise RuntimeError("평가 LLM의 구조화 응답이 비어 있습니다.")
            return response.output_parsed
        except Exception as exc:
            last_error = exc
            LOGGER.warning("평가 LLM 호출 실패 (%s/%s): %s", attempt, max_retries, exc)
            if attempt < max_retries:
                time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError(f"평가 LLM 호출이 {max_retries}회 모두 실패했습니다.") from last_error


def request_validated_evaluation_assessment(
    *,
    client: OpenAI,
    model: str,
    input_messages: list[dict[str, Any]],
    max_retries: int,
    rubric: LectureRubric,
    valid_segments: dict[str, str],
    transcript: str,
    max_validation_retries: int = 1,
) -> TopicAssessment:
    """Request an assessment and retry once when its evidence fails validation.

    API/parse retries and domain-validation retries are kept separate. A validation
    retry receives the invalid full response and the exact validation error so it can
    correct the structured result without weakening exact-quote validation.
    """
    if max_validation_retries < 0:
        raise ValueError("max_validation_retries는 0 이상이어야 합니다.")

    messages = list(input_messages)
    last_assessment: TopicAssessment | None = None
    for validation_attempt in range(max_validation_retries + 1):
        assessment = request_evaluation_assessment(
            client=client,
            model=model,
            input_messages=messages,
            max_retries=max_retries,
        )
        last_assessment = assessment
        try:
            validate_assessment(
                rubric,
                assessment,
                valid_segments=valid_segments,
                transcript=transcript,
            )
            return assessment
        except ValueError as exc:
            if validation_attempt >= max_validation_retries:
                raise AssessmentValidationError(str(exc), assessment) from exc
            LOGGER.warning(
                "평가 결과 검증 실패, 교정 재요청 (%s/%s): %s",
                validation_attempt + 1,
                max_validation_retries,
                exc,
            )
            messages = [
                *input_messages,
                {
                    "role": "assistant",
                    "content": assessment.model_dump_json(),
                },
                {
                    "role": "user",
                    "content": (
                        "위 JSON은 다음 결정적 검증을 통과하지 못했습니다: "
                        f"{exc}\n"
                        "원래 평가 입력을 다시 확인하고 전체 JSON을 수정해 반환하세요. "
                        "특히 evidence_spans의 quote는 지정한 segment에서 글자 그대로 "
                        "복사해야 하며, 판정·충돌 근거를 누락해서는 안 됩니다."
                    ),
                },
            ]

    # The loop always returns or raises, but this keeps type checkers honest.
    assert last_assessment is not None
    raise AssessmentValidationError("평가 결과 검증에 실패했습니다.", last_assessment)
