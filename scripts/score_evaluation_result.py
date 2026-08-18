from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import LECTURES, Settings
from src.evaluation import (
    load_assessment,
    load_profile,
    load_rubric,
    score_evaluation,
    validate_assessment_against_rubric,
    validate_profile_against_rubric,
)
from src.io_utils import write_json


PROFILE_SUFFIXES = {
    "2min": "free_recall_demo_2min",
    "3min": "free_recall_3min",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="구조화된 LLM 판정 결과를 40·40·20 기준으로 계산합니다."
    )
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--lecture-id", choices=sorted(LECTURES), required=True)
    parser.add_argument("--profile", choices=sorted(PROFILE_SUFFIXES), required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="점수 JSON 경로(기본값: outputs/scores/..._score.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env()
    assessment_path = _resolve_path(args.assessment, settings.project_root)
    if not assessment_path.is_file():
        raise FileNotFoundError(f"평가 판정 파일이 없습니다: {assessment_path}")

    evaluation_dir = settings.project_root / "data" / "evaluation"
    rubric = load_rubric(
        evaluation_dir / "rubrics" / f"{args.lecture_id}.json"
    )
    profile = load_profile(
        evaluation_dir
        / "profiles"
        / f"{args.lecture_id}_{PROFILE_SUFFIXES[args.profile]}.json"
    )
    assessment = load_assessment(assessment_path)
    validate_profile_against_rubric(profile, rubric)
    validate_assessment_against_rubric(assessment, rubric)
    score = score_evaluation(rubric, assessment, profile)

    output_path = args.output
    if output_path is None:
        output_path = (
            settings.project_root
            / "outputs"
            / "scores"
            / f"{assessment_path.stem}_score.json"
        )
    else:
        output_path = _resolve_path(output_path, settings.project_root)
    write_json(output_path, score)

    print(f"점수 계산 완료: {output_path}")
    print(f"개념 정확도: {score['concept_accuracy']:.2f} / 40")
    print(f"핵심 개념 충족도: {score['core_fulfillment']:.2f} / 40")
    print(f"구조적 이해도: {score['structural_understanding']:.2f} / 20")
    print(f"총점: {score['total_score']:.2f} / 100")


def _resolve_path(path: Path, project_root: Path) -> Path:
    return path if path.is_absolute() else project_root / path


if __name__ == "__main__":
    main()
