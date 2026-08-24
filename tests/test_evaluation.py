from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation import (
    load_branch_evidence,
    load_branch_terminology,
    load_rubric,
    score_topic_assessment,
    select_objective_branch,
    validate_assessment,
)
from src.evaluation_schemas import EvidenceSpan, TopicAssessment
from src.evaluation_prompt import build_evaluation_prompt
from src.schemas import TranscriptSegment


ROOT = Path(__file__).resolve().parents[1]
RUBRIC_DIR = ROOT / "data" / "evaluation" / "rubrics"
PROCESSED_DIR = ROOT / "data" / "processed"


@pytest.mark.parametrize("rubric_path", sorted(RUBRIC_DIR.glob("*.json")))
def test_rubrics_reference_verified_chunks(
    rubric_path: Path,
) -> None:
    rubric = load_rubric(rubric_path)
    processed = json.loads(
        (PROCESSED_DIR / f"{rubric.lecture_id}.json").read_text(encoding="utf-8")
    )
    chunks = {chunk["chunk_id"]: chunk for chunk in processed["chunks"]}
    for objective in rubric.top_level_objectives:
        assert 3 <= len(objective.sub_objectives) <= 4
        claim_count = sum(len(sub.claims) for sub in objective.sub_objectives)
        assert 7 <= claim_count <= 12
        for sub in objective.sub_objectives:
            assert sum(claim.role == "essential" for claim in sub.claims) == 1
            for claim in sub.claims:
                if rubric.schema_version == "2.2.0":
                    assert claim.evaluation_criteria is not None
                    assert claim.evaluation_criteria.required_elements
                for evidence in claim.evidence:
                    assert evidence.chunk_id in chunks
                    assert chunks[evidence.chunk_id]["page"] == evidence.page
                    if processed.get("schema_version") == "2.1.0":
                        assert evidence.unit_id
                        unit = next(
                            item
                            for item in chunks[evidence.chunk_id]["evidence_units"]
                            if item["unit_id"] == evidence.unit_id
                        )
                        assert unit["source_excerpt"] == evidence.source_excerpt
                        assert unit["source_status"] == "verified"
                    else:
                        assert chunks[evidence.chunk_id]["content"] == evidence.source_excerpt


def make_assessment(
    lecture_id: str,
    objective_id: str,
    branch,
    default: str = "correct",
) -> TopicAssessment:
    return TopicAssessment(
        lecture_id=lecture_id,
        objective_id=objective_id,
        claim_assessments=[
            {
                "claim_id": claim.claim_id,
                "judgment": default,
                "source_chunk_ids_used": (
                    [claim.evidence[0].chunk_id]
                    if default != "not_addressed"
                    else []
                ),
                "conflict_status": "none",
                "evidence_spans": (
                    [
                        {
                            "segment_id": "seg_01",
                            "quote": "사용자 발화의 근거 문장",
                            "relation": "supports",
                        }
                    ]
                    if default != "not_addressed"
                    else []
                ),
                "rationale": "테스트 판정",
            }
            for sub in branch.sub_objectives
            for claim in sub.claims
        ],
    )


def test_basic_statistics_selected_branch_full_score_is_100() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.hypothesis_uncertainty"
    branch = select_objective_branch(rubric, objective_id)
    assessment = make_assessment(rubric.lecture_id, objective_id, branch)

    result = score_topic_assessment(rubric, assessment)

    assert result["essential_score"] == 60.0
    assert result["supporting_score"] == 20.0
    assert result["coverage_score"] == 20.0
    assert result["total_score"] == 100.0


