from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from src.config import LECTURES, Settings
from src.pipeline import configure_logging, process_lecture


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="강의 PDF 하나를 processed JSON으로 처리합니다.")
    parser.add_argument("lecture_id", choices=sorted(LECTURES))
    parser.add_argument("--force", action="store_true", help="페이지 캐시를 무시합니다.")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="텍스트가 있는 앞 N페이지만 처리합니다(스모크 테스트용).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env(require_api_key=True)
    configure_logging(settings)
    client = OpenAI(api_key=settings.openai_api_key)
    result = process_lecture(
        lecture_id=args.lecture_id,
        client=client,
        settings=settings,
        force=args.force,
        max_pages=args.max_pages,
    )
    print(
        f"완료: {result.lecture_id} / {result.processed_pages} pages / "
        f"{result.chunks} chunks"
    )
    if result.empty_pages:
        print(f"텍스트 없는 페이지: {result.empty_pages}")


if __name__ == "__main__":
    main()
