from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from src.config import LECTURES, Settings
from src.embedding import build_embedding_text, create_embeddings
from src.indexing import (
    EmbeddingManifest,
    IndexSelection,
    load_embedding_manifest,
    prepare_index_selections,
    sha256_file,
    sha256_texts,
)
from src.io_utils import write_json
from src.vector_store import LectureVectorStore


MANIFEST_PATH = Path("data/indexing/embedding_manifest.json")
RUN_RECORD_PATH = Path("outputs/indexing/last_index_run.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "기존 data/processed JSON만 읽어 임베딩 대상을 검증하고 ChromaDB를 "
            "구축합니다. PDF 구조화 파이프라인은 실행하지 않습니다."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="API와 ChromaDB를 건드리지 않고 선별 결과만 확인합니다(기본값).",
    )
    mode.add_argument(
        "--smoke-test",
        action="store_true",
        help="첫 Chunk 하나만 임베딩하고 ChromaDB에는 저장하지 않습니다.",
    )
    mode.add_argument(
        "--execute",
        action="store_true",
        help="선별된 전체 Chunk를 임베딩하고 ChromaDB에 저장합니다.",
    )
    parser.add_argument(
        "--lecture-id",
        action="append",
        choices=sorted(LECTURES),
        help="대상 강의를 제한합니다. 여러 번 지정할 수 있습니다.",
    )
    parser.add_argument(
        "--preview-per-lecture",
        type=int,
        default=1,
        help="dry-run에서 강의별 임베딩 텍스트 미리보기 개수(기본 1).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.preview_per_lecture < 0:
        raise SystemExit("--preview-per-lecture는 0 이상이어야 합니다.")

    settings = Settings.from_env()
    manifest_path = settings.project_root / MANIFEST_PATH
    manifest = load_embedding_manifest(manifest_path)
    selections = prepare_index_selections(
        manifest=manifest,
        project_root=settings.project_root,
        lecture_ids=set(args.lecture_id) if args.lecture_id else None,
    )
    _print_selection_summary(
        selections=selections,
        manifest=manifest,
        preview_per_lecture=args.preview_per_lecture,
    )

    if not args.execute and not args.smoke_test:
        print("\nDRY RUN 완료: OpenAI API 호출 0회, ChromaDB 변경 없음")
        return

    if settings.embedding_model != manifest.embedding_model:
        raise RuntimeError(
            "EMBEDDING_MODEL과 검토된 manifest 모델이 다릅니다: "
            f"env={settings.embedding_model}, manifest={manifest.embedding_model}"
        )
    settings = Settings.from_env(require_api_key=True)
    client = OpenAI(api_key=settings.openai_api_key)

    if args.smoke_test:
        selection = selections[0]
        chunk = selection.selected.chunks[0]
        embedding = create_embeddings(
            client=client,
            texts=[build_embedding_text(chunk)],
            model=settings.embedding_model,
            batch_size=1,
        )[0]
        if not embedding:
            raise RuntimeError("Embedding 응답 벡터가 비어 있습니다.")
        print(
            f"\nSMOKE TEST 완료: {chunk.chunk_id}, dimension={len(embedding)}, "
            "ChromaDB 변경 없음"
        )
        return

    _execute_indexing(
        client=client,
        settings=settings,
        manifest=manifest,
        manifest_path=manifest_path,
        selections=selections,
    )


def _execute_indexing(
    *,
    client: OpenAI,
    settings: Settings,
    manifest: EmbeddingManifest,
    manifest_path: Path,
    selections: list[IndexSelection],
) -> None:
    embeddings_by_lecture: dict[str, list[list[float]]] = {}
    dimensions: set[int] = set()
    for selection in selections:
        texts = [
            build_embedding_text(chunk) for chunk in selection.selected.chunks
        ]
        embeddings = create_embeddings(
            client=client,
            texts=texts,
            model=settings.embedding_model,
            batch_size=settings.embedding_batch_size,
        )
        embeddings_by_lecture[selection.original.lecture_id] = embeddings
        dimensions.update(len(embedding) for embedding in embeddings)
    if len(dimensions) != 1:
        raise RuntimeError(f"Embedding 벡터 차원이 일치하지 않습니다: {dimensions}")

    store = LectureVectorStore(
        path=settings.vector_db_path,
        collection_name=settings.collection_name,
        embedding_model=settings.embedding_model,
    )
    total_indexed = 0
    for selection in selections:
        review_metadata = {
            entry.chunk_id: {
                "review_status": entry.flag,
                "review_note": entry.note,
            }
            for entry in selection.review_flags
        }
        count = store.upsert_lecture(
            selection.selected,
            embeddings_by_lecture[selection.original.lecture_id],
            metadata_overrides=review_metadata,
        )
        total_indexed += count
        print(f"저장 완료: {selection.original.lecture_id} / {count} chunks")

    run_record = _build_run_record(
        settings=settings,
        manifest=manifest,
        manifest_path=manifest_path,
        selections=selections,
        embedding_dimension=next(iter(dimensions)),
    )
    run_record_path = settings.project_root / RUN_RECORD_PATH
    write_json(run_record_path, run_record)
    print(
        f"\nINDEX 완료: {total_indexed} chunks / "
        f"run record={run_record_path.relative_to(settings.project_root)}"
    )


def _print_selection_summary(
    *,
    selections: list[IndexSelection],
    manifest: EmbeddingManifest,
    preview_per_lecture: int,
) -> None:
    total = sum(selection.total_count for selection in selections)
    indexed = sum(selection.indexed_count for selection in selections)
    print(f"Embedding model: {manifest.embedding_model}")
    print(
        "Embedding fields: " + ", ".join(manifest.embedding_text_fields)
        + " (raw_text 제외)"
    )
    print(f"선택 범위: 전체 {total} / 포함 {indexed} / 제외 {total - indexed}")

    for selection in selections:
        texts = [
            build_embedding_text(chunk) for chunk in selection.selected.chunks
        ]
        print(
            f"\n[{selection.original.lecture_id}] 전체 {selection.total_count} / "
            f"포함 {selection.indexed_count} / 제외 {len(selection.excluded)} / "
            f"입력 {sum(len(text) for text in texts):,}자 / "
            f"최대 {max(len(text) for text in texts):,}자"
        )
        for entry in selection.excluded:
            print(f"  제외 {entry.chunk_id} [{entry.reason}] {entry.note}")
        for entry in selection.review_flags:
            print(f"  검토 {entry.chunk_id} [{entry.flag}] {entry.note}")
        for chunk in selection.selected.chunks[:preview_per_lecture]:
            preview = build_embedding_text(chunk).replace("\n", " | ")
            if len(preview) > 360:
                preview = preview[:357] + "..."
            print(f"  미리보기 {chunk.chunk_id}: {preview}")


def _build_run_record(
    *,
    settings: Settings,
    manifest: EmbeddingManifest,
    manifest_path: Path,
    selections: list[IndexSelection],
    embedding_dimension: int,
) -> dict[str, Any]:
    lectures: list[dict[str, Any]] = []
    for selection in selections:
        texts = [
            build_embedding_text(chunk) for chunk in selection.selected.chunks
        ]
        lectures.append(
            {
                "lecture_id": selection.original.lecture_id,
                "source_file": str(
                    selection.source_path.relative_to(settings.project_root)
                ),
                "source_sha256": selection.source_sha256,
                "total_chunks": selection.total_count,
                "indexed_chunks": selection.indexed_count,
                "excluded_chunks": len(selection.excluded),
                "embedding_input_sha256": sha256_texts(texts),
            }
        )
    return {
        "schema_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "embedding_model": settings.embedding_model,
        "embedding_dimension": embedding_dimension,
        "collection_name": settings.collection_name,
        "selection_manifest": str(
            manifest_path.relative_to(settings.project_root)
        ),
        "selection_manifest_sha256": sha256_file(manifest_path),
        "indexed_lecture_ids": [item["lecture_id"] for item in lectures],
        "total_indexed_chunks": sum(
            item["indexed_chunks"] for item in lectures
        ),
        "lectures": lectures,
    }


if __name__ == "__main__":
    main()
