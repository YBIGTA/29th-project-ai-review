from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from src.config import LECTURES, Settings
from src.search import search_transcript, segment_transcript


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="2~3분 STT 답변을 의미 단위로 나누어 ChromaDB에서 검색합니다."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help="UTF-8 STT 텍스트 파일")
    source.add_argument("--text", help="직접 입력한 STT 답변")
    parser.add_argument("--lecture-id", choices=sorted(LECTURES), required=True)
    parser.add_argument(
        "--top-k-per-segment",
        type=int,
        default=5,
        help="의미 구간별 ChromaDB 후보 수(기본값: 5)",
    )
    parser.add_argument("--max-evidence", type=int, default=12)
    parser.add_argument(
        "--max-distance",
        type=float,
        default=None,
        help="최종 근거에 포함할 최대 cosine distance(기본값은 제한 없음)",
    )
    parser.add_argument("--min-chars", type=int, default=60)
    parser.add_argument("--target-chars", type=int, default=220)
    parser.add_argument("--max-chars", type=int, default=360)
    parser.add_argument("--max-segments", type=int, default=12)
    parser.add_argument(
        "--segment-only",
        action="store_true",
        help="API를 호출하지 않고 의미 단위 분할 결과만 확인합니다.",
    )
    parser.add_argument(
        "--show-segment-hits",
        action="store_true",
        help="최종 근거 외에 각 구간의 전체 검색 결과도 출력합니다.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    transcript = _read_transcript(file_path=args.file, text=args.text)
    if args.segment_only:
        segments = segment_transcript(
            transcript,
            min_chars=args.min_chars,
            target_chars=args.target_chars,
            max_chars=args.max_chars,
            max_segments=args.max_segments,
        )
        print(f"의미 단위: {len(segments)}개 (API 호출 없음)")
        for segment in segments:
            print(f"\n[{segment.segment_id}] {segment.text}")
        return

    settings = Settings.from_env(require_api_key=True)
    client = OpenAI(api_key=settings.openai_api_key)
    result = search_transcript(
        client=client,
        settings=settings,
        transcript=transcript,
        lecture_id=args.lecture_id,
        top_k_per_segment=args.top_k_per_segment,
        max_evidence=args.max_evidence,
        max_distance=args.max_distance,
        min_chars=args.min_chars,
        target_chars=args.target_chars,
        max_chars=args.max_chars,
        max_segments=args.max_segments,
    )

    print(f"의미 단위: {len(result.segment_results)}개")
    for segment_result in result.segment_results:
        segment = segment_result.segment
        print(f"\n[{segment.segment_id}] {segment.text}")
        if args.show_segment_hits:
            for hit in segment_result.hits:
                print(
                    f"  {hit.rank}. p.{hit.page} {hit.topic} "
                    f"(distance={hit.distance:.4f}, {hit.chunk_id})"
                )

    print(f"\n최종 중복 제거 근거: {len(result.evidence)}개")
    for evidence in result.evidence:
        matched = ", ".join(evidence.matched_segment_ids)
        print(
            f"\n{evidence.rank}. {evidence.lecture_name} / p.{evidence.page} / "
            f"{evidence.topic}\n"
            f"chunk_id: {evidence.chunk_id}\n"
            f"matched segments: {matched}\n"
            f"best cosine distance: {evidence.best_distance:.4f}\n"
            f"{evidence.content}"
        )


def _read_transcript(*, file_path: Path | None, text: str | None) -> str:
    if file_path is not None:
        if not file_path.is_file():
            raise FileNotFoundError(f"STT 텍스트 파일이 없습니다: {file_path}")
        return file_path.read_text(encoding="utf-8")
    assert text is not None
    return text


if __name__ == "__main__":
    main()
