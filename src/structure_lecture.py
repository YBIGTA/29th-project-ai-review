from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path

from openai import OpenAI
from pydantic import ValidationError

from src.config import LectureConfig, Settings
from src.io_utils import read_json, write_json
from src.pdf_loader import PdfLoadResult, PageText, page_image_data_url, split_long_text
from src.schemas import (
    Chunk,
    LectureDocument,
    StructuredChunk,
    StructuredPageResponse,
)


LOGGER = logging.getLogger(__name__)
STRUCTURE_CACHE_VERSION = 2

SYSTEM_PROMPT = """당신은 교육용 강의안을 RAG 지식베이스용 데이터로 구조화하는 AI이다.

주어진 강의안 내용만을 근거로 작업해야 한다.

반드시 지켜야 할 규칙:
1. 강의안에 존재하지 않는 외부 지식을 추가하지 않는다.
2. 강의안의 주장과 의미를 변경하지 않는다.
3. 불명확한 내용은 임의로 보완하지 않는다.
4. 전문용어는 가능하면 강의안 표기를 유지한다.
5. 한 Chunk는 하나의 핵심 주제를 중심으로 구성한다.
6. 서로 강하게 연결된 내용은 불필요하게 분리하지 않는다.
7. 페이지 이미지를 반드시 직접 확인하고 텍스트 추출에서 빠진 표, 그래프, 수식,
   다이어그램, 화살표 관계, 범례, 축, 스크린샷, 코드와 예시를 놓치지 않는다.
8. raw_text는 제공된 '추출 텍스트'에서 그대로 복사한 연속된 구간만 사용한다.
   이미지에만 있는 글자는 raw_text가 아니라 visual_description에 기록한다.
9. visual_description은 학습에 필요한 시각 정보만 객관적으로 설명한다.
10. content는 raw_text와 시각 정보를 함께 반영한 검색용 설명으로 작성한다.
11. 이미지에서 확인할 수 없는 의미를 외부 지식으로 추측하지 않는다.
12. 너무 짧고 의미 없는 Chunk는 만들지 않는다.
"""


def structure_lecture(
    *,
    client: OpenAI,
    settings: Settings,
    lecture: LectureConfig,
    pdf: PdfLoadResult,
    force: bool = False,
) -> LectureDocument:
    chunks: list[Chunk] = []
    for page_index, page in enumerate(pdf.pages):
        previous_text = pdf.pages[page_index - 1].text if page_index > 0 else ""
        next_text = (
            pdf.pages[page_index + 1].text
            if page_index + 1 < len(pdf.pages)
            else ""
        )
        structured = _structure_page(
            client=client,
            settings=settings,
            lecture=lecture,
            page=page,
            previous_text=previous_text,
            next_text=next_text,
            force=force,
        )
        for chunk_number, candidate in enumerate(structured.chunks, start=1):
            chunks.append(
                Chunk(
                    chunk_id=make_chunk_id(
                        lecture.lecture_id, page.page, chunk_number
                    ),
                    lecture_id=lecture.lecture_id,
                    lecture_name=lecture.lecture_name,
                    page=page.page,
                    topic=candidate.topic,
                    concepts=candidate.concepts,
                    raw_text=candidate.raw_text,
                    visual_description=candidate.visual_description,
                    content=candidate.content,
                )
            )

    return LectureDocument(
        lecture_id=lecture.lecture_id,
        lecture_name=lecture.lecture_name,
        source_file=pdf.source_file,
        chunks=chunks,
    )


def make_chunk_id(lecture_id: str, page: int, chunk_number: int) -> str:
    if page < 1 or chunk_number < 1:
        raise ValueError("page와 chunk_number는 1 이상이어야 합니다.")
    return f"{lecture_id}_p{page}_{chunk_number:02d}"


def _structure_page(
    *,
    client: OpenAI,
    settings: Settings,
    lecture: LectureConfig,
    page: PageText,
    previous_text: str,
    next_text: str,
    force: bool,
) -> StructuredPageResponse:
    cache_path = (
        settings.cache_dir / lecture.lecture_id / f"page_{page.page:03d}.json"
    )
    source_hash = hashlib.sha256(
        previous_text.encode("utf-8")
        + b"\x00"
        + page.text.encode("utf-8")
        + b"\x00"
        + next_text.encode("utf-8")
        + b"\x00"
        + page.image_png
    ).hexdigest()
    if not force:
        cached = _load_cache(
            cache_path,
            source_hash,
            settings.llm_model,
            settings.vision_detail,
            settings.page_render_dpi,
        )
        if cached is not None:
            LOGGER.info("캐시 사용: %s p.%s", lecture.lecture_id, page.page)
            return cached

    candidates: list[StructuredChunk] = []
    segments = split_long_text(page.text, settings.max_page_chars)
    image_data_url = page_image_data_url(page)
    for segment_number, segment in enumerate(segments, start=1):
        response = _call_with_retries(
            client=client,
            model=settings.llm_model,
            lecture=lecture,
            page=page.page,
            segment=segment,
            segment_number=segment_number,
            segment_count=len(segments),
            image_data_url=image_data_url,
            vision_detail=settings.vision_detail,
            previous_text=previous_text,
            next_text=next_text,
            max_retries=settings.max_retries,
        )
        candidates.extend(_preserve_source_text(response.chunks, segment))

    result = StructuredPageResponse(chunks=candidates)
    write_json(
        cache_path,
        {
            "lecture_id": lecture.lecture_id,
            "page": page.page,
            "source_sha256": source_hash,
            "model": settings.llm_model,
            "vision_detail": settings.vision_detail,
            "render_dpi": settings.page_render_dpi,
            "cache_version": STRUCTURE_CACHE_VERSION,
            "result": result.model_dump(mode="json"),
        },
    )
    return result


