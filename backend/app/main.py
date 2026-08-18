from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .integrations import evaluate_with_rag
from .schemas import (
    ReviewSubmitRequest,
    ReviewSubmitResponse,
    TranscriptionJobResponse,
    TranscriptionStatusResponse,
)
from .storage import LocalStorage

AUDIO_SUFFIXES = {".wav", ".webm", ".m4a"}
AUDIO_CONTENT_TYPES = {"audio/wav", "audio/x-wav", "audio/webm", "video/webm", "audio/mp4", "audio/m4a", "audio/x-m4a"}
TERM_DB_BY_TOPIC = {
    "기초통계": "data/term_dbs/basic_statistics.json",
    "크롤링": "data/term_dbs/crawling.json",
    "EDA/FE": "data/term_dbs/eda_fe.json",
    "시각화": "data/term_dbs/visualization.json",
}


def create_app() -> FastAPI:
    app = FastAPI(title="AI Review API", version="0.2.0")
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.state.storage = LocalStorage("backend/data")
    app.state.transcription_jobs = {}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/stt/transcribe", response_model=TranscriptionJobResponse, status_code=status.HTTP_202_ACCEPTED)
    async def transcribe_audio(
        background_tasks: BackgroundTasks,
        session_id: str = Form(...),
        topic: str = Form("DB"),
        audio_file: UploadFile = File(...),
    ) -> TranscriptionJobResponse:
        suffix = Path(audio_file.filename or "").suffix.lower()
        if suffix not in AUDIO_SUFFIXES or audio_file.content_type not in AUDIO_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail="WAV, WebM 또는 M4A 오디오 파일만 업로드할 수 있습니다.")
        term_db_path = TERM_DB_BY_TOPIC.get(topic)
        if term_db_path is None:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 topic입니다: {topic}")
        _review_id, stored_filename = await app.state.storage.save_audio(audio_file)
        job_id = f"job-{uuid4().hex[:12]}"
        app.state.transcription_jobs[job_id] = {
            "job_id": job_id,
            "session_id": session_id,
            "topic": topic,
            "status": "transcribing",
            "transcript_raw": None,
            "transcript_corrected": None,
            "error": None,
        }
        background_tasks.add_task(
            _run_transcription_job,
            app,
            job_id,
            str(app.state.storage.audio_path(stored_filename)),
            term_db_path,
        )
        return TranscriptionJobResponse(**app.state.transcription_jobs[job_id])

    @app.get("/api/stt/transcribe/{job_id}", response_model=TranscriptionStatusResponse)
    def transcription_status(job_id: str) -> TranscriptionStatusResponse:
        job = app.state.transcription_jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="transcription job을 찾을 수 없습니다.")
        return TranscriptionStatusResponse(**job)

    @app.post("/api/reviews/submit", response_model=ReviewSubmitResponse, status_code=status.HTTP_201_CREATED)
    def submit_review(request: ReviewSubmitRequest) -> ReviewSubmitResponse:
        job = app.state.transcription_jobs.get(request.job_id) if request.job_id else None
        if job is not None:
            job["status"] = "evaluating"
        from openai import OpenAI, OpenAIError
        from src.config import Settings

        try:
            rag_settings = Settings.from_env(require_api_key=True)
            evaluation = evaluate_with_rag(
                transcript=request.transcript_corrected,
                topic=request.topic,
                settings=rag_settings,
                client=OpenAI(api_key=rag_settings.openai_api_key),
            )
        except (FileNotFoundError, RuntimeError, ValueError, OpenAIError) as exc:
            if job is not None:
                job["status"] = "failed"
                job["error"] = str(exc)
            raise HTTPException(status_code=502, detail=f"RAG 평가에 실패했습니다: {exc}") from exc
        response = ReviewSubmitResponse(
            review_id=f"review-{uuid4().hex[:12]}",
            session_id=request.session_id,
            score=evaluation["quantitative"]["total"]["score"],
            transcript=request.transcript_raw,
            corrected_transcript=request.transcript_corrected,
            quantitative=evaluation["quantitative"],
            qualitative=evaluation["qualitative"],
            status="evaluated",
        )
        if job is not None:
            job["status"] = "evaluated"
        return response

    return app


app = create_app()


def _run_transcription_job(app: FastAPI, job_id: str, audio_path: str, term_db_path: str) -> None:
    job = app.state.transcription_jobs[job_id]
    try:
        from sttcorrect.llm.correction import correct_with_llm
        from sttcorrect.llm.groq_client import GroqLLMClient
        from sttcorrect.stt.whisper_backend import SttConfig, WhisperSttBackend
        from sttcorrect.term_db.builder import load_term_db
        from sttcorrect.term_db.prompt_builder import build_stt_hints

        term_db = load_term_db(term_db_path)
        initial_prompt, hotwords = build_stt_hints(term_db)
        stt = WhisperSttBackend(SttConfig(model_size="medium", beam_size=2))
        raw = stt.transcribe(audio_path, initial_prompt=initial_prompt, hotwords=hotwords)
        job["transcript_raw"] = raw
        job["status"] = "correcting"
        corrected = correct_with_llm(raw, term_db.to_term_db_used(), GroqLLMClient())
        if not corrected.strip():
            raise RuntimeError("LLM이 빈 보정 결과를 반환했습니다.")
        job["transcript_corrected"] = corrected
        job["status"] = "corrected"
    except (FileNotFoundError, RuntimeError, ValueError, KeyError) as exc:
        job["status"] = "failed"
        job["error"] = str(exc)
