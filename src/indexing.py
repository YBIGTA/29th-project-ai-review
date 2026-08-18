from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from src.io_utils import read_json
from src.schemas import LectureDocument, StrictModel


ExclusionReason = Literal[
    "cover",
    "table_of_contents",
    "section_divider",
    "empty_activity_divider",
    "closing",
]


class ExcludedChunk(StrictModel):
    chunk_id: str = Field(min_length=1)
    reason: ExclusionReason
    note: str = Field(min_length=1)


class ReviewFlag(StrictModel):
    chunk_id: str = Field(min_length=1)
    flag: Literal["source_claim_needs_review"]
    note: str = Field(min_length=1)


class LectureIndexPolicy(StrictModel):
    lecture_id: str = Field(min_length=1)
    processed_file: str = Field(min_length=1)
    expected_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_chunk_count: int = Field(ge=1)
    excluded_chunks: list[ExcludedChunk] = Field(default_factory=list)
    review_flags: list[ReviewFlag] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_chunk_references(self) -> "LectureIndexPolicy":
        excluded_ids = [entry.chunk_id for entry in self.excluded_chunks]
        flagged_ids = [entry.chunk_id for entry in self.review_flags]
        if len(excluded_ids) != len(set(excluded_ids)):
            raise ValueError(f"{self.lecture_id}: 제외 chunk_id가 중복되었습니다.")
        if len(flagged_ids) != len(set(flagged_ids)):
            raise ValueError(f"{self.lecture_id}: 검토 표시 chunk_id가 중복되었습니다.")
        overlap = sorted(set(excluded_ids) & set(flagged_ids))
        if overlap:
            raise ValueError(
                f"{self.lecture_id}: 제외 Chunk에는 검토 표시를 붙일 수 없습니다: {overlap}"
            )
        return self


class EmbeddingManifest(StrictModel):
    schema_version: Literal["1.0.0"]
    default_action: Literal["include"]
    embedding_model: Literal["text-embedding-3-small"]
    embedding_text_fields: list[
        Literal["topic", "concepts", "visual_description", "content"]
    ]
    expected_total_chunks: int = Field(ge=1)
    expected_indexed_chunks: int = Field(ge=1)
    lectures: list[LectureIndexPolicy] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_manifest(self) -> "EmbeddingManifest":
        lecture_ids = [policy.lecture_id for policy in self.lectures]
        if len(lecture_ids) != len(set(lecture_ids)):
            raise ValueError("manifest의 lecture_id가 중복되었습니다.")
        expected_fields = ["topic", "concepts", "visual_description", "content"]
        if self.embedding_text_fields != expected_fields:
            raise ValueError(
                "embedding_text_fields의 순서가 현재 build_embedding_text와 다릅니다."
            )
        return self


@dataclass(frozen=True)
class IndexSelection:
    source_path: Path
    source_sha256: str
    original: LectureDocument
    selected: LectureDocument
    excluded: list[ExcludedChunk]
    review_flags: list[ReviewFlag]

    @property
    def total_count(self) -> int:
        return len(self.original.chunks)

    @property
    def indexed_count(self) -> int:
        return len(self.selected.chunks)


def load_embedding_manifest(path: Path) -> EmbeddingManifest:
    return EmbeddingManifest.model_validate(read_json(path))


def prepare_index_selections(
    *,
    manifest: EmbeddingManifest,
    project_root: Path,
    lecture_ids: set[str] | None = None,
) -> list[IndexSelection]:
    available_ids = {policy.lecture_id for policy in manifest.lectures}
    requested_ids = lecture_ids or available_ids
    unknown = sorted(requested_ids - available_ids)
    if unknown:
        raise ValueError(f"manifest에 없는 lecture_id입니다: {unknown}")

    all_selections = [
        _prepare_selection(policy=policy, project_root=project_root)
        for policy in manifest.lectures
    ]
    total_chunks = sum(selection.total_count for selection in all_selections)
    indexed_chunks = sum(selection.indexed_count for selection in all_selections)
    all_chunk_ids = [
        chunk.chunk_id
        for selection in all_selections
        for chunk in selection.original.chunks
    ]
    if len(all_chunk_ids) != len(set(all_chunk_ids)):
        raise ValueError("강의 간에 중복된 chunk_id가 있습니다.")
    if total_chunks != manifest.expected_total_chunks:
        raise ValueError(
            "전체 Chunk 수가 manifest와 다릅니다: "
            f"expected={manifest.expected_total_chunks}, actual={total_chunks}"
        )
    if indexed_chunks != manifest.expected_indexed_chunks:
        raise ValueError(
            "임베딩 대상 Chunk 수가 manifest와 다릅니다: "
            f"expected={manifest.expected_indexed_chunks}, actual={indexed_chunks}"
        )
    return [
        selection
        for selection in all_selections
        if selection.original.lecture_id in requested_ids
    ]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_texts(texts: list[str]) -> str:
    digest = hashlib.sha256()
    for text in texts:
        encoded = text.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, byteorder="big"))
        digest.update(encoded)
    return digest.hexdigest()


def _prepare_selection(
    *, policy: LectureIndexPolicy, project_root: Path
) -> IndexSelection:
    source_path = (project_root / policy.processed_file).resolve()
    if project_root.resolve() not in source_path.parents:
        raise ValueError(
            f"processed_file은 project 폴더 안에 있어야 합니다: {policy.processed_file}"
        )
    if not source_path.is_file():
        raise FileNotFoundError(f"구조화 JSON이 없습니다: {source_path}")

    actual_sha256 = sha256_file(source_path)
    if actual_sha256 != policy.expected_sha256:
        raise ValueError(
            f"{policy.lecture_id}: 구조화 JSON이 manifest 검토 이후 변경되었습니다. "
            "Chunk 선별 기준을 다시 검토하고 expected_sha256을 갱신하세요."
        )

    document = LectureDocument.model_validate(read_json(source_path))
    if document.lecture_id != policy.lecture_id:
        raise ValueError(
            f"lecture_id가 다릅니다: manifest={policy.lecture_id}, "
            f"document={document.lecture_id}"
        )
    if len(document.chunks) != policy.expected_chunk_count:
        raise ValueError(
            f"{policy.lecture_id}: Chunk 수가 다릅니다: "
            f"expected={policy.expected_chunk_count}, actual={len(document.chunks)}"
        )

    chunk_ids = [chunk.chunk_id for chunk in document.chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError(f"{policy.lecture_id}: 구조화 JSON의 chunk_id가 중복되었습니다.")
    known_ids = set(chunk_ids)
    referenced_ids = {
        entry.chunk_id for entry in policy.excluded_chunks
    } | {entry.chunk_id for entry in policy.review_flags}
    missing = sorted(referenced_ids - known_ids)
    if missing:
        raise ValueError(
            f"{policy.lecture_id}: JSON에 존재하지 않는 chunk_id가 있습니다: {missing}"
        )

    excluded_ids = {entry.chunk_id for entry in policy.excluded_chunks}
    selected_chunks = [
        chunk for chunk in document.chunks if chunk.chunk_id not in excluded_ids
    ]
    if not selected_chunks:
        raise ValueError(f"{policy.lecture_id}: 임베딩 대상 Chunk가 하나도 없습니다.")
    selected = document.model_copy(update={"chunks": selected_chunks})
    return IndexSelection(
        source_path=source_path,
        source_sha256=actual_sha256,
        original=document,
        selected=selected,
        excluded=policy.excluded_chunks,
        review_flags=policy.review_flags,
    )
