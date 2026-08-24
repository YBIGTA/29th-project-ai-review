from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from src.config import LECTURES, Settings
from src.pipeline import configure_logging, process_lecture


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="강의 PDF 4개를 모두 처리합니다.")
    parser.add_argument("--force", action="store_true", help="페이지 캐시를 무시합니다.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env(require_api_key=True)
    configure_logging(settings)
    client = OpenAI(api_key=settings.openai_api_key)
    failures: list[str] = []
    for lecture_id in LECTURES:
        try:
            result = process_lecture(
                lecture_id=lecture_id,
                client=client,
                settings=settings,
                force=args.force,
            )
            print(
                f"완료: {lecture_id} / {result.processed_pages} pages / "
                f"{result.chunks} chunks"
            )
        except Exception as exc:
            failures.append(f"{lecture_id}: {exc}")
            print(f"실패: {lecture_id}: {exc}", file=sys.stderr)
    if failures:
        raise SystemExit("\n".join(failures))


if __name__ == "__main__":
    main()
