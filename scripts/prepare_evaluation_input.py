from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from src.config import LECTURES, Settings
from src.evaluation import (
    load_profile,
    load_rubric,
    validate_profile_against_rubric,
)
from src.evaluation_prompt import EVALUATION_SYSTEM_PROMPT, build_evaluation_prompt
from src.evaluation_schemas import EvaluationAssessment
from src.io_utils import read_json, write_json
from src.search import search_transcript


PROFILE_SUFFIXES = {
    "2min": "free_recall_demo_2min",
    "3min": "free_recall_3min",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "STT 검색 결과, 전체 Rubric, 시간 프로필을 평가 LLM 입력으로 조립합니다. "
            "임베딩 API만 호출하며 평가 LLM은 호출하지 않습니다."
        )
    )
    parser.add_argument("--file", type=Path, required=True, help="UTF-8 STT 텍스트 파일")
    parser.add_argument("--lecture-id", choices=sorted(LECTURES), required=True)
    parser.add_argument("--profile", choices=sorted(PROFILE_SUFFIXES), required=True)
    parser.add_argument("--top-k-per-segment", type=int, default=5)
    parser.add_argument("--max-evidence", type=int, default=12)
    parser.add_argument(
        "--max-distance",
        type=float,
        default=None,
        help="최종 근거의 최대 cosine distance(기본값: 제한 없음)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="평가 입력 JSON 경로(기본값: outputs/evaluation_inputs/...)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env(require_api_key=True)
    transcript_path = args.file.resolve()
    if not transcript_path.is_file():
        raise FileNotFoundError(f"STT 텍스트 파일이 없습니다: {transcript_path}")
    transcript = transcript_path.read_text(encoding="utf-8").strip()
    if not transcript:
        raise ValueError("STT 텍스트 파일이 비어 있습니다.")

    evaluation_dir = settings.project_root / "data" / "evaluation"
    rubric_path = evaluation_dir / "rubrics" / f"{args.lecture_id}.json"
    profile_suffix = PROFILE_SUFFIXES[args.profile]
    profile_path = (
        evaluation_dir
        / "profiles"
        / f"{args.lecture_id}_{profile_suffix}.json"
    )
    policy_path = evaluation_dir / "scoring_policy.json"

    rubric = load_rubric(rubric_path)
    profile = load_profile(profile_path)
    validate_profile_against_rubric(profile, rubric)
    scoring_policy = read_json(policy_path)
    search_result = search_transcript(
        client=OpenAI(api_key=settings.openai_api_key),
        settings=settings,
        transcript=transcript,
        lecture_id=args.lecture_id,
        top_k_per_segment=args.top_k_per_segment,
        max_evidence=args.max_evidence,
        max_distance=args.max_distance,
    )
    user_prompt = build_evaluation_prompt(
        rubric,
        transcript,
        profile,
        search_result=search_result,
        scoring_policy=scoring_policy,
    )

    output_path = args.output
    if output_path is None:
        output_path = (
            settings.project_root
            / "outputs"
            / "evaluation_inputs"
            / f"{args.lecture_id}_{args.profile}.json"
        )
    elif not output_path.is_absolute():
        output_path = settings.project_root / output_path

    payload = {
        "schema_version": "1.0.0",
        "lecture_id": args.lecture_id,
        "profile_id": profile.profile_id,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "source_transcript": str(transcript_path),
        "retrieval": search_result.model_dump(mode="json"),
        "llm_request": {
            "input": [
                {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "text_format": "EvaluationAssessment",
            "expected_output_schema": EvaluationAssessment.model_json_schema(),
        },
    }
    write_json(output_path, payload)

    print(f"평가 입력 준비 완료: {output_path}")
    print(f"의미 구간: {len(search_result.segment_results)}개")
    print(f"최종 검색 근거: {len(search_result.evidence)}개")
    print(f"프로필: {profile.profile_id}")
    print("평가 LLM 호출: 없음")


if __name__ == "__main__":
    main()