def _call_with_retries(
    *,
    client: OpenAI,
    model: str,
    lecture: LectureConfig,
    page: int,
    segment: str,
    segment_number: int,
    segment_count: int,
    image_data_url: str,
    vision_detail: str,
    previous_text: str,
    next_text: str,
    max_retries: int,
) -> StructuredPageResponse:
    user_prompt = f"""다음은 '{lecture.lecture_name}' 강의안의 {page}페이지 내용이다.
이 페이지를 RAG 지식베이스에 넣기 좋은 형태로 구조화하라.

페이지 전체가 하나의 주제라면 Chunk 하나만 생성한다.
서로 다른 주요 주제가 여러 개라면 의미 단위로 Chunk를 나눈다.
첨부된 페이지 이미지 전체를 반드시 확인한다.
이미지 속 글자, 표의 행과 열, 그래프의 축/범례/분포, 도형과 화살표의 관계,
코드 및 실행 결과를 빠짐없이 확인하되 강의안 밖의 의미는 추측하지 않는다.
raw_text는 아래 '추출 텍스트'에서만 정확히 복사하고, 이미지에서만 읽힌 정보는
visual_description과 content에 기록한다.

분할 구간: {segment_number}/{segment_count}

이전 페이지 추출 텍스트(문맥 참고 전용, 현재 Chunk에 복사 금지):
---
{previous_text}
---

현재 페이지 추출 텍스트:
---
{segment}
---

다음 페이지 추출 텍스트(문맥 참고 전용, 현재 Chunk에 복사 금지):
---
{next_text}
---
"""
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.responses.parse(
                model=model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": user_prompt},
                            {
                                "type": "input_image",
                                "image_url": image_data_url,
                                "detail": vision_detail,
                            },
                        ],
                    },
                ],
                text_format=StructuredPageResponse,
            )
            if response.output_parsed is None:
                raise RuntimeError("구조화 응답이 비어 있습니다.")
            return response.output_parsed
        except Exception as exc:  # SDK/network/schema errors all need retry here.
            last_error = exc
            LOGGER.warning(
                "LLM 호출 실패 (%s p.%s, %s/%s): %s",
                lecture.lecture_id,
                page,
                attempt,
                max_retries,
                exc,
            )
            if attempt < max_retries:
                time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError(
        f"{lecture.lecture_id} p.{page} 구조화에 {max_retries}회 실패했습니다."
    ) from last_error


def _load_cache(
    cache_path: Path,
    source_hash: str,
    model: str,
    vision_detail: str,
    render_dpi: int,
) -> StructuredPageResponse | None:
    if not cache_path.is_file():
        return None
    try:
        payload = read_json(cache_path)
        if (
            payload.get("source_sha256") != source_hash
            or payload.get("model") != model
            or payload.get("vision_detail") != vision_detail
            or payload.get("render_dpi") != render_dpi
            or payload.get("cache_version") != STRUCTURE_CACHE_VERSION
        ):
            return None
        return StructuredPageResponse.model_validate(payload["result"])
    except (OSError, KeyError, TypeError, ValueError, ValidationError):
        LOGGER.warning("손상되거나 오래된 캐시를 무시합니다: %s", cache_path)
        return None


def _preserve_source_text(
    chunks: list[StructuredChunk], source_text: str
) -> list[StructuredChunk]:
    """Keep model-written summaries, but never accept invented raw source text."""
    normalized_source = _normalize_whitespace(source_text)
    preserved: list[StructuredChunk] = []
    for chunk in chunks:
        raw_text = chunk.raw_text
        if _normalize_whitespace(raw_text) not in normalized_source:
            LOGGER.warning("LLM raw_text가 원문과 달라 해당 입력 구간으로 대체합니다.")
            raw_text = source_text
        preserved.append(chunk.model_copy(update={"raw_text": raw_text}))
    return preserved


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())
