import pytest

from src.pipeline import _validate_page_coverage
from src.schemas import Chunk, LectureDocument


def _document_with_pages(*pages: int) -> LectureDocument:
    chunks = [
        Chunk(
            chunk_id=f"lecture_p{page}_01",
            lecture_id="lecture",
            lecture_name="강의",
            page=page,
            topic=f"주제 {page}",
            concepts=[],
            raw_text="",
            visual_description=f"페이지 {page} 시각 정보",
            content=f"페이지 {page} 내용",
        )
        for page in pages
    ]
    return LectureDocument(
        lecture_id="lecture",
        lecture_name="강의",
        source_file="lecture.pdf",
        chunks=chunks,
    )


def test_page_coverage_accepts_every_page():
    _validate_page_coverage(_document_with_pages(1, 2, 3), {1, 2, 3})


def test_page_coverage_rejects_missing_page():
    with pytest.raises(RuntimeError, match="missing=\\[2\\]"):
        _validate_page_coverage(_document_with_pages(1, 3), {1, 2, 3})