def test_supporting_claim_can_give_half_coverage_when_essential_is_omitted() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.hypothesis_uncertainty"
    branch = select_objective_branch(rubric, objective_id)
    assessment = make_assessment(
        rubric.lecture_id, objective_id, branch, default="not_addressed"
    )
    first_supporting = next(
        claim
        for claim in branch.sub_objectives[0].claims
        if claim.role == "supporting"
    )
    item = next(
        item
        for item in assessment.claim_assessments
        if item.claim_id == first_supporting.claim_id
    )
    item.judgment = "partial"
    item.source_chunk_ids_used = [first_supporting.evidence[0].chunk_id]
    item.evidence_spans = [
        EvidenceSpan(**{
            "segment_id": "seg_02",
            "quote": "부분적으로 언급함",
            "relation": "supports",
        })
    ]

    result = score_topic_assessment(rubric, assessment)

    assert result["essential_score"] == 0.0
    assert result["supporting_score"] == pytest.approx(3.33, abs=0.01)
    assert result["coverage_score"] == 2.5
    assert result["total_score"] == pytest.approx(5.83, abs=0.01)


def test_incorrect_addressed_supporting_claim_is_not_discarded_by_top_n() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.probability_foundations"
    branch = select_objective_branch(rubric, objective_id)
    assessment = make_assessment(rubric.lecture_id, objective_id, branch)
    item = next(
        item
        for item in assessment.claim_assessments
        if item.claim_id == "stats.correlation_not_causation"
    )
    item.judgment = "incorrect"
    item.evidence_spans = [
        EvidenceSpan(**{
            "segment_id": "seg_01",
            "quote": "상관관계가 높으면 인과관계입니다.",
            "relation": "contradicts",
        })
    ]

    result = score_topic_assessment(rubric, assessment)

    assert result["essential_score"] == 60.0
    assert result["supporting_score"] == 16.0
    assert result["coverage_score"] == 18.5
    assert result["total_score"] == 94.5
    assert result["score_breakdown"]["supporting"]["top_n_ratio"] == 1.0
    assert result["score_breakdown"]["supporting"]["addressed_accuracy"] == 0.8
    correlation = next(
        item
        for item in result["sub_objective_coverage"]
        if item["sub_objective_id"] == "stats.probability.correlation"
    )
    assert correlation["base_ratio"] == 1.0
    assert correlation["coverage_cap"] == 0.7
    assert correlation["ratio"] == 0.7


def test_unresolved_conflict_caps_coverage_and_keeps_both_quotes() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.probability_foundations"
    branch = select_objective_branch(rubric, objective_id)
    assessment = make_assessment(rubric.lecture_id, objective_id, branch)
    item = next(
        item
        for item in assessment.claim_assessments
        if item.claim_id == "stats.expectation_variance"
    )
    item.judgment = "partial"
    item.conflict_status = "unresolved"
    item.evidence_spans = [
        EvidenceSpan(**{
            "segment_id": "seg_01",
            "quote": "분산이 작을수록 평균 주변에 모입니다.",
            "relation": "supports",
        }),
        EvidenceSpan(**{
            "segment_id": "seg_02",
            "quote": "분산이 클수록 안정적입니다.",
            "relation": "contradicts",
        }),
    ]

    result = score_topic_assessment(rubric, assessment)

    random_variable_sub = next(
        value
        for value in result["sub_objective_coverage"]
        if value["sub_objective_id"] == "stats.probability.random_variable"
    )
    assert random_variable_sub["coverage_cap"] == 0.85
    assert random_variable_sub["ratio"] == 0.85
    assert len(item.evidence_spans) == 2


def test_assessment_must_cover_exactly_the_selected_branch() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.probability_foundations"
    branch = select_objective_branch(rubric, objective_id)
    assessment = make_assessment(rubric.lecture_id, objective_id, branch)
    assessment.claim_assessments.pop()

    with pytest.raises(ValueError, match="완전하지 않습니다"):
        validate_assessment(rubric, assessment)


def test_assessment_cannot_claim_unlinked_source_chunk() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.probability_foundations"
    branch = select_objective_branch(rubric, objective_id)
    assessment = make_assessment(rubric.lecture_id, objective_id, branch)
    assessment.claim_assessments[0].source_chunk_ids_used = [
        "basic_statistics_p41_01"
    ]

    with pytest.raises(ValueError, match="연결되지 않은 source chunk"):
        validate_assessment(rubric, assessment)


