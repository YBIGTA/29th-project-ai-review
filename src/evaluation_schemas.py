from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EvidenceRef(StrictModel):
    page: int = Field(ge=1)
    chunk_id: str = Field(min_length=1)


class ReferenceClaim(StrictModel):
    claim_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    essential: bool = True
    weight: float = Field(gt=0)
    evidence: list[EvidenceRef] = Field(min_length=1)


class Misconception(StrictModel):
    misconception_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    correction: str = Field(min_length=1)
    severity: Literal["major", "minor"]


class LearningObjective(StrictModel):
    objective_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    importance: int = Field(ge=1, le=5)
    required: bool
    reference_claims: list[ReferenceClaim] = Field(min_length=2)
    misconceptions: list[Misconception] = Field(default_factory=list)

    @field_validator("reference_claims")
    @classmethod
    def unique_claim_ids(cls, values: list[ReferenceClaim]) -> list[ReferenceClaim]:
        ids = [value.claim_id for value in values]
        if len(ids) != len(set(ids)):
            raise ValueError("claim_id가 중복되었습니다.")
        return values


RelationType = Literal[
    "causes",
    "derived_from",
    "prerequisite",
    "sequence",
    "used_for",
    "part_of",
    "contrasts_with",
    "alternative_to",
    "condition_for",
    "solves",
    "supports",
]


class RelationRubric(StrictModel):
    relation_id: str = Field(min_length=1)
    source_objective_id: str = Field(min_length=1)
    target_objective_id: str = Field(min_length=1)
    relation_type: RelationType
    statement: str = Field(min_length=1)
    directional: bool
    importance: int = Field(ge=1, le=5)
    required: bool
    evidence: list[EvidenceRef] = Field(min_length=1)


class RelationChain(StrictModel):
    chain_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    relation_ids: list[str] = Field(min_length=2)
    importance: int = Field(ge=1, le=5)
    required: bool


class LectureRubric(StrictModel):
    schema_version: str = Field(min_length=1)
    lecture_id: str = Field(min_length=1)
    lecture_name: str = Field(min_length=1)
    evaluation_scope: str = Field(min_length=1)
    learning_objectives: list[LearningObjective] = Field(min_length=1)
    relations: list[RelationRubric] = Field(min_length=1)
    relation_chains: list[RelationChain] = Field(default_factory=list)
    excluded_source_claims: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_references(self) -> "LectureRubric":
        objective_ids = [item.objective_id for item in self.learning_objectives]
        if len(objective_ids) != len(set(objective_ids)):
            raise ValueError("objective_id가 중복되었습니다.")
        objective_id_set = set(objective_ids)

        relation_ids = [item.relation_id for item in self.relations]
        if len(relation_ids) != len(set(relation_ids)):
            raise ValueError("relation_id가 중복되었습니다.")
        relation_id_set = set(relation_ids)
        relation_by_id = {item.relation_id: item for item in self.relations}

        for relation in self.relations:
            if relation.source_objective_id not in objective_id_set:
                raise ValueError(
                    f"존재하지 않는 source objective: {relation.source_objective_id}"
                )
            if relation.target_objective_id not in objective_id_set:
                raise ValueError(
                    f"존재하지 않는 target objective: {relation.target_objective_id}"
                )
        for chain in self.relation_chains:
            missing = set(chain.relation_ids) - relation_id_set
            if missing:
                raise ValueError(f"chain에서 존재하지 않는 relation 참조: {missing}")
            for left_id, right_id in zip(chain.relation_ids, chain.relation_ids[1:]):
                left = relation_by_id[left_id]
                right = relation_by_id[right_id]
                left_nodes = {left.source_objective_id, left.target_objective_id}
                right_nodes = {right.source_objective_id, right.target_objective_id}
                if left_nodes.isdisjoint(right_nodes):
                    raise ValueError(
                        f"chain의 인접 relation이 연결되지 않았습니다: "
                        f"{left_id} -> {right_id}"
                    )
        return self


