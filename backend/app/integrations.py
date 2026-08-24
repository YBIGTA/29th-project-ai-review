from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from openai import OpenAI

from src.config import Settings
from src.evaluation import load_profile, load_rubric, score_evaluation, validate_assessment_against_rubric
from src.evaluation_api import request_evaluation_assessment
from src.evaluation_prompt import build_evaluation_prompt
from src.search import search_transcript
from src.schemas import TranscriptSearchResult

class EvaluationResult(TypedDict):
    segments: list[dict[str, object]]
    claims: list[dict[str, object]]
    quantitative: dict[str, object]
    qualitative: dict[str, list[str]]


TOPIC_TO_LECTURE_ID = {
    "기초통계": "basic_statistics",
    "DB": "basic_statistics",
    "크롤링": "crawling",
    "EDA/FE": "eda_fe",
    "시각화": "visualization",
}


def evaluate_with_rag(
    *,
    transcript: str,
    topic: str,
    settings: Settings,
    client: OpenAI,
) -> EvaluationResult:
    lecture_id = TOPIC_TO_LECTURE_ID.get(topic)
    if lecture_id is None:
        raise ValueError(f"지원하지 않는 topic입니다: {topic}")

    evaluation_dir = settings.project_root / "data" / "evaluation"
    rubric = load_rubric(evaluation_dir / "rubrics" / f"{lecture_id}.json")
    profile = load_profile(
        evaluation_dir / "profiles" / f"{lecture_id}_free_recall_3min.json"
    )
    scoring_policy = json.loads(
        (evaluation_dir / "scoring_policy.json").read_text(encoding="utf-8")
    )
    search_result = search_transcript(
        client=client,
        settings=settings,
        transcript=transcript,
        lecture_id=lecture_id,
        top_k_per_segment=5,
        max_evidence=12,
    )
    prompt = build_evaluation_prompt(
        rubric=rubric,
        profile=profile,
        transcript=transcript,
        search_result=search_result,
        scoring_policy=scoring_policy,
    )
    assessment = request_evaluation_assessment(
        client=client,
        model=settings.llm_model,
        input_messages=[
            {"role": "system", "content": "평가 결과는 반드시 제공된 스키마로 반환하세요."},
            {"role": "user", "content": prompt},
        ],
        max_retries=settings.max_retries,
    )
    validate_assessment_against_rubric(assessment, rubric)
    score = score_evaluation(rubric, assessment, profile)
    return _to_review_result(score, assessment, rubric, search_result)


