from __future__ import annotations

import json

import pytest

from src.config import LECTURES, Settings, resolve_pdf_path
from src.pdf_loader import load_pdf_pages
from src.schemas import LectureDocument


EXPECTED_PAGE_COUNTS = {
    "basic_statistics": 42,
    "crawling": 21,
    "eda_fe": 42,
    "visualization": 39,
    "cs_basics": 44,
    "git": 32,
    "python_environment": 61,
    "web": 29,
    "network_basics": 28,
    "machine_learning": 51,
    "deep_learning": 54,
    "computer_vision": 42,
    "nlp": 52,
}


@pytest.mark.parametrize("lecture_id", EXPECTED_PAGE_COUNTS)
def test_curated_document_covers_pdf_exactly(lecture_id: str) -> None:
    settings = Settings.from_env()
    output = settings.processed_dir / f"{lecture_id}.json"
    payload = json.loads(output.read_text(encoding="utf-8"))
    document = LectureDocument.model_validate(payload)

    expected_count = EXPECTED_PAGE_COUNTS[lecture_id]
    assert len(document.chunks) == expected_count
    assert [chunk.page for chunk in document.chunks] == list(range(1, expected_count + 1))
    assert len({chunk.chunk_id for chunk in document.chunks}) == expected_count

    lecture = LECTURES[lecture_id]
    loaded = load_pdf_pages(
        resolve_pdf_path(settings, lecture),
        render_dpi=settings.page_render_dpi,
    )
    assert loaded.total_pages == expected_count
    assert [chunk.raw_text for chunk in document.chunks] == [page.text for page in loaded.pages]

    for chunk in document.chunks:
        assert chunk.lecture_id == lecture_id
        assert chunk.lecture_name == lecture.lecture_name
        assert chunk.topic
        assert chunk.concepts
        assert chunk.visual_description
        assert chunk.content

    if lecture_id in {
        "basic_statistics",
        "crawling",
        "eda_fe",
        "visualization",
        "cs_basics",
        "git",
        "python_environment",
        "web",
        "network_basics",
        "machine_learning",
        "deep_learning",
        "computer_vision",
        "nlp",
    }:
        assert document.schema_version == "2.1.0"
        assert document.terminology
        assert sum(len(chunk.evidence_units) for chunk in document.chunks) > 0
        assert all(
            not chunk.evidence_units
            for chunk in document.chunks
            if chunk.page_role in {
                "cover", "table_of_contents", "section_divider", "closing"
            }
        )
