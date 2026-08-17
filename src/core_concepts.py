from __future__ import annotations

import logging

from openai import OpenAI

from src.config import Settings
from src.io_utils import write_json
from src.schemas import (
    CoreConceptDocument,
    CoreConceptResponse,
    LectureDocument,
)


LOGGER = logging.getLogger(__name__)

CORE_SYSTEM_PROMPT = """당신은 교육용 강의안의 복습 평가 기준을 구조화하는 AI이다.
반드시 제공된 강의안 내용만 사용하고 외부 지식을 추가하지 않는다.
지나치게 세부적인 용어는 핵심 개념으로 분류하지 않는다.
description은 강의안의 의미를 보존해야 한다.
텍스트뿐 아니라 각 Chunk의 시각 정보 설명도 평가 기준에 반영한다.
"""


def generate_core_concepts(
    *,
    client: OpenAI,
    settings: Settings,
    lecture: LectureDocument,
) -> CoreConceptDocument:
    source = "\n\n".join(
        (
            f"[p.{chunk.page}]\n"
            f"Topic: {chunk.topic}\n"
            f"Concepts: {', '.join(chunk.concepts)}\n"
            f"Visual: {chunk.visual_description}\n"
            f"Content: {chunk.content}"
        )
        for chunk in lecture.chunks
    )
    prompt = f"""다음은 '{lecture.lecture_name}' 강의 전체의 구조화 결과이다.
사용자가 복습 시 기억해야 할 핵심 개념을 중요도 high/medium/low로 구분하라.
각 개념이 실제로 등장하는 페이지와 강의안에 근거한 설명을 작성하라.

강의안 구조화 결과:
---
{source}
---
"""

    last_error: Exception | None = None
    for attempt in range(1, settings.max_retries + 1):
        try:
            response = client.responses.parse(
                model=settings.llm_model,
                input=[
                    {"role": "system", "content": CORE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                text_format=CoreConceptResponse,
            )
            if response.output_parsed is None:
                raise RuntimeError("핵심 개념 응답이 비어 있습니다.")
            valid_pages = {chunk.page for chunk in lecture.chunks}
            invalid = {
                page
                for concept in response.output_parsed.core_concepts
                for page in concept.pages
                if page not in valid_pages
            }
            if invalid:
                raise ValueError(f"강의안에 없는 페이지가 반환됐습니다: {sorted(invalid)}")
            document = CoreConceptDocument(
                lecture_id=lecture.lecture_id,
                lecture_name=lecture.lecture_name,
                core_concepts=response.output_parsed.core_concepts,
            )
            output_path = settings.core_concepts_dir / f"{lecture.lecture_id}.json"
            write_json(output_path, document.model_dump(mode="json"))
            return document
        except Exception as exc:
            last_error = exc
            LOGGER.warning(
                "핵심 개념 호출 실패 (%s, %s/%s): %s",
                lecture.lecture_id,
                attempt,
                settings.max_retries,
                exc,
            )
            if attempt < settings.max_retries:
                import time

                time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError(
        f"{lecture.lecture_id} 핵심 개념 생성에 실패했습니다."
    ) from last_error
