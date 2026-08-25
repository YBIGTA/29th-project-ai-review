from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScoreDetail(BaseModel):
    score: float = Field(ge=0)
    max_score: int = Field(gt=0)
    rubric_level: int = Field(ge=0, le=4)
    reason: str


class QuantitativeEvaluation(BaseModel):
    scores: dict[str, ScoreDetail]
    total: ScoreDetail
    sub_objective_coverage: list[dict[str, Any]]


class QualitativeEvaluation(BaseModel):
    strengths: list[str]
    missing_claims: list[str]
    incorrect_claims: list[str]
    review_suggestions: list[str]


class ReviewSegment(BaseModel):
    segment_id: str
    index: int
    text: str


class SourceChunkReference(BaseModel):
    source_chunk_id: str
    page: int


class ClaimEvaluation(BaseModel):
    claim_id: str
    claim_text: str = ""
    judgment: str
    source_chunk_ids_used: list[str]
    source_chunks: list[SourceChunkReference]
    conflict_status: str
    evidence_spans: list[dict[str, str]]
    rationale: str


class ReviewSubmitRequest(BaseModel):
    job_id: str | None = None
    session_id: str
    topic: str
    lecture_id: str
    objective_id: str
    transcript_raw: str
    transcript_corrected: str
    term_db_used: dict[str, list[str]]


class ReviewSubmitResponse(BaseModel):
    review_id: str
    session_id: str
    lecture_id: str
    objective_id: str
    score: float = Field(ge=0, le=100)
    pass_status: str
    transcript: str
    corrected_transcript: str
    segments: list[ReviewSegment]
    claims: list[ClaimEvaluation]
    quantitative: QuantitativeEvaluation
    qualitative: QualitativeEvaluation
    status: str


class TranscriptionJobResponse(BaseModel):
    job_id: str
    session_id: str
    topic: str
    status: str


class TranscriptionStatusResponse(BaseModel):
    job_id: str
    session_id: str
    topic: str
    status: str
    transcript_raw: str | None = None
    transcript_corrected: str | None = None
    error: str | None = None


class GoogleLoginRequest(BaseModel):
    authorization_code: str = Field(min_length=1)
    redirect_uri: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: str
    google_user_id: str
    nickname: str | None = None
    profile_image_url: str | None = None


class AuthResponse(BaseModel):
    user: UserResponse
    expires_at: str


class StudySessionCreateRequest(BaseModel):
    lecture_id: str = Field(min_length=1, max_length=100)
    learning_objective_id: str = Field(min_length=1)


class LearningObjectiveResponse(BaseModel):
    learning_objective_id: str
    objective_id: str
    title: str
    description: str | None = None
    display_order: int


class LearningObjectiveListResponse(BaseModel):
    lecture_id: str
    objectives: list[LearningObjectiveResponse]


class StudySessionResponse(BaseModel):
    id: str
    lecture_id: str
    learning_objective_id: str
    objective_title: str
    status: str
    pass_status: str
    total_score: float | None = None
    hint_used: bool
    started_at: str
    completed_at: str | None = None


class StudySessionDetailResponse(BaseModel):
    id: str
    lecture_id: str
    objective_title: str
    status: str
    pass_status: str
    total_score: float
    started_at: str
    completed_at: str | None = None
    transcript_raw: str
    transcript_corrected: str
    segments: list[ReviewSegment]
    claims: list[ClaimEvaluation]
    quantitative: QuantitativeEvaluation
    qualitative: QualitativeEvaluation


class HintResponse(BaseModel):
    session_id: str
    lecture_id: str
    key_objectives: list[str]
