from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.evaluation_schemas import AssessmentProfile, EvaluationAssessment, LectureRubric


CLAIM_VALUES = {
    "correct": 1.0,
    "mostly_correct": 0.75,
    "partial": 0.5,
    "incorrect": 0.0,
}
FULFILLMENT_VALUES = {
    "complete": 1.0,
    "substantial": 0.8,
    "partial": 0.5,
    "name_only": 0.2,
    "absent": 0.0,
}
RELATION_VALUES = {
    "explicit_correct": 1.0,
    "implicit_correct": 0.5,
    "co_occurrence_only": 0.0,
    "incorrect": 0.0,
    "absent": 0.0,
}


def load_rubric(path: Path) -> LectureRubric:
    return LectureRubric.model_validate_json(path.read_text(encoding="utf-8"))


def load_profile(path: Path) -> AssessmentProfile:
    return AssessmentProfile.model_validate_json(path.read_text(encoding="utf-8"))


def validate_profile_against_rubric(
    profile: AssessmentProfile,
    rubric: LectureRubric,
) -> None:
    if profile.lecture_id != rubric.lecture_id:
        raise ValueError(
            f"profile과 rubric의 lecture_id 불일치: "
            f"{profile.lecture_id} != {rubric.lecture_id}"
        )
    objective_ids = {item.objective_id for item in rubric.learning_objectives}
    relation_ids = {item.relation_id for item in rubric.relations}
    chain_ids = {item.chain_id for item in rubric.relation_chains}
    unknown_objectives = {
        item_id
        for group in profile.objective_groups
        for item_id in group.candidate_objective_ids
        if item_id not in objective_ids
    }
    unknown_relations = {
        item_id
        for group in profile.relation_groups
        for item_id in group.candidate_relation_ids
        if item_id not in relation_ids
    }
    unknown_chains = {
        item_id
        for group in profile.chain_groups
        for item_id in group.candidate_chain_ids
        if item_id not in chain_ids
    }
    unknown = {
        key: sorted(value)
        for key, value in {
            "objectives": unknown_objectives,
            "relations": unknown_relations,
            "chains": unknown_chains,
        }.items()
        if value
    }
    if unknown:
        raise ValueError(f"profile이 rubric에 없는 ID를 참조합니다: {unknown}")


def validate_assessment_against_rubric(
    assessment: EvaluationAssessment,
    rubric: LectureRubric,
) -> None:
    if assessment.lecture_id != rubric.lecture_id:
        raise ValueError(
            f"assessment와 rubric의 lecture_id 불일치: "
            f"{assessment.lecture_id} != {rubric.lecture_id}"
        )

    expected = {
        "claims": {
            claim.claim_id
            for objective in rubric.learning_objectives
            for claim in objective.reference_claims
        },
        "objectives": {
            objective.objective_id for objective in rubric.learning_objectives
        },
        "relations": {relation.relation_id for relation in rubric.relations},
        "chains": {chain.chain_id for chain in rubric.relation_chains},
    }
    actual_items = {
        "claims": (assessment.claim_assessments, "claim_id"),
        "objectives": (assessment.objective_assessments, "objective_id"),
        "relations": (assessment.relation_assessments, "relation_id"),
        "chains": (assessment.chain_assessments, "chain_id"),
    }
    problems: dict[str, dict[str, list[str]]] = {}
    for label, (items, id_field) in actual_items.items():
        ids = [getattr(item, id_field) for item in items]
        duplicate_ids = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        actual = set(ids)
        issue = {
            "missing": sorted(expected[label] - actual),
            "unknown": sorted(actual - expected[label]),
            "duplicates": duplicate_ids,
        }
        issue = {key: value for key, value in issue.items() if value}
        if issue:
            problems[label] = issue
    if problems:
        raise ValueError(f"평가 결과의 Rubric ID가 완전하지 않습니다: {problems}")


def _top_n_average(values: list[float], count: int) -> float:
    selected = sorted(values, reverse=True)[:count]
    selected.extend([0.0] * (count - len(selected)))
    return sum(selected) / count


