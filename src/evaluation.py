from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.evaluation_schemas import (
    ClaimAssessment,
    LectureRubric,
    TopLevelObjective,
    TopicAssessment,
)


JUDGMENT_VALUES = {
    "correct": 1.0,
    "mostly_correct": 0.8,
    "partial": 0.5,
    "incorrect": 0.0,
    "not_addressed": 0.0,
}
ESSENTIAL_COVERAGE_VALUES = {
    "correct": 1.0,
    "mostly_correct": 0.9,
    "partial": 0.7,
    "incorrect": 0.0,
    "not_addressed": 0.0,
}


def load_rubric(path: Path) -> LectureRubric:
    return LectureRubric.model_validate_json(path.read_text(encoding="utf-8"))


def select_objective_branch(
    rubric: LectureRubric,
    objective_id: str,
) -> TopLevelObjective:
    for objective in rubric.top_level_objectives:
        if objective.objective_id == objective_id:
            return objective
    raise ValueError(f"rubric에 없는 상위 학습목표입니다: {objective_id}")


def load_branch_evidence(
    rubric: LectureRubric,
    objective_id: str,
    processed_path: Path,
) -> dict[str, dict[str, Any]]:
    branch = select_objective_branch(rubric, objective_id)
    document = json.loads(processed_path.read_text(encoding="utf-8"))
    if document["lecture_id"] != rubric.lecture_id:
        raise ValueError("processed 파일과 rubric의 lecture_id가 다릅니다.")
    chunks = {chunk["chunk_id"]: chunk for chunk in document["chunks"]}
    evidence_refs = [
        evidence
        for sub in branch.sub_objectives
        for claim in sub.claims
        for evidence in claim.evidence
    ]
    required_ids = {evidence.chunk_id for evidence in evidence_refs}
    missing = required_ids - set(chunks)
    if missing:
        raise ValueError(f"processed 파일에 없는 evidence chunk입니다: {sorted(missing)}")
    result: dict[str, dict[str, Any]] = {}
    for chunk_id in sorted(required_ids):
        chunk = chunks[chunk_id]
        requested_unit_ids = {
            evidence.unit_id
            for evidence in evidence_refs
            if evidence.chunk_id == chunk_id and evidence.unit_id is not None
        }
        if not requested_unit_ids:
            result[chunk_id] = chunk
            continue
        unit_lookup = {
            unit["unit_id"]: unit for unit in chunk.get("evidence_units", [])
        }
        missing_units = requested_unit_ids - set(unit_lookup)
        if missing_units:
            raise ValueError(
                f"processed 파일에 없는 evidence unit입니다: {sorted(missing_units)}"
            )
        result[chunk_id] = {
            "chunk_id": chunk["chunk_id"],
            "page": chunk["page"],
            "topic": chunk["topic"],
            "evidence_units": [
                unit_lookup[unit_id] for unit_id in sorted(requested_unit_ids)
            ],
        }
    return result


def load_branch_terminology(
    rubric: LectureRubric,
    objective_id: str,
    processed_path: Path,
) -> list[dict[str, Any]]:
    branch = select_objective_branch(rubric, objective_id)
    document = json.loads(processed_path.read_text(encoding="utf-8"))
    required_term_ids = {
        term_id
        for sub in branch.sub_objectives
        for claim in sub.claims
        for term_id in claim.term_ids
    }
    terminology = {
        term["term_id"]: term for term in document.get("terminology", [])
    }
    missing = required_term_ids - set(terminology)
    if missing:
        raise ValueError(f"processed 파일에 없는 terminology입니다: {sorted(missing)}")
    return [terminology[term_id] for term_id in sorted(required_term_ids)]


def validate_assessment(
    rubric: LectureRubric,
    assessment: TopicAssessment,
    *,
    valid_segments: dict[str, str] | None = None,
    transcript: str | None = None,
) -> None:
    if assessment.lecture_id != rubric.lecture_id:
        raise ValueError("assessment와 rubric의 lecture_id가 다릅니다.")
    branch = select_objective_branch(rubric, assessment.objective_id)
    claim_lookup = {
        claim.claim_id: claim
        for sub in branch.sub_objectives
        for claim in sub.claims
    }
    ids = [item.claim_id for item in assessment.claim_assessments]
    problems = {
        "missing": sorted(set(claim_lookup) - set(ids)),
        "unknown": sorted(set(ids) - set(claim_lookup)),
        "duplicates": sorted({item_id for item_id in ids if ids.count(item_id) > 1}),
    }
    problems = {key: values for key, values in problems.items() if values}
    if problems:
        raise ValueError(f"선택한 상위 목표의 Claim 판정이 완전하지 않습니다: {problems}")

    assessment_by_id = {item.claim_id: item for item in assessment.claim_assessments}
    for claim_id, claim in claim_lookup.items():
        item = assessment_by_id[claim_id]
        allowed_chunk_ids = {evidence.chunk_id for evidence in claim.evidence}
        unknown_chunks = (
            set(item.source_chunk_ids_used) - allowed_chunk_ids
        )
        if unknown_chunks:
            raise ValueError(
                f"{claim_id}가 연결되지 않은 source chunk를 사용했습니다: "
                f"{sorted(unknown_chunks)}"
            )
        if item.judgment != "not_addressed" and not item.source_chunk_ids_used:
            raise ValueError(f"{claim_id}: 판정에 사용한 source chunk가 필요합니다.")
        for span in item.evidence_spans:
            normalized_quote = " ".join(span.quote.split())
            if valid_segments is not None:
                segment_text = valid_segments.get(span.segment_id)
                if segment_text is None:
                    raise ValueError(
                        f"{claim_id}가 존재하지 않는 segment를 사용했습니다: "
                        f"{span.segment_id}"
                    )
                if normalized_quote not in " ".join(segment_text.split()):
                    raise ValueError(
                        f"{claim_id}: quote가 지정된 {span.segment_id}에 없습니다."
                    )
            elif transcript is not None:
                if normalized_quote not in " ".join(transcript.split()):
                    raise ValueError(
                        f"{claim_id}: quote가 실제 발화문에 없습니다."
                    )