def _to_review_result(
    score: dict[str, object],
    assessment: object,
    rubric: object,
    search_result: TranscriptSearchResult,
) -> EvaluationResult:
    # The public BE schema keeps the existing FE-friendly names while the RAG
    # evaluator remains responsible for rubric-level judgment and scoring.
    assessment_data = assessment.model_dump()
    rubric_data = rubric.model_dump()
    objective_titles = {
        item["objective_id"]: item["title"]
        for item in rubric_data["learning_objectives"]
    }
    claim_titles = {
        claim["claim_id"]: claim["text"]
        for item in rubric_data["learning_objectives"]
        for claim in item["reference_claims"]
    }
    objective_by_id = {
        item["objective_id"]: item for item in assessment_data["objective_assessments"]
    }
    claim_by_id = {
        item["claim_id"]: item for item in assessment_data["claim_assessments"]
    }
    evidence_by_chunk = {item.chunk_id: item for item in search_result.evidence}
    claim_reference_chunks = {
        claim.claim_id: claim.evidence
        for objective in rubric.learning_objectives
        for claim in objective.reference_claims
    }
    rubric_pages = {
        reference.chunk_id: reference.page
        for references in claim_reference_chunks.values()
        for reference in references
    }
    claims = []
    for claim_id, item in claim_by_id.items():
        source_ids = item.get("source_chunk_ids_used") or [
            reference.chunk_id
            for reference in claim_reference_chunks.get(claim_id, [])
        ]
        source_ids = list(dict.fromkeys(source_ids))
        matched_segments = item.get("matched_segment_ids") or [
            segment_id
            for chunk_id in source_ids
            if chunk_id in evidence_by_chunk
            for segment_id in evidence_by_chunk[chunk_id].matched_segment_ids
        ]
        claims.append({
            "claim_id": claim_id,
            "judgment": item["judgment"],
            "matched_segment_ids": list(dict.fromkeys(matched_segments)),
            "evidence_quote": item["evidence_quote"],
            "rationale": item["rationale"],
            "source_chunk_ids_used": source_ids,
            "source_chunks": [
                {
                    "source_chunk_id": chunk_id,
                    "page": evidence_by_chunk[chunk_id].page
                    if chunk_id in evidence_by_chunk
                    else rubric_pages[chunk_id],
                }
                for chunk_id in source_ids
                if chunk_id in evidence_by_chunk or chunk_id in rubric_pages
            ],
        })
    relation_by_id = {
        item["relation_id"]: item for item in assessment_data["relation_assessments"]
    }
    accuracy = float(score["concept_accuracy"])
    coverage = float(score["core_fulfillment"])
    structural = float(score["structural_understanding"])
    accuracy_ratio = float(score["ratios"]["accuracy"])
    coverage_ratio = float(score["ratios"]["coverage"])
    concept_f1 = (
        2 * accuracy_ratio * coverage_ratio / (accuracy_ratio + coverage_ratio)
        if accuracy_ratio + coverage_ratio
        else 0.0
    )

    missing = [
        objective_titles[item_id]
        for item_id, item in objective_by_id.items()
        if item["judgment"] in {"absent", "partial", "name_only"}
    ]
    incorrect = [
        claim_titles[item_id]
        for item_id, item in claim_by_id.items()
        if item["judgment"] == "incorrect"
    ]
    misconnected = [
        item["rationale"]
        for item in relation_by_id.values()
        if item["judgment"] == "incorrect"
    ]
    suggestions = [
        f"'{title}'의 핵심 내용을 다시 설명해 보세요."
        for title in missing[:5]
    ]
    if misconnected:
        suggestions.append("개념 사이의 원인·목적·순서 관계를 다시 연결해 보세요.")
    accuracy_reason = _assessment_reason(
        "핵심 개념별 판단",
        [
            f"{claim_titles.get(item['claim_id'], item['claim_id'])}: {item['judgment']}"
            + (f" (근거: {item['evidence_quote']})" if item["evidence_quote"] else "")
            for item in claim_by_id.values()
            if item["judgment"] != "not_addressed"
        ],
        f"평가 대상 핵심 주장 {len(claim_by_id)}개 중 사용자 발화에서 확인된 내용을 기준으로 {accuracy_ratio:.0%}로 산정했습니다.",
        accuracy_ratio,
    )
    coverage_reason = _assessment_reason(
        "학습 목표별 판단",
        [
            f"{objective_titles.get(item['objective_id'], item['objective_id'])}: {item['judgment']}"
            for item in objective_by_id.values()
        ],
        f"필수 학습 목표의 설명 충족도를 반영해 {coverage_ratio:.0%}로 산정했습니다.",
        coverage_ratio,
    )
    structural_reason = _assessment_reason(
        "개념 관계별 판단",
        [
            f"{item['relation_id']}: {item['judgment']}"
            + (f" (근거: {item['evidence_quote']})" if item["evidence_quote"] else "")
            for item in relation_by_id.values()
        ],
        f"개념 관계와 관계 chain의 설명 결과를 반영해 {structural / 20:.0%}로 산정했습니다.",
        structural / 20,
    )
    return {
        "segments": [
            result.segment.model_dump() for result in search_result.segment_results
        ],
        "claims": claims,
        "quantitative": {
            "concept_recall": coverage_ratio,
            "concept_precision": accuracy_ratio,
            "concept_f1": concept_f1,
            "scores": {
                "accuracy": _score_detail(accuracy, 40, accuracy_ratio, accuracy_reason),
                "coverage": _score_detail(coverage, 40, coverage_ratio, coverage_reason),
                "structural_understanding": _score_detail(structural, 20, structural / 20, structural_reason),
            },
            "total": {
                "score": float(score["total_score"]),
                "max_score": 100,
                "rubric_level": _level(float(score["total_score"])),
                "reason": "RAG rubric의 claim, objective, relation 평가를 합산했습니다.",
            },
        },
        "qualitative": {
            "missing_concepts": missing,
            "incorrect_concepts": incorrect,
            "misconnected_concepts": misconnected,
            "review_suggestions": suggestions,
        },
    }


def _score_detail(
    score: float, maximum: int, ratio: float, reason: str
) -> dict[str, object]:
    return {
        "score": round(score, 2),
        "max_score": maximum,
        "rubric_level": _level(ratio * 4),
        "reason": reason,
    }


def _assessment_reason(
    title: str, details: list[str], fallback: str, ratio: float
) -> str:
    level = _level(ratio)
    if not details:
        return f"루브릭 단계: {level}/4\n- {fallback}"
    preview = details[:3]
    suffix = "\n- 그 외 평가 항목은 화면의 정성 피드백을 참고하세요." if len(details) > 3 else ""
    return "\n".join([f"루브릭 단계: {level}/4", f"- {fallback}", f"- {title}"] + [f"  · {item}" for item in preview]) + suffix


def _level(value: float) -> int:
    return max(0, min(4, int(value * 4)))


def mock_evaluation(transcript: str) -> EvaluationResult:
    return {
        "segments": [{"segment_id": "seg_01", "index": 1, "text": transcript}],
        "claims": [],
        "quantitative": {
            "concept_recall": 0.72,
            "concept_precision": 0.84,
            "concept_f1": 0.77,
            "scores": {
                "accuracy": {"score": 32, "max_score": 40, "rubric_level": 3, "reason": "핵심 개념을 대체로 정확하게 설명했습니다."},
                "coverage": {"score": 29, "max_score": 40, "rubric_level": 3, "reason": "주요 주제를 다루었지만 일부 개념이 누락되었습니다."},
                "structural_understanding": {"score": 14, "max_score": 20, "rubric_level": 3, "reason": "개념 간 관계를 대체로 일관되게 설명했습니다."}
            },
            "total": {"score": 75, "max_score": 100, "rubric_level": 3, "reason": "세 평가 영역을 종합한 Mock 결과입니다."}
        },
        "qualitative": {
            "missing_concepts": ["세부 근거와 예시"],
            "incorrect_concepts": [],
            "misconnected_concepts": [],
            "review_suggestions": ["핵심 개념 사이의 관계를 한 문장씩 설명해 보세요."]
        }
    }
