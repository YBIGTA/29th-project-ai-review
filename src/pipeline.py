from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from src.config import LECTURES, Settings, resolve_pdf_path
from src.core_concepts import generate_core_concepts
from src.embedding import build_embedding_text, create_embeddings
from src.io_utils import write_json
from src.pdf_loader import PdfLoadResult, load_pdf_pages
from src.schemas import LectureDocument
from src.structure_lecture import structure_lecture
from src.vector_store import LectureVectorStore


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessResult:
    lecture_id: str
    total_pdf_pages: int
    processed_pages: int
    empty_pages: list[int]
    chunks: int
    processed_path: Path
    core_concepts_created: bool
    indexed_chunks: int


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
    create_core_concepts: bool = True,
    build_index: bool = True,
) -> ProcessResult:
    if lecture_id not in LECTURES:
        raise ValueError(
            f"알 수 없는 lecture_id입니다: {lecture_id}. "
            f"가능한 값: {', '.join(LECTURES)}"
        )
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages는 1 이상이어야 합니다.")
    if max_pages is not None and (create_core_concepts or build_index):
        raise ValueError(
            "일부 페이지만 처리할 때는 불완전한 평가 기준/DB 생성을 막기 위해 "
            "핵심 개념 생성과 인덱싱을 건너뛰어야 합니다."
        )

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

    core_created = False
    if create_core_concepts:
        generate_core_concepts(client=client, settings=settings, lecture=document)
        core_created = True

    indexed_chunks = 0
    if build_index:
        texts = [build_embedding_text(chunk) for chunk in document.chunks]
        embeddings = create_embeddings(
            client=client,
            texts=texts,
            model=settings.embedding_model,
            batch_size=settings.embedding_batch_size,
        )
        store = LectureVectorStore(
            path=settings.vector_db_path,
            collection_name=settings.collection_name,
            embedding_model=settings.embedding_model,
        )
        indexed_chunks = store.upsert_lecture(document, embeddings)
        LOGGER.info("ChromaDB 저장: %s chunks", indexed_chunks)

    return ProcessResult(
        lecture_id=lecture_id,
        total_pdf_pages=loaded.total_pages,
        processed_pages=len(selected.pages),
        empty_pages=loaded.empty_pages,
        chunks=len(document.chunks),
        processed_path=processed_path,
        core_concepts_created=core_created,
        indexed_chunks=indexed_chunks,
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
