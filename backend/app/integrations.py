from __future__ import annotations

from typing import TypedDict

from openai import OpenAI

from src.config import Settings
from src.evaluation import (
    load_branch_evidence,
    load_branch_terminology,
    load_rubric,
    score_topic_assessment,
    select_objective_branch,
)
from src.evaluation_api import request_validated_evaluation_assessment
from src.evaluation_prompt import EVALUATION_SYSTEM_PROMPT, build_evaluation_prompt
from src.transcript import segment_transcript


class EvaluationResult(TypedDict):
    segments: list[dict[str, object]]
    claims: list[dict[str, object]]
    quantitative: dict[str, object]
    qualitative: dict[str, list[str]]


def evaluate_selected_topic(
    *,
    transcript: str,
    lecture_id: str,
    objective_id: str,
    settings: Settings,
    client: OpenAI,
) -> EvaluationResult:
    evaluation_dir = settings.project_root / "data" / "evaluation"
    rubric = load_rubric(evaluation_dir / "rubrics" / f"{lecture_id}.json")
    branch = select_objective_branch(rubric, objective_id)
    evidence_chunks = load_branch_evidence(
        rubric,
        objective_id,
        settings.processed_dir / f"{lecture_id}.json",
    )
    terminology = load_branch_terminology(
        rubric,
        objective_id,
        settings.processed_dir / f"{lecture_id}.json",
    )
    segments = segment_transcript(transcript)
    prompt = build_evaluation_prompt(
        rubric=rubric,
        branch=branch,
        transcript=transcript,
        segments=segments,
        evidence_chunks=evidence_chunks,
        terminology=terminology,
    )
    assessment = request_validated_evaluation_assessment(
        client=client,
        model=settings.llm_model,
        input_messages=[
            {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_retries=settings.max_retries,
        rubric=rubric,
        valid_segments={segment.segment_id: segment.text for segment in segments},
        transcript=transcript,
    )
    score = score_topic_assessment(rubric, assessment)
    return _to_review_result(score, assessment, branch, segments)


def _to_review_result(score, assessment, branch, segments) -> EvaluationResult:
    claim_lookup = {
        claim.claim_id: (claim, sub)
        for sub in branch.sub_objectives
        for claim in sub.claims
    }
    assessment_by_id = {item.claim_id: item for item in assessment.claim_assessments}
    claims = []
    for item in assessment.claim_assessments:
        claim = claim_lookup[item.claim_id][0]
        source_ids = item.source_chunk_ids_used or [
            evidence.chunk_id for evidence in claim.evidence
        ]
        page_by_chunk = {evidence.chunk_id: evidence.page for evidence in claim.evidence}
        claims.append(
            {
                "claim_id": item.claim_id,
                "judgment": item.judgment,
                "source_chunk_ids_used": source_ids,
                "source_chunks": [
                    {"source_chunk_id": chunk_id, "page": page_by_chunk[chunk_id]}
                    for chunk_id in source_ids
                    if chunk_id in page_by_chunk
                ],
                "conflict_status": item.conflict_status,
                "evidence_spans": [span.model_dump() for span in item.evidence_spans],
                "rationale": item.rationale,
            }
        )
    strengths = [
        claim_lookup[item.claim_id][0].text
        for item in assessment.claim_assessments
        if item.judgment in {"correct", "mostly_correct"}
    ]
    missing = [
        claim_lookup[item.claim_id][0].text
        for item in assessment.claim_assessments
        if item.judgment == "not_addressed"
    ]
    incorrect = [
        f"{claim_lookup[item.claim_id][0].text} — {item.rationale}"
        for item in assessment.claim_assessments
        if item.judgment == "incorrect"
    ]
    suggestions = []
    for sub in branch.sub_objectives:
        essential = next(claim for claim in sub.claims if claim.role == "essential")
        if assessment_by_id[essential.claim_id].judgment in {
            "partial", "incorrect", "not_addressed"
        }:
            suggestions.append(f"'{sub.title}'의 핵심 내용을 다시 설명해 보세요.")

    return {
        "segments": [segment.model_dump() for segment in segments],
        "claims": claims,
        "quantitative": {
            "scores": {
                "essential": _score_detail(float(score["essential_score"]), 60, "하위 목표별 essential Claim의 정확도를 반영했습니다."),
                "supporting": _score_detail(float(score["supporting_score"]), 20, f"가장 잘 설명한 supporting Claim {branch.supporting_claim_slots}개와 실제 언급한 supporting 내용의 정확도를 함께 반영했습니다."),
                "coverage": _score_detail(float(score["coverage_score"]), 20, "선택 주제 아래 하위 학습목표의 충족 범위를 반영했습니다."),
            },
            "total": _score_detail(float(score["total_score"]), 100, "Rubric의 60+20+20 규칙으로 계산했습니다."),
            "sub_objective_coverage": score["sub_objective_coverage"],
        },
        "qualitative": {
            "strengths": strengths,
            "missing_claims": missing,
            "incorrect_claims": incorrect,
            "review_suggestions": suggestions,
        },
    }


def _score_detail(score: float, maximum: int, reason: str) -> dict[str, object]:
    ratio = score / maximum if maximum else 0.0
    return {
        "score": round(score, 2),
        "max_score": maximum,
        "rubric_level": max(0, min(4, round(ratio * 4))),
        "reason": reason,
    }


def mock_evaluation(transcript: str) -> EvaluationResult:
    return {
        "segments": [{"segment_id": "seg_01", "index": 1, "text": transcript}],
        "claims": [],
        "quantitative": {
            "scores": {
                "essential": _score_detail(48, 60, "핵심 Claim을 대체로 정확하게 설명했습니다."),
                "supporting": _score_detail(14, 20, "보조 설명 두 가지를 연결했습니다."),
                "coverage": _score_detail(15, 20, "하위 목표 대부분을 다뤘습니다."),
            },
            "total": _score_detail(77, 100, "Rubric Mock 결과입니다."),
            "sub_objective_coverage": [],
        },
        "qualitative": {
            "strengths": ["핵심 개념을 정확하게 설명했습니다."],
            "missing_claims": ["일부 보조 설명"],
            "incorrect_claims": [],
            "review_suggestions": ["빠진 하위 목표를 한 문장으로 보완해 보세요."],
        },
    }