def _weighted_ratio(
    claims: list[Any],
    assessments: dict[str, ClaimAssessment],
) -> float:
    denominator = sum(claim.weight for claim in claims)
    return sum(
        claim.weight * JUDGMENT_VALUES[assessments[claim.claim_id].judgment]
        for claim in claims
    ) / denominator


def score_topic_assessment(
    rubric: LectureRubric,
    assessment: TopicAssessment,
) -> dict[str, Any]:
    validate_assessment(rubric, assessment)
    branch = select_objective_branch(rubric, assessment.objective_id)
    assessment_by_id = {
        item.claim_id: item for item in assessment.claim_assessments
    }
    claims = [claim for sub in branch.sub_objectives for claim in sub.claims]
    essential_claims = [claim for claim in claims if claim.role == "essential"]
    supporting_claims = [claim for claim in claims if claim.role == "supporting"]
    policy = rubric.assessment.score_policy

    essential_score = policy.essential_points * _weighted_ratio(
        essential_claims, assessment_by_id
    )
    essential_weight_total = sum(claim.weight for claim in essential_claims)
    essential_breakdown = [
        {
            "claim_id": claim.claim_id,
            "judgment": assessment_by_id[claim.claim_id].judgment,
            "value": JUDGMENT_VALUES[
                assessment_by_id[claim.claim_id].judgment
            ],
            "weight": claim.weight,
            "point_contribution": round(
                policy.essential_points
                * claim.weight
                * JUDGMENT_VALUES[assessment_by_id[claim.claim_id].judgment]
                / essential_weight_total,
                2,
            ),
        }
        for claim in essential_claims
    ]

    supporting_items = [
        {
            "claim_id": claim.claim_id,
            "judgment": assessment_by_id[claim.claim_id].judgment,
            "value": JUDGMENT_VALUES[assessment_by_id[claim.claim_id].judgment],
        }
        for claim in supporting_claims
    ]
    ranked_supporting = sorted(
        supporting_items,
        key=lambda item: item["value"],
        reverse=True,
    )
    selected_supporting = ranked_supporting[: branch.supporting_claim_slots]
    top_n_ratio = sum(item["value"] for item in selected_supporting) / (
        branch.supporting_claim_slots
    )
    addressed_supporting = [
        item for item in supporting_items if item["judgment"] != "not_addressed"
    ]
    addressed_accuracy = (
        sum(item["value"] for item in addressed_supporting)
        / len(addressed_supporting)
        if addressed_supporting
        else 0.0
    )
    supporting_ratio = min(top_n_ratio, addressed_accuracy)
    supporting_score = policy.supporting_points * supporting_ratio

    sub_coverage: list[dict[str, Any]] = []
    for sub in branch.sub_objectives:
        essential = next(claim for claim in sub.claims if claim.role == "essential")
        essential_judgment = assessment_by_id[essential.claim_id].judgment
        base_ratio = ESSENTIAL_COVERAGE_VALUES[essential_judgment]
        if base_ratio == 0.0:
            supporting_judgments = [
                assessment_by_id[claim.claim_id].judgment
                for claim in sub.claims
                if claim.role == "supporting"
            ]
            if any(JUDGMENT_VALUES[item] >= 0.5 for item in supporting_judgments):
                base_ratio = 0.5
        sub_assessments = [assessment_by_id[claim.claim_id] for claim in sub.claims]
        coverage_cap = 1.0
        cap_reasons: list[str] = []
        if any(item.judgment == "incorrect" for item in sub_assessments):
            coverage_cap = min(coverage_cap, 0.7)
            cap_reasons.append("하위 목표 안에 incorrect Claim이 있음")
        if any(item.conflict_status == "unresolved" for item in sub_assessments):
            coverage_cap = min(coverage_cap, 0.85)
            cap_reasons.append("하위 목표 안에 해결되지 않은 충돌이 있음")
        ratio = min(base_ratio, coverage_cap)
        sub_coverage.append(
            {
                "sub_objective_id": sub.sub_objective_id,
                "ratio": ratio,
                "base_ratio": base_ratio,
                "coverage_cap": coverage_cap,
                "cap_reasons": cap_reasons,
            }
        )
    coverage_ratio = sum(item["ratio"] for item in sub_coverage) / len(sub_coverage)
    coverage_score = policy.coverage_points * coverage_ratio

    result = {
        "schema_version": rubric.schema_version,
        "lecture_id": rubric.lecture_id,
        "objective_id": branch.objective_id,
        "essential_score": round(essential_score, 2),
        "supporting_score": round(supporting_score, 2),
        "coverage_score": round(coverage_score, 2),
        "total_score": round(
            essential_score + supporting_score + coverage_score, 2
        ),
        "sub_objective_coverage": sub_coverage,
        "score_breakdown": {
            "essential_claims": essential_breakdown,
            "supporting": {
                "slots": branch.supporting_claim_slots,
                "selected_top_n": selected_supporting,
                "not_selected": ranked_supporting[branch.supporting_claim_slots :],
                "top_n_ratio": round(top_n_ratio, 4),
                "addressed_accuracy": round(addressed_accuracy, 4),
                "applied_ratio": round(supporting_ratio, 4),
            },
            "sub_objectives": sub_coverage,
        },
    }
    return result
