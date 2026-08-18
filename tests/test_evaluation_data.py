from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation import (
    load_profile,
    load_rubric,
    score_evaluation,
    validate_assessment_against_rubric,
    validate_profile_against_rubric,
)
from src.evaluation_prompt import build_evaluation_prompt
from src.evaluation_schemas import EvaluationAssessment
from src.schemas import (
    EvidenceHit,
    SearchHit,
    SegmentSearchResult,
    TranscriptSearchResult,
    TranscriptSegment,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUBRIC_DIR = PROJECT_ROOT / "data" / "evaluation" / "rubrics"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROFILE_DIR = PROJECT_ROOT / "data" / "evaluation" / "profiles"


@pytest.mark.parametrize("rubric_path", sorted(RUBRIC_DIR.glob("*.json")))
def test_rubric_evidence_points_to_existing_chunks(rubric_path: Path) -> None:
    rubric = load_rubric(rubric_path)
    lecture = json.loads(
        (PROCESSED_DIR / f"{rubric.lecture_id}.json").read_text(encoding="utf-8")
    )
    chunks = {chunk["chunk_id"]: chunk for chunk in lecture["chunks"]}

    evidence_items = [
        evidence
        for objective in rubric.learning_objectives
        for claim in objective.reference_claims
        for evidence in claim.evidence
    ] + [evidence for relation in rubric.relations for evidence in relation.evidence]

    assert evidence_items
    for evidence in evidence_items:
        assert evidence.chunk_id in chunks
        assert chunks[evidence.chunk_id]["page"] == evidence.page


def test_calibration_cases_are_valid_jsonl_and_reference_known_ids() -> None:
    rubrics = {
        path.stem: load_rubric(path) for path in sorted(RUBRIC_DIR.glob("*.json"))
    }
    path = PROJECT_ROOT / "data" / "evaluation" / "calibration_cases.jsonl"
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    assert len(cases) >= 12
    assert len({case["case_id"] for case in cases}) == len(cases)
    for case in cases:
        rubric = rubrics[case["lecture_id"]]
        claim_ids = {
            claim.claim_id
            for objective in rubric.learning_objectives
            for claim in objective.reference_claims
        }
        objective_ids = {item.objective_id for item in rubric.learning_objectives}
        relation_ids = {item.relation_id for item in rubric.relations}
        signals = case["expected_signals"]
        for key in ("correct_claims", "incorrect_claims"):
            assert set(signals.get(key, [])) <= claim_ids
        for key in ("fulfilled_objectives", "name_only_objectives"):
            assert set(signals.get(key, [])) <= objective_ids
        assert set(signals.get("matched_relations", [])) <= relation_ids


def test_deterministic_scoring_uses_40_40_20_weights() -> None:
    rubric = load_rubric(RUBRIC_DIR / "crawling.json")
    assessment = EvaluationAssessment(
        lecture_id="crawling",
        claim_assessments=[
            {
                "claim_id": claim.claim_id,
                "judgment": "correct",
                "evidence_quote": "",
                "rationale": "",
            }
            for objective in rubric.learning_objectives
            for claim in objective.reference_claims
        ],
        objective_assessments=[
            {
                "objective_id": objective.objective_id,
                "judgment": "complete",
                "evidence_quote": "",
                "rationale": "",
            }
            for objective in rubric.learning_objectives
        ],
        relation_assessments=[
            {
                "relation_id": relation.relation_id,
                "judgment": "explicit_correct",
                "evidence_quote": "",
                "rationale": "",
            }
            for relation in rubric.relations
        ],
        chain_assessments=[
            {
                "chain_id": chain.chain_id,
                "matched": True,
                "evidence_quote": "",
                "rationale": "",
            }
            for chain in rubric.relation_chains
        ],
    )

    result = score_evaluation(rubric, assessment)
    assert result["concept_accuracy"] == 40.0
    assert result["core_fulfillment"] == 40.0
    assert result["structural_understanding"] == 20.0
    assert result["total_score"] == 100.0


def test_missing_assessments_score_zero() -> None:
    rubric = load_rubric(RUBRIC_DIR / "visualization.json")
    result = score_evaluation(
        rubric,
        EvaluationAssessment(
            lecture_id="visualization",
            claim_assessments=[],
            objective_assessments=[],
            relation_assessments=[],
            chain_assessments=[],
        ),
    )
    assert result["total_score"] == 0.0


def test_evaluation_prompt_contains_full_required_scan_and_transcript() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    prompt = build_evaluation_prompt(rubric, "p-value를 설명한 사용자 발화")
    for objective in rubric.learning_objectives:
        assert objective.objective_id in prompt
    for relation in rubric.relations:
        assert relation.relation_id in prompt
    assert "p-value를 설명한 사용자 발화" in prompt


@pytest.mark.parametrize("profile_path", sorted(PROFILE_DIR.glob("*.json")))
def test_profiles_reference_existing_rubric_items(profile_path: Path) -> None:
    profile = load_profile(profile_path)
    rubric = load_rubric(RUBRIC_DIR / f"{profile.lecture_id}.json")
    validate_profile_against_rubric(profile, rubric)
    assert sum(group.weight for group in profile.objective_groups) == 100
    assert sum(group.weight for group in profile.relation_groups) == 100
    assert sum(group.weight for group in profile.chain_groups) == 100


def test_full_assessment_scores_100_with_profile() -> None:
    rubric = load_rubric(RUBRIC_DIR / "visualization.json")
    profile = load_profile(PROFILE_DIR / "visualization_free_recall_3min.json")
    assessment = EvaluationAssessment(
        lecture_id="visualization",
        claim_assessments=[
            {
                "claim_id": claim.claim_id,
                "judgment": "correct",
                "evidence_quote": "",
                "rationale": "",
            }
            for objective in rubric.learning_objectives
            for claim in objective.reference_claims
        ],
        objective_assessments=[
            {
                "objective_id": objective.objective_id,
                "judgment": "complete",
                "evidence_quote": "",
                "rationale": "",
            }
            for objective in rubric.learning_objectives
        ],
        relation_assessments=[
            {
                "relation_id": relation.relation_id,
                "judgment": "explicit_correct",
                "evidence_quote": "",
                "rationale": "",
            }
            for relation in rubric.relations
        ],
        chain_assessments=[
            {
                "chain_id": chain.chain_id,
                "matched": True,
                "evidence_quote": "",
                "rationale": "",
            }
            for chain in rubric.relation_chains
        ],
    )
    result = score_evaluation(rubric, assessment, profile)
    assert result["total_score"] == 100.0
    assert result["profile_id"] == profile.profile_id


def test_three_minute_profile_requires_more_breadth_than_demo_profile() -> None:
    rubric = load_rubric(RUBRIC_DIR / "eda_fe.json")
    standard = load_profile(PROFILE_DIR / "eda_fe_free_recall_3min.json")
    demo = load_profile(PROFILE_DIR / "eda_fe_free_recall_demo_2min.json")
    assessment = EvaluationAssessment(
        lecture_id="eda_fe",
        claim_assessments=[],
        objective_assessments=[
            {
                "objective_id": objective_id,
                "judgment": "complete",
                "evidence_quote": "",
                "rationale": "",
            }
            for objective_id in (
                "eda.process_roles",
                "eda.missing_outliers",
                "eda.data_leakage",
            )
        ],
        relation_assessments=[],
        chain_assessments=[],
    )
    standard_result = score_evaluation(rubric, assessment, standard)
    demo_result = score_evaluation(rubric, assessment, demo)
    assert demo_result["core_fulfillment"] == 40.0
    assert standard_result["core_fulfillment"] < demo_result["core_fulfillment"]


def test_evaluation_prompt_includes_active_profile() -> None:
    rubric = load_rubric(RUBRIC_DIR / "crawling.json")
    profile = load_profile(PROFILE_DIR / "crawling_free_recall_demo_2min.json")
    prompt = build_evaluation_prompt(rubric, "크롤링을 설명합니다.", profile)
    assert "ACTIVE_ASSESSMENT_PROFILE" in prompt
    assert profile.profile_id in prompt


def test_evaluation_prompt_includes_segments_retrieved_evidence_and_exclusions() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    transcript = "p-value는 귀무가설이 참일 확률입니다."
    search_result = TranscriptSearchResult(
        lecture_id="basic_statistics",
        segment_results=[
            SegmentSearchResult(
                segment=TranscriptSegment(
                    segment_id="seg_01",
                    index=1,
                    text=transcript,
                ),
                hits=[
                    SearchHit(
                        rank=1,
                        chunk_id="basic_statistics_p16_01",
                        lecture_id="basic_statistics",
                        lecture_name="기초통계",
                        page=16,
                        topic="p-value의 흔한 오류",
                        content="p-value의 조건 방향을 바꾸어 해석하면 안 된다.",
                        distance=0.31,
                    )
                ],
            )
        ],
        evidence=[
            EvidenceHit(
                rank=1,
                chunk_id="basic_statistics_p16_01",
                lecture_id="basic_statistics",
                lecture_name="기초통계",
                page=16,
                topic="p-value의 흔한 오류",
                content="p-value의 조건 방향을 바꾸어 해석하면 안 된다.",
                best_distance=0.31,
                matched_segment_ids=["seg_01"],
            )
        ],
    )
    policy = json.loads(
        (PROJECT_ROOT / "data" / "evaluation" / "scoring_policy.json").read_text(
            encoding="utf-8"
        )
    )

    prompt = build_evaluation_prompt(
        rubric,
        transcript,
        search_result=search_result,
        scoring_policy=policy,
    )

    assert "TRANSCRIPT_SEGMENTS_AND_RETRIEVED_EVIDENCE" in prompt
    assert "basic_statistics_p16_01" in prompt
    assert '"best_distance": 0.31' in prompt
    assert "excluded_source_claims" in prompt
    assert rubric.excluded_source_claims[0] in prompt
    assert "JUDGMENT_POLICY" in prompt
    assert '"formula"' not in prompt
    assert '"total_score"' not in prompt


def test_evaluation_prompt_rejects_search_result_for_another_lecture() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    search_result = TranscriptSearchResult(
        lecture_id="crawling",
        segment_results=[
            SegmentSearchResult(
                segment=TranscriptSegment(
                    segment_id="seg_01",
                    index=1,
                    text="크롤링 설명",
                ),
                hits=[],
            )
        ],
        evidence=[],
    )

    with pytest.raises(ValueError, match="search_result"):
        build_evaluation_prompt(
            rubric,
            "기초통계 설명",
            search_result=search_result,
        )


def test_basic_statistics_gold_case_score_is_reproducible() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    profile = load_profile(
        PROFILE_DIR / "basic_statistics_free_recall_demo_2min.json"
    )
    assessment_path = (
        PROJECT_ROOT
        / "data"
        / "evaluation"
        / "gold"
        / "basic_statistics_script_01_assessment.json"
    )
    assessment = EvaluationAssessment.model_validate_json(
        assessment_path.read_text(encoding="utf-8")
    )
    result = score_evaluation(rubric, assessment, profile)
    assert result["concept_accuracy"] == 17.26
    assert result["core_fulfillment"] == 27.6
    assert result["structural_understanding"] == 16.0
    assert result["total_score"] == 60.86


def test_incomplete_assessment_is_rejected_before_scoring() -> None:
    rubric = load_rubric(RUBRIC_DIR / "basic_statistics.json")
    assessment = EvaluationAssessment(
        lecture_id="basic_statistics",
        claim_assessments=[],
        objective_assessments=[],
        relation_assessments=[],
        chain_assessments=[],
    )

    with pytest.raises(ValueError, match="missing"):
        validate_assessment_against_rubric(assessment, rubric)
