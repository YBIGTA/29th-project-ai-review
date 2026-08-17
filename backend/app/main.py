from __future__ import annotations

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
        evaluation = mock_evaluation(request.corrected_transcript)
        return ReviewSubmitResponse(
            review_id=request.review_id,
            session_id=request.session_id,
            score=evaluation["score"],
            transcript=request.transcript,
            corrected_transcript=request.corrected_transcript,
            feedback={key: evaluation[key] for key in ("summary", "strengths", "missing_points", "suggestions")},
            status="mock",
        )

    return app


app = create_app()
