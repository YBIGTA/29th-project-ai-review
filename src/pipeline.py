from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from src.config import LECTURES, Settings, resolve_pdf_path
from src.io_utils import write_json
from src.pdf_loader import PdfLoadResult, load_pdf_pages
from src.schemas import LectureDocument
from src.structure_lecture import structure_lecture


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessResult:
    lecture_id: str
    total_pdf_pages: int
    processed_pages: int
    empty_pages: list[int]
    chunks: int
    processed_path: Path


def configure_logging(settings: Settings) -> None:
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
        logging.FileHandler(settings.logs_dir / "pipeline.log", encoding="utf-8"),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


def process_lecture(
    *,
    lecture_id: str,
    client: OpenAI,
    settings: Settings,
    force: bool = False,
    max_pages: int | None = None,
) -> ProcessResult:
    if lecture_id not in LECTURES:
        raise ValueError(
            f"알 수 없는 lecture_id입니다: {lecture_id}. "
            f"가능한 값: {', '.join(LECTURES)}"
        )
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages는 1 이상이어야 합니다.")

    settings.ensure_output_dirs()
    lecture = LECTURES[lecture_id]
    pdf_path = resolve_pdf_path(settings, lecture)
    LOGGER.info("PDF 로드: %s", pdf_path)
    loaded = load_pdf_pages(pdf_path, render_dpi=settings.page_render_dpi)
    selected = loaded
    if max_pages is not None:
        selected = PdfLoadResult(
            source_file=loaded.source_file,
            total_pages=loaded.total_pages,
            pages=loaded.pages[:max_pages],
            empty_pages=loaded.empty_pages,
        )
    if not selected.pages:
        raise RuntimeError(f"{lecture.lecture_name} PDF에 처리할 페이지가 없습니다.")

    document = structure_lecture(
        client=client,
        settings=settings,
        lecture=lecture,
        pdf=selected,
        force=force,
    )
    _validate_page_coverage(document, {page.page for page in selected.pages})
    suffix = f".partial_{max_pages}" if max_pages is not None else ""
    processed_path = settings.processed_dir / f"{lecture_id}{suffix}.json"
    write_json(processed_path, document.model_dump(mode="json"))
    LOGGER.info("구조화 JSON 저장: %s (%s chunks)", processed_path, len(document.chunks))

    return ProcessResult(
        lecture_id=lecture_id,
        total_pdf_pages=loaded.total_pages,
        processed_pages=len(selected.pages),
        empty_pages=loaded.empty_pages,
        chunks=len(document.chunks),
        processed_path=processed_path,
    )


def _validate_page_coverage(
    document: LectureDocument, expected_pages: set[int]
) -> None:
    actual_pages = {chunk.page for chunk in document.chunks}
    missing = sorted(expected_pages - actual_pages)
    extra = sorted(actual_pages - expected_pages)
    if missing or extra:
        raise RuntimeError(
            f"페이지 구조화 범위가 원본과 다릅니다. missing={missing}, extra={extra}"
        )
