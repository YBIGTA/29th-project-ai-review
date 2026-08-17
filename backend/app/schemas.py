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


class ReviewSubmitRequest(BaseModel):
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
    feedback: Feedback
    status: str