def _unique_by_id(items: list[Any], field: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in items:
        item_id = getattr(item, field)
        if item_id in result:
            raise ValueError(f"중복된 평가 ID입니다: {item_id}")
        result[item_id] = item
    return result


def score_evaluation(
    rubric: LectureRubric,
    assessment: EvaluationAssessment,
    profile: AssessmentProfile | None = None,
) -> dict[str, Any]:
    if assessment.lecture_id != rubric.lecture_id:
        raise ValueError(
            f"lecture_id 불일치: {assessment.lecture_id} != {rubric.lecture_id}"
        )
    if profile is not None:
        validate_profile_against_rubric(profile, rubric)

    claim_lookup = {
        claim.claim_id: (claim, objective)
        for objective in rubric.learning_objectives
        for claim in objective.reference_claims
    }
    objective_lookup = {item.objective_id: item for item in rubric.learning_objectives}
    relation_lookup = {item.relation_id: item for item in rubric.relations}
    chain_lookup = {item.chain_id: item for item in rubric.relation_chains}

    claim_assessments = _unique_by_id(assessment.claim_assessments, "claim_id")
    objective_assessments = _unique_by_id(
        assessment.objective_assessments, "objective_id"
    )
    relation_assessments = _unique_by_id(
        assessment.relation_assessments, "relation_id"
    )
    chain_assessments = _unique_by_id(assessment.chain_assessments, "chain_id")

    unknown = {
        "claims": set(claim_assessments) - set(claim_lookup),
        "objectives": set(objective_assessments) - set(objective_lookup),
        "relations": set(relation_assessments) - set(relation_lookup),
        "chains": set(chain_assessments) - set(chain_lookup),
    }
    unknown = {key: sorted(value) for key, value in unknown.items() if value}
    if unknown:
        raise ValueError(f"rubric에 없는 평가 ID입니다: {unknown}")

    accuracy_numerator = 0.0
    accuracy_denominator = 0.0
    for claim_id, item in claim_assessments.items():
        if item.judgment == "not_addressed":
            continue
        claim, objective = claim_lookup[claim_id]
        weight = claim.weight * objective.importance
        accuracy_numerator += weight * CLAIM_VALUES[item.judgment]
        accuracy_denominator += weight
    accuracy_ratio = (
        accuracy_numerator / accuracy_denominator if accuracy_denominator else 0.0
    )

    if profile is None:
        coverage_numerator = 0.0
        coverage_denominator = 0.0
        for objective in rubric.learning_objectives:
            if not objective.required:
                continue
            item = objective_assessments.get(objective.objective_id)
            judgment = item.judgment if item else "absent"
            coverage_numerator += objective.importance * FULFILLMENT_VALUES[judgment]
            coverage_denominator += objective.importance
        coverage_ratio = (
            coverage_numerator / coverage_denominator if coverage_denominator else 0.0
        )
    else:
        coverage_ratio = sum(
            (group.weight / 100.0)
            * _top_n_average(
                [
                    FULFILLMENT_VALUES[
                        objective_assessments[item_id].judgment
                        if item_id in objective_assessments
                        else "absent"
                    ]
                    for item_id in group.candidate_objective_ids
                ],
                group.minimum_objectives,
            )
            for group in profile.objective_groups
        )

    if profile is None:
        relation_numerator = 0.0
        relation_denominator = 0.0
        for relation in rubric.relations:
            if not relation.required:
                continue
            item = relation_assessments.get(relation.relation_id)
            judgment = item.judgment if item else "absent"
            relation_numerator += relation.importance * RELATION_VALUES[judgment]
            relation_denominator += relation.importance
        relation_ratio = (
            relation_numerator / relation_denominator if relation_denominator else 0.0
        )
    else:
        relation_ratio = sum(
            (group.weight / 100.0)
            * _top_n_average(
                [
                    RELATION_VALUES[
                        relation_assessments[item_id].judgment
                        if item_id in relation_assessments
                        else "absent"
                    ]
                    for item_id in group.candidate_relation_ids
                ],
                group.minimum_relations,
            )
            for group in profile.relation_groups
        )

    if profile is None:
        chain_numerator = 0.0
        chain_denominator = 0.0
        for chain in rubric.relation_chains:
            if not chain.required:
                continue
            item = chain_assessments.get(chain.chain_id)
            chain_numerator += chain.importance * float(bool(item and item.matched))
            chain_denominator += chain.importance
        chain_ratio = chain_numerator / chain_denominator if chain_denominator else 0.0
    else:
        chain_ratio = sum(
            (group.weight / 100.0)
            * _top_n_average(
                [
                    float(
                        bool(
                            item_id in chain_assessments
                            and chain_assessments[item_id].matched
                        )
                    )
                    for item_id in group.candidate_chain_ids
                ],
                group.minimum_chains,
            )
            for group in profile.chain_groups
        )

    accuracy_score = 40.0 * accuracy_ratio
    coverage_score = 40.0 * coverage_ratio
    structural_score = 16.0 * relation_ratio + 4.0 * chain_ratio
    total_score = accuracy_score + coverage_score + structural_score

    return {
        "lecture_id": rubric.lecture_id,
        "profile_id": profile.profile_id if profile else None,
        "concept_accuracy": round(accuracy_score, 2),
        "core_fulfillment": round(coverage_score, 2),
        "structural_understanding": round(structural_score, 2),
        "total_score": round(total_score, 2),
        "ratios": {
            "accuracy": round(accuracy_ratio, 4),
            "coverage": round(coverage_ratio, 4),
            "relations": round(relation_ratio, 4),
            "chains": round(chain_ratio, 4),
        },
    }


def load_assessment(path: Path) -> EvaluationAssessment:
    return EvaluationAssessment.model_validate_json(path.read_text(encoding="utf-8"))


def dump_score(result: dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)