ClaimJudgment = Literal[
    "correct", "mostly_correct", "partial", "incorrect", "not_addressed"
]
FulfillmentJudgment = Literal[
    "complete", "substantial", "partial", "name_only", "absent"
]
RelationJudgment = Literal[
    "explicit_correct", "implicit_correct", "co_occurrence_only", "incorrect", "absent"
]


class ClaimAssessment(StrictModel):
    claim_id: str = Field(min_length=1)
    judgment: ClaimJudgment
    evidence_quote: str
    rationale: str
    matched_segment_ids: list[str] = Field(default_factory=list)
    source_chunk_ids_used: list[str] = Field(default_factory=list)


class ObjectiveAssessment(StrictModel):
    objective_id: str = Field(min_length=1)
    judgment: FulfillmentJudgment
    evidence_quote: str
    rationale: str


class RelationAssessment(StrictModel):
    relation_id: str = Field(min_length=1)
    judgment: RelationJudgment
    evidence_quote: str
    rationale: str


class ChainAssessment(StrictModel):
    chain_id: str = Field(min_length=1)
    matched: bool
    evidence_quote: str
    rationale: str


class EvaluationAssessment(StrictModel):
    lecture_id: str = Field(min_length=1)
    claim_assessments: list[ClaimAssessment]
    objective_assessments: list[ObjectiveAssessment]
    relation_assessments: list[RelationAssessment]
    chain_assessments: list[ChainAssessment]


class ObjectiveSelectionGroup(StrictModel):
    group_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    weight: int = Field(ge=1, le=100)
    minimum_objectives: int = Field(ge=1)
    candidate_objective_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_minimum(self) -> "ObjectiveSelectionGroup":
        if self.minimum_objectives > len(self.candidate_objective_ids):
            raise ValueError("minimum_objectives가 후보 수보다 큽니다.")
        if len(self.candidate_objective_ids) != len(set(self.candidate_objective_ids)):
            raise ValueError("candidate_objective_ids가 중복되었습니다.")
        return self


class RelationSelectionGroup(StrictModel):
    group_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    weight: int = Field(ge=1, le=100)
    minimum_relations: int = Field(ge=1)
    candidate_relation_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_minimum(self) -> "RelationSelectionGroup":
        if self.minimum_relations > len(self.candidate_relation_ids):
            raise ValueError("minimum_relations가 후보 수보다 큽니다.")
        if len(self.candidate_relation_ids) != len(set(self.candidate_relation_ids)):
            raise ValueError("candidate_relation_ids가 중복되었습니다.")
        return self


class ChainSelectionGroup(StrictModel):
    group_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    weight: int = Field(ge=1, le=100)
    minimum_chains: int = Field(ge=1)
    candidate_chain_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_minimum(self) -> "ChainSelectionGroup":
        if self.minimum_chains > len(self.candidate_chain_ids):
            raise ValueError("minimum_chains가 후보 수보다 큽니다.")
        if len(self.candidate_chain_ids) != len(set(self.candidate_chain_ids)):
            raise ValueError("candidate_chain_ids가 중복되었습니다.")
        return self


class AssessmentProfile(StrictModel):
    schema_version: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    lecture_id: str = Field(min_length=1)
    mode: Literal["free_recall"]
    target_seconds: int = Field(ge=30)
    max_seconds: int = Field(ge=30)
    description: str = Field(min_length=1)
    objective_groups: list[ObjectiveSelectionGroup] = Field(min_length=1)
    relation_groups: list[RelationSelectionGroup] = Field(min_length=1)
    chain_groups: list[ChainSelectionGroup] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_profile(self) -> "AssessmentProfile":
        if self.target_seconds > self.max_seconds:
            raise ValueError("target_seconds는 max_seconds보다 클 수 없습니다.")
        for label, groups in (
            ("objective_groups", self.objective_groups),
            ("relation_groups", self.relation_groups),
            ("chain_groups", self.chain_groups),
        ):
            ids = [group.group_id for group in groups]
            if len(ids) != len(set(ids)):
                raise ValueError(f"{label}의 group_id가 중복되었습니다.")
            if sum(group.weight for group in groups) != 100:
                raise ValueError(f"{label}의 weight 합은 100이어야 합니다.")
        return self
