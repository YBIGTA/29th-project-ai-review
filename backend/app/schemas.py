from __future__ import annotations

from pydantic import BaseModel, Field


class MaterialUploadResponse(BaseModel):
    pdf_id: str
    filename: str
    status: str = "processing"
    message: str = "학습 자료를 분석하고 있습니다."


class MaterialStatusResponse(BaseModel):
    pdf_id: str
    filename: str | None = None
    status: str
    message: str
    error: str | None = None


class Feedback(BaseModel):
    summary: str
    strengths: list[str]
    missing_points: list[str]
    suggestions: list[str]


class ScoreDetail(BaseModel):
    score: int = Field(ge=0)
    max_score: int = Field(gt=0)
    rubric_level: int = Field(ge=0, le=4)
    reason: str


class QuantitativeEvaluation(BaseModel):
    concept_recall: float = Field(ge=0, le=1)
    concept_precision: float = Field(ge=0, le=1)
    concept_f1: float = Field(ge=0, le=1)
    scores: dict[str, ScoreDetail]
    total: ScoreDetail


class QualitativeEvaluation(BaseModel):
    missing_concepts: list[str]
    incorrect_concepts: list[str]
    misconnected_concepts: list[str]
    review_suggestions: list[str]


class ReviewSubmitRequest(BaseModel):
    job_id: str | None = None
    session_id: str
    topic: str
    transcript_raw: str
    transcript_corrected: str
    term_db_used: dict[str, list[str]]


class ReviewSubmitResponse(BaseModel):
    review_id: str
    session_id: str
    score: int = Field(ge=0, le=100)
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
