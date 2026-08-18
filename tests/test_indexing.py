from __future__ import annotations

from pathlib import Path

from src.config import PROJECT_ROOT
from src.embedding import build_embedding_text
from src.indexing import (
    load_embedding_manifest,
    prepare_index_selections,
    sha256_texts,
)


MANIFEST_PATH = PROJECT_ROOT / "data" / "indexing" / "embedding_manifest.json"


def test_embedding_manifest_selects_reviewed_chunks() -> None:
    manifest = load_embedding_manifest(MANIFEST_PATH)
    selections = prepare_index_selections(
        manifest=manifest,
        project_root=PROJECT_ROOT,
    )

    counts = {
        selection.original.lecture_id: (
            selection.total_count,
            selection.indexed_count,
            len(selection.excluded),
        )
        for selection in selections
    }
    assert counts == {
        "basic_statistics": (42, 36, 6),
        "crawling": (21, 14, 7),
        "eda_fe": (42, 35, 7),
        "visualization": (39, 32, 7),
    }
    assert sum(selection.total_count for selection in selections) == 144
    assert sum(selection.indexed_count for selection in selections) == 117


def test_embedding_manifest_excludes_only_explicit_chunk_ids() -> None:
    manifest = load_embedding_manifest(MANIFEST_PATH)
    selections = prepare_index_selections(
        manifest=manifest,
        project_root=PROJECT_ROOT,
    )

    for selection in selections:
        all_ids = {chunk.chunk_id for chunk in selection.original.chunks}
        selected_ids = {chunk.chunk_id for chunk in selection.selected.chunks}
        excluded_ids = {entry.chunk_id for entry in selection.excluded}
        assert selected_ids == all_ids - excluded_ids
        assert selected_ids.isdisjoint(excluded_ids)


def test_all_selected_chunks_have_nonempty_embedding_text() -> None:
    manifest = load_embedding_manifest(MANIFEST_PATH)
    selections = prepare_index_selections(
        manifest=manifest,
        project_root=PROJECT_ROOT,
    )

    texts = [
        build_embedding_text(chunk)
        for selection in selections
        for chunk in selection.selected.chunks
    ]
    assert len(texts) == 117
    assert all(text.strip() for text in texts)
    assert len(sha256_texts(texts)) == 64


def test_selection_can_be_limited_to_one_lecture() -> None:
    manifest = load_embedding_manifest(MANIFEST_PATH)
    selections = prepare_index_selections(
        manifest=manifest,
        project_root=Path(PROJECT_ROOT),
        lecture_ids={"crawling"},
    )

    assert [selection.original.lecture_id for selection in selections] == [
        "crawling"
    ]