def test_each_quote_must_exist_in_its_declared_segment() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.probability_foundations"
    branch = select_objective_branch(rubric, objective_id)
    assessment = make_assessment(rubric.lecture_id, objective_id, branch)

    with pytest.raises(ValueError, match="지정된 seg_01에 없습니다"):
        validate_assessment(
            rubric,
            assessment,
            valid_segments={"seg_01": "실제 segment의 다른 문장"},
        )


def test_direct_evidence_loading_only_returns_selected_branch_chunks() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.hypothesis_uncertainty"
    branch = select_objective_branch(rubric, objective_id)
    expected_ids = {
        evidence.chunk_id
        for sub in branch.sub_objectives
        for claim in sub.claims
        for evidence in claim.evidence
    }

    chunks = load_branch_evidence(
        rubric,
        objective_id,
        PROCESSED_DIR / "basic_statistics.json",
    )

    assert set(chunks) == expected_ids
    assert "basic_statistics_p4_01" not in chunks
    assert all("raw_text" not in chunk for chunk in chunks.values())
    assert all("source_issues" not in chunk for chunk in chunks.values())
    assert all(chunk["evidence_units"] for chunk in chunks.values())


def test_basic_statistics_branch_loads_only_relevant_bilingual_terms() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    terms = load_branch_terminology(
        rubric,
        "stats.hypothesis_uncertainty",
        PROCESSED_DIR / "basic_statistics.json",
    )
    by_id = {term["term_id"]: term for term in terms}

    assert by_id["p_value"]["canonical_ko"] == "p-value"
    assert "p값" in by_id["p_value"]["accepted_aliases"]
    assert by_id["type_i_error"]["canonical_en"] == "type I error"
    assert "false positive" in by_id["type_i_error"]["accepted_aliases"]
    assert by_id["p_value"]["not_equivalent_to"] == ["null_probability"]
    assert "random_variable" not in by_id


def test_prompt_contains_atomic_evidence_and_bilingual_terms_only() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    objective_id = "stats.hypothesis_uncertainty"
    branch = select_objective_branch(rubric, objective_id)
    processed_path = PROCESSED_DIR / "basic_statistics.json"
    evidence = load_branch_evidence(rubric, objective_id, processed_path)
    terminology = load_branch_terminology(rubric, objective_id, processed_path)

    prompt = build_evaluation_prompt(
        rubric=rubric,
        branch=branch,
        transcript="Type I error는 false positive입니다.",
        segments=[TranscriptSegment(segment_id="seg_01", index=1, text="Type I error는 false positive입니다.")],
        evidence_chunks=evidence,
        terminology=terminology,
    )

    assert '"canonical_en": "type I error"' in prompt
    assert '"unit_id": "basic_statistics_p11_u01"' in prompt
    assert '"raw_text"' not in prompt
    assert '"source_issues"' not in prompt
    assert "basic_statistics_p4_u01" not in prompt


def test_bilingual_gold_cases_reference_selected_claims() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    cases = json.loads(
        (
            ROOT
            / "data/evaluation/gold/basic_statistics_bilingual_cases.json"
        ).read_text(encoding="utf-8")
    )["cases"]
    branches = {
        objective.objective_id: {
            claim.claim_id
            for sub in objective.sub_objectives
            for claim in sub.claims
        }
        for objective in rubric.top_level_objectives
    }

    assert {case["expected_judgment"] for case in cases} == {"correct", "incorrect"}
    assert all(
        case["claim_id"] in branches[case["objective_id"]]
        for case in cases
    )


def test_basic_statistics_gold_example_reproduces_expected_score() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    assessment = TopicAssessment.model_validate_json(
        (
            ROOT
            / "data/evaluation/gold/basic_statistics_hypothesis_assessment.json"
        ).read_text(encoding="utf-8")
    )
    expected = json.loads(
        (
            ROOT / "data/evaluation/gold/basic_statistics_hypothesis_score.json"
        ).read_text(encoding="utf-8")
    )

    actual = score_topic_assessment(rubric, assessment)

    for key in (
        "essential_score",
        "supporting_score",
        "coverage_score",
        "total_score",
    ):
        assert actual[key] == expected[key]
