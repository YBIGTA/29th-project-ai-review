from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.transcript import segment_transcript  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="평가 API를 호출하지 않고 발화문을 결정적 Segment로 나눕니다."
    )
    parser.add_argument("--transcript-file", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    transcript = args.transcript_file.read_text(encoding="utf-8").strip()
    segments = segment_transcript(transcript)
    rendered = json.dumps(
        [segment.model_dump(mode="json") for segment in segments],
        ensure_ascii=False,
        indent=2,
    ) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
