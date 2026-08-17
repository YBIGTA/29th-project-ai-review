from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from src.config import LECTURES, Settings
from src.search import search


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ChromaDB 의미 검색을 테스트합니다.")
    parser.add_argument("query", nargs="?", help="검색할 문장")
    parser.add_argument("--lecture-id", choices=sorted(LECTURES), default=None)
    parser.add_argument("--top-k", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    query = args.query or input("검색 문장을 입력하세요: ").strip()
    settings = Settings.from_env(require_api_key=True)
    client = OpenAI(api_key=settings.openai_api_key)
    hits = search(
        client=client,
        settings=settings,
        query=query,
        top_k=args.top_k,
        lecture_id=args.lecture_id,
    )
    if not hits:
        print("검색 결과가 없습니다.")
        return
    for hit in hits:
        print(
            f"\n{hit.rank}. {hit.lecture_name} / p.{hit.page} / {hit.topic}\n"
            f"chunk_id: {hit.chunk_id}\n"
            f"cosine distance: {hit.distance:.4f}\n"
            f"{hit.content}"
        )


if __name__ == "__main__":
    main()

