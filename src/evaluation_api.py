from __future__ import annotations

import logging
import time
from typing import Any

from openai import OpenAI

from src.evaluation_schemas import EvaluationAssessment


LOGGER = logging.getLogger(__name__)


def request_evaluation_assessment(
    *,
    client: OpenAI,
    model: str,
    input_messages: list[dict[str, Any]],
    max_retries: int,
) -> EvaluationAssessment:
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
                text_format=EvaluationAssessment,
            )
            if response.output_parsed is None:
                raise RuntimeError("평가 LLM의 구조화 응답이 비어 있습니다.")
            return response.output_parsed
        except Exception as exc:
            last_error = exc
            LOGGER.warning(
                "평가 LLM 호출 실패 (%s/%s): %s",
                attempt,
                max_retries,
                exc,
            )
            if attempt < max_retries:
                time.sleep(min(2 ** (attempt - 1), 8))

    raise RuntimeError(
        f"평가 LLM 호출이 {max_retries}회 모두 실패했습니다."
    ) from last_error
