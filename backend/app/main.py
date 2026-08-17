from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .integrations import mock_evaluation
from .schemas import ReviewSubmitRequest, ReviewSubmitResponse


def create_app() -> FastAPI:
    app = FastAPI(title="AI Review API", version="0.2.0")
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/reviews/submit", response_model=ReviewSubmitResponse, status_code=status.HTTP_201_CREATED)
    def submit_review(request: ReviewSubmitRequest) -> ReviewSubmitResponse:
        evaluation = mock_evaluation(request.transcript_corrected)
        return ReviewSubmitResponse(
            review_id=f"review-{uuid4().hex[:12]}",
            session_id=request.session_id,
            score=evaluation["score"],
            transcript=request.transcript_raw,
            corrected_transcript=request.transcript_corrected,
            feedback={key: evaluation[key] for key in ("summary", "strengths", "missing_points", "suggestions")},
            status="mock",
        )

    return app


app = create_app()
