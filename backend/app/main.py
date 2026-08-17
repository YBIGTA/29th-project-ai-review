from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .integrations import mock_evaluation
from .schemas import ReviewSubmitRequest, ReviewSubmitResponse
from .storage import LocalStorage

AUDIO_SUFFIXES = {".wav", ".webm", ".m4a"}
AUDIO_CONTENT_TYPES = {"audio/wav", "audio/x-wav", "audio/webm", "video/webm", "audio/mp4", "audio/m4a", "audio/x-m4a"}


def create_app() -> FastAPI:
    app = FastAPI(title="AI Review API", version="0.2.0")
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.state.storage = LocalStorage("backend/data")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/stt/transcribe")
    async def transcribe_audio(
        session_id: str = Form(...),
        topic: str = Form("DB"),
        audio_file: UploadFile = File(...),
    ) -> dict[str, object]:
        suffix = Path(audio_file.filename or "").suffix.lower()
        if suffix not in AUDIO_SUFFIXES or audio_file.content_type not in AUDIO_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail="WAV, WebM 또는 M4A 오디오 파일만 업로드할 수 있습니다.")
        _review_id, stored_filename = await app.state.storage.save_audio(audio_file)
        try:
            from sttcorrect.pipeline import run_pipeline
            from sttcorrect.stt.whisper_backend import SttConfig, WhisperSttBackend
            from sttcorrect.term_db.builder import load_term_db

            term_db = load_term_db("data/term_dbs/db_course.json")
            result = run_pipeline(
                audio_path=str(app.state.storage.audio_path(stored_filename)),
                term_db=term_db,
                session_id=session_id,
                topic=topic,
                stt=WhisperSttBackend(SttConfig(model_size="medium", beam_size=2)),
            )
            return result.model_dump(mode="json")
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.post("/api/reviews/submit", response_model=ReviewSubmitResponse, status_code=status.HTTP_201_CREATED)
    def submit_review(request: ReviewSubmitRequest) -> ReviewSubmitResponse:
        evaluation = mock_evaluation(request.transcript_corrected)
        return ReviewSubmitResponse(
            review_id=f"review-{uuid4().hex[:12]}",
            session_id=request.session_id,
            score=evaluation["quantitative"]["total"]["score"],
            transcript=request.transcript_raw,
            corrected_transcript=request.transcript_corrected,
            quantitative=evaluation["quantitative"],
            qualitative=evaluation["qualitative"],
            status="mock",
        )

    return app


app = create_app()
