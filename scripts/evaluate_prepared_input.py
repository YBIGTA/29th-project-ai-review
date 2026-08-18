from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI

from src.config import Settings
from src.evaluation import load_rubric, validate_assessment_against_rubric
from src.evaluation_api import request_evaluation_assessment
from src.io_utils import read_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="준비된 평가 입력을 OpenAI Responses API로 판정합니다."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="판정 JSON 경로(기본값: outputs/evaluations/..._assessment.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env(require_api_key=True)
    input_path = _resolve_path(args.input, settings.project_root)
    if not input_path.is_file():
        raise FileNotFoundError(f"준비된 평가 입력 파일이 없습니다: {input_path}")

    payload = read_json(input_path)
    lecture_id = _required_string(payload, "lecture_id")
    model = _required_string(payload, "llm_model")
    request_payload = payload.get("llm_request")
    if not isinstance(request_payload, dict):
        raise ValueError("llm_request가 없거나 객체가 아닙니다.")
    input_messages = _validate_input_messages(request_payload.get("input"))

    rubric_path = (
        settings.project_root
        / "data"
        / "evaluation"
        / "rubrics"
        / f"{lecture_id}.json"
    )
    rubric = load_rubric(rubric_path)
    assessment = request_evaluation_assessment(
        client=OpenAI(api_key=settings.openai_api_key),
        model=model,
        input_messages=input_messages,
        max_retries=settings.max_retries,
    )
    validate_assessment_against_rubric(assessment, rubric)

    output_path = args.output
    if output_path is None:
        output_path = (
            settings.project_root
            / "outputs"
            / "evaluations"
            / f"{input_path.stem}_assessment.json"
        )
    else:
        output_path = _resolve_path(output_path, settings.project_root)
    write_json(output_path, assessment.model_dump(mode="json"))

    print(f"평가 API 호출 완료: {output_path}")
    print(f"모델: {model}")
    print(f"주장 판정: {len(assessment.claim_assessments)}개")
    print(f"학습목표 판정: {len(assessment.objective_assessments)}개")
    print(f"관계 판정: {len(assessment.relation_assessments)}개")
    print(f"관계 체인 판정: {len(assessment.chain_assessments)}개")


def _resolve_path(path: Path, project_root: Path) -> Path:
    return path if path.is_absolute() else project_root / path


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key}가 없거나 문자열이 아닙니다.")
    return value.strip()


def _validate_input_messages(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError("llm_request.input이 없거나 배열이 아닙니다.")
    messages: list[dict[str, Any]] = []
    for index, message in enumerate(value, start=1):
        if not isinstance(message, dict):
            raise ValueError(f"입력 메시지 {index}가 객체가 아닙니다.")
        role = message.get("role")
        content = message.get("content")
        if role not in {"system", "user"}:
            raise ValueError(f"입력 메시지 {index}의 role이 잘못됐습니다: {role}")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"입력 메시지 {index}의 content가 비어 있습니다.")
        messages.append({"role": role, "content": content})
    return messages


if __name__ == "__main__":
    main()
