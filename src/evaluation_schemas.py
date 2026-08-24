from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


ClaimRole = Literal["essential", "supporting"]
ClaimCategory = Literal[
    "core_understanding",
    "explanation_application",
    "connection_comparison",
]
ClaimJudgment = Literal[
    "correct", "mostly_correct", "partial", "incorrect", "not_addressed"
]
SourceStatus = Literal["verified", "needs_review", "source_error"]
EvidenceRelation = Literal["supports", "contradicts", "corrects"]
ConflictStatus = Literal["none", "self_corrected", "unresolved"]


class EvaluationCriteria(StrictModel):
    required_elements: list[str] = Field(min_length=1)
    critical_errors: list[str] = Field(default_factory=list)


class EvidenceRef(StrictModel):
    page: int = Field(ge=1)
    chunk_id: str = Field(min_length=1)
    unit_id: str | None = None
    source_excerpt: str = Field(min_length=1)
    source_status: SourceStatus = "verified"
    review_note: str = ""


class Claim(StrictModel):
    claim_id: str = Field(min_length=1)
    role: ClaimRole
    category: ClaimCategory
    text: str = Field(min_length=1)
    term_ids: list[str] = Field(default_factory=list)
    weight: float = Field(default=1.0, gt=0)
    evidence: list[EvidenceRef] = Field(min_length=1)
    evaluation_criteria: EvaluationCriteria | None = None


class SubObjective(StrictModel):
    sub_objective_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    claims: list[Claim] = Field(min_length=2, max_length=4)

    @model_validator(mode="after")
    def validate_claim_roles(self) -> "SubObjective":
        essential_count = sum(claim.role == "essential" for claim in self.claims)
        if essential_count != 1:
            raise ValueError("하위 학습목표에는 essential Claim이 정확히 1개여야 합니다.")
        return self


class TopLevelObjective(StrictModel):
    objective_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    selection_description: str = Field(min_length=1)
    supporting_claim_slots: int = Field(ge=2, le=3)
    sub_objectives: list[SubObjective] = Field(min_length=3, max_length=4)

    @model_validator(mode="after")
    def validate_branch_size(self) -> "TopLevelObjective":
        claim_count = sum(len(item.claims) for item in self.sub_objectives)
        if not 7 <= claim_count <= 12:
            raise ValueError("상위 학습목표의 전체 Claim 수는 7~12개여야 합니다.")
        expected_slots = 2 if claim_count <= 8 else 3
        if self.supporting_claim_slots != expected_slots:
            raise ValueError(
                f"Claim {claim_count}개에는 supporting_claim_slots={expected_slots}가 필요합니다."
            )
        return self


class ScorePolicy(StrictModel):
    essential_points: int = 60
    supporting_points: int = 20
    coverage_points: int = 20

    @model_validator(mode="after")
    def validate_total(self) -> "ScorePolicy":
        if self.essential_points + self.supporting_points + self.coverage_points != 100:
            raise ValueError("점수 배점의 합은 100이어야 합니다.")
        return self


class AssessmentConfig(StrictModel):
    mode: Literal["selected_topic_recall"] = "selected_topic_recall"
    target_seconds: int = Field(default=120, ge=30)
    max_seconds: int = Field(default=120, ge=30)
    score_policy: ScorePolicy = Field(default_factory=ScorePolicy)

    @model_validator(mode="after")
    def validate_duration(self) -> "AssessmentConfig":
        if self.target_seconds > self.max_seconds:
            raise ValueError("target_seconds는 max_seconds보다 클 수 없습니다.")
        return self


class ExcludedSourceClaim(StrictModel):
    page: int = Field(ge=1)
    chunk_id: str = Field(min_length=1)
    source_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class LectureRubric(StrictModel):
    schema_version: Literal["2.0.0", "2.1.0", "2.2.0"]
    lecture_id: str = Field(min_length=1)
    lecture_name: str = Field(min_length=1)
    assessment: AssessmentConfig
    top_level_objectives: list[TopLevelObjective] = Field(min_length=3, max_length=4)
    excluded_source_claims: list[ExcludedSourceClaim] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "LectureRubric":
        objective_ids = [item.objective_id for item in self.top_level_objectives]
        sub_ids = [
            sub.sub_objective_id
            for objective in self.top_level_objectives
            for sub in objective.sub_objectives
        ]
        claim_ids = [
            claim.claim_id
            for objective in self.top_level_objectives
            for sub in objective.sub_objectives
            for claim in sub.claims
        ]
        for label, ids in (
            ("objective_id", objective_ids),
            ("sub_objective_id", sub_ids),
            ("claim_id", claim_ids),
        ):
            if len(ids) != len(set(ids)):
                raise ValueError(f"{label}가 중복되었습니다.")
        return self


class EvidenceSpan(StrictModel):
    segment_id: str = Field(min_length=1)
    quote: str = Field(
        min_length=1,
        description=(
            "지정한 segment에 실제로 존재하는 하나의 연속 구간을 글자 그대로 "
            "복사한 인용문. 요약·수정·생략부호 결합 금지."
        ),
    )
    relation: EvidenceRelation


class ClaimAssessment(StrictModel):
    claim_id: str = Field(min_length=1)
    judgment: ClaimJudgment
    source_chunk_ids_used: list[str] = Field(default_factory=list)
    conflict_status: ConflictStatus
    evidence_spans: list[EvidenceSpan] = Field(
        default_factory=list,
        max_length=4,
        description=(
            "Claim 판정에 필요한 최소 비중복 발화 근거. 같은 의미의 반복은 가장 "
            "명확한 하나만 남기고, 보완·충돌·정정 근거는 각각 보존한다."
        ),
    )
    rationale: str = Field(min_length=1)

    @field_validator("source_chunk_ids_used")
    @classmethod
    def unique_ids(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("참조 ID가 중복되었습니다.")
        return values

    @model_validator(mode="after")
    def validate_evidence_state(self) -> "ClaimAssessment":
        if self.judgment == "not_addressed":
            if self.evidence_spans:
                raise ValueError("not_addressed에는 발화 근거가 없어야 합니다.")
            if self.conflict_status != "none":
                raise ValueError("not_addressed의 conflict_status는 none이어야 합니다.")
            return self
        if not self.evidence_spans:
            raise ValueError("판정한 Claim에는 최소 한 개의 발화 근거가 필요합니다.")
        keys = [(span.segment_id, span.quote) for span in self.evidence_spans]
        if len(keys) != len(set(keys)):
            raise ValueError("같은 evidence span이 중복되었습니다.")
        relations = {span.relation for span in self.evidence_spans}
        if self.conflict_status == "self_corrected" and not {
            "contradicts", "corrects"
        }.issubset(relations):
            raise ValueError(
                "self_corrected에는 contradicts와 corrects 근거가 모두 필요합니다."
            )
        if self.conflict_status == "unresolved" and not {
            "supports", "contradicts"
        }.issubset(relations):
            raise ValueError(
                "unresolved에는 supports와 contradicts 근거가 모두 필요합니다."
            )
        return self


class TopicAssessment(StrictModel):
    lecture_id: str = Field(min_length=1)
    objective_id: str = Field(min_length=1)
    claim_assessments: list[ClaimAssessment] = Field(min_length=1)
