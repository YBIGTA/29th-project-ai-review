from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openai import OpenAI  # noqa: E402

from src.config import Settings  # noqa: E402
from src.evaluation import (  # noqa: E402
    load_branch_evidence,
    load_branch_terminology,
    load_rubric,
    score_topic_assessment,
    select_objective_branch,
)
from src.evaluation_api import (  # noqa: E402
    AssessmentValidationError,
    request_validated_evaluation_assessment,
)
from src.evaluation_prompt import (  # noqa: E402
    EVALUATION_SYSTEM_PROMPT,
    build_evaluation_prompt,
)
from src.transcript import segment_transcript  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="서버 없이 Rubric 평가 API를 직접 호출합니다."
    )
    parser.add_argument("--lecture", default="basic_statistics")
    parser.add_argument("--objective", required=True)
    parser.add_argument("--text", help="평가할 발화문을 명령행에서 직접 전달합니다.")
    parser.add_argument(
        "--transcript-file",
        type=Path,
        help="UTF-8 발화문 텍스트 파일 경로입니다.",
    )
    parser.add_argument("--model", help="미지정 시 .env의 LLM_MODEL을 사용합니다.")
    parser.add_argument("--output", type=Path, help="결과 JSON을 저장할 경로입니다.")
    return parser.parse_args()


def read_transcript(args: argparse.Namespace) -> str:
    if args.text and args.transcript_file:
        raise ValueError("--text와 --transcript-file은 동시에 사용할 수 없습니다.")
    if args.text:
        transcript = args.text
    elif args.transcript_file:
        transcript = args.transcript_file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        transcript = sys.stdin.read()
    else:
        raise ValueError("--text, --transcript-file 또는 표준입력으로 발화문을 주세요.")
    transcript = transcript.strip()
    if not transcript:
        raise ValueError("발화문이 비어 있습니다.")
    return transcript


def main() -> None:
    args = parse_args()
    transcript = read_transcript(args)
    settings = Settings.from_env(require_api_key=True)
    rubric_path = (
        settings.project_root
        / "data"
        / "evaluation"
        / "rubrics"
        / f"{args.lecture}.json"
    )
    processed_path = settings.processed_dir / f"{args.lecture}.json"
    rubric = load_rubric(rubric_path)
    branch = select_objective_branch(rubric, args.objective)
    evidence = load_branch_evidence(
        rubric,
        args.objective,
        processed_path,
    )
    terminology = load_branch_terminology(
        rubric,
        args.objective,
        processed_path,
    )
    segments = segment_transcript(transcript)
    prompt = build_evaluation_prompt(
        rubric=rubric,
        branch=branch,
        transcript=transcript,
        segments=segments,
        evidence_chunks=evidence,
        terminology=terminology,
    )
    try:
        assessment = request_validated_evaluation_assessment(
            client=OpenAI(api_key=settings.openai_api_key),
            model=args.model or settings.llm_model,
            input_messages=[
                {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_retries=settings.max_retries,
            rubric=rubric,
            valid_segments={segment.segment_id: segment.text for segment in segments},
            transcript=transcript,
        )
    except AssessmentValidationError as exc:
        invalid_output = (
            args.output.with_suffix(".invalid.json")
            if args.output
            else ROOT / "outputs" / "evaluation_invalid.json"
        )
        invalid_output.parent.mkdir(parents=True, exist_ok=True)
        invalid_output.write_text(
            exc.assessment.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            f"검증 실패한 LLM 원본 응답을 저장했습니다: {invalid_output}",
            file=sys.stderr,
        )
        raise
    score = score_topic_assessment(rubric, assessment)
    result = {
        "model": args.model or settings.llm_model,
        "lecture_id": rubric.lecture_id,
        "objective_id": branch.objective_id,
        "objective_title": branch.title,
        "transcript": transcript,
        "segments": [segment.model_dump(mode="json") for segment in segments],
        "assessment": assessment.model_dump(mode="json"),
        "score": score,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
