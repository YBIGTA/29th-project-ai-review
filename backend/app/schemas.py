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
    transcript: str
    corrected_transcript: str
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
