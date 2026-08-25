from __future__ import annotations

import logging
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import httpx
from fastapi import BackgroundTasks, Cookie, FastAPI, File, Form, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import get_session
from .models import AuthSession, AudioFile, Evaluation, LearningObjective, Transcription, User, StudySession
from sqlalchemy import select, update
from .integrations import evaluate_selected_topic
from .schemas import (
    ReviewSubmitRequest,
    ReviewSubmitResponse,
    TranscriptionJobResponse,
    TranscriptionStatusResponse,
    AuthResponse,
    GoogleLoginRequest,
    StudySessionCreateRequest,
    StudySessionResponse,
    HintResponse,
    LearningObjectiveListResponse,
    LearningObjectiveResponse,
    StudySessionDetailResponse,
    UserResponse,
)
from .storage import LocalStorage

AUDIO_SUFFIXES = {".wav", ".webm", ".m4a"}
AUDIO_CONTENT_TYPES = {"audio/wav", "audio/x-wav", "audio/webm", "video/webm", "audio/mp4", "audio/m4a", "audio/x-m4a"}
LOGGER = logging.getLogger(__name__)
TERM_DB_BY_TOPIC = {
    "기초통계": "data/term_dbs/basic_statistics.json",
    "크롤링": "data/term_dbs/crawling.json",
    "EDA/FE": "data/term_dbs/eda_fe.json",
    "시각화": "data/term_dbs/visualization.json",
    "CS기초": "data/term_dbs/cs_basics.json",
    "Python개발환경": "data/term_dbs/python_environment.json",
    "Git": "data/term_dbs/git.json",
    "Web 기초": "data/term_dbs/web.json",
    "네트워크 기초": "data/term_dbs/network_basics.json",
    "ML": "data/term_dbs/machine_learning.json",
    "DL": "data/term_dbs/deep_learning.json",
    "CV": "data/term_dbs/computer_vision.json",
    "NLP": "data/term_dbs/nlp.json",
    "AI Agent": "data/term_dbs/ai_agent.json",
    "AWS": "data/term_dbs/aws.json",
    "DB": "data/term_dbs/db.json",
    "Docker": "data/term_dbs/docker.json",
    "LLM": "data/term_dbs/llm.json",
    "RAG": "data/term_dbs/rag.json",
}
LECTURE_ID_BY_TOPIC = {
    "기초통계": "basic_statistics",
    "크롤링": "crawling",
    "EDA/FE": "eda_fe",
    "시각화": "visualization",
    "CS기초": "cs_basics",
    "Python개발환경": "python_environment",
    "Git": "git",
    "Web 기초": "web",
    "네트워크 기초": "network_basics",
    "ML": "machine_learning",
    "DL": "deep_learning",
    "CV": "computer_vision",
    "NLP": "nlp",
    "AI Agent": "ai_agent",
    "AWS": "aws",
    "DB": "db",
    "Docker": "docker",
    "LLM": "llm",
    "RAG": "rag",
}


def create_app() -> FastAPI:
    app = FastAPI(title="AI Review API", version="2.0.0")
    app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.state.storage = LocalStorage("backend/data")
    app.state.transcription_jobs = {}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/auth/google", response_model=AuthResponse)
    async def google_login(request: GoogleLoginRequest, response: Response) -> AuthResponse:
        if not settings.google_client_id:
            raise HTTPException(status_code=503, detail="GOOGLE_CLIENT_ID가 설정되지 않았습니다.")
        token_payload = {
            "grant_type": "authorization_code",
            "client_id": settings.google_client_id,
            "redirect_uri": request.redirect_uri,
            "code": request.authorization_code,
        }
        if settings.google_client_secret:
            token_payload["client_secret"] = settings.google_client_secret
        async with httpx.AsyncClient(timeout=10) as client:
            token_response = await client.post("https://oauth2.googleapis.com/token", data=token_payload)
            if token_response.is_error:
                raise HTTPException(status_code=401, detail="Google authorization code 교환에 실패했습니다.")
            access_token = token_response.json().get("access_token")
            user_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if user_response.is_error:
            raise HTTPException(status_code=401, detail="Google 사용자 정보 조회에 실패했습니다.")
        google_user = user_response.json()
        google_user_id = str(google_user["sub"])
        with get_session() as db:
            user = db.scalar(select(User).where(User.google_user_id == google_user_id))
            if user is None:
                user = User(google_user_id=google_user_id)
                db.add(user)
            user.nickname = google_user.get("name") or google_user.get("email")
            user.profile_image_url = google_user.get("picture")
            user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
            db.flush()
            db.commit()
        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(days=7)
        with get_session() as db:
            db.add(AuthSession(user_id=user.id, session_token_hash=_hash_token(raw_token), expires_at=expires_at.replace(tzinfo=None)))
            db.commit()
        response.set_cookie(settings.auth_cookie_name, raw_token, httponly=True, secure=settings.auth_cookie_secure, samesite=settings.auth_cookie_samesite, max_age=7 * 24 * 60 * 60)
        return AuthResponse(user=UserResponse(id=str(user.id), google_user_id=user.google_user_id, nickname=user.nickname, profile_image_url=user.profile_image_url), expires_at=expires_at.isoformat())

    @app.get("/api/auth/me", response_model=UserResponse)
    def current_user(session_cookie: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> UserResponse:
        user = _get_user_from_cookie(session_cookie)
        return UserResponse(id=str(user.id), google_user_id=user.google_user_id, nickname=user.nickname, profile_image_url=user.profile_image_url)

    @app.post("/api/auth/logout", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
    def logout(response: Response, session_cookie: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> None:
        if session_cookie:
            with get_session() as db:
                db.execute(update(AuthSession).where(AuthSession.session_token_hash == _hash_token(session_cookie)).values(revoked_at=datetime.now(UTC).replace(tzinfo=None)))
                db.commit()
        response.delete_cookie(settings.auth_cookie_name)

    @app.get("/api/learning-objectives", response_model=LearningObjectiveListResponse)
    def list_learning_objectives(lecture_id: str) -> LearningObjectiveListResponse:
        with get_session() as db:
            objectives = db.scalars(
                select(LearningObjective)
                .where(
                    LearningObjective.lecture_id == lecture_id,
                    LearningObjective.parent_id.is_(None),
                    LearningObjective.is_active.is_(True),
                    LearningObjective.rag_objective_id.is_not(None),
                )
                .order_by(LearningObjective.display_order)
            ).all()
        return LearningObjectiveListResponse(
            lecture_id=lecture_id,
            objectives=[
                LearningObjectiveResponse(
                    learning_objective_id=str(objective.id),
                    objective_id=objective.rag_objective_id,
                    title=objective.title,
                    description=objective.description,
                    display_order=objective.display_order,
                )
                for objective in objectives
            ],
        )

    @app.post("/api/study-sessions", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
    def create_study_session(request: StudySessionCreateRequest, session_cookie: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> StudySessionResponse:
        user = _get_user_from_cookie(session_cookie)
        objective_id = _parse_uuid(request.learning_objective_id)
        if objective_id is None:
            raise HTTPException(status_code=400, detail="learning_objective_id는 UUID 형식이어야 합니다.")
        with get_session() as db:
            objective = db.scalar(select(LearningObjective).where(
                LearningObjective.id == objective_id,
                LearningObjective.lecture_id == request.lecture_id,
                LearningObjective.parent_id.is_(None),
                LearningObjective.is_active.is_(True),
            ))
            if objective is None:
                raise HTTPException(status_code=400, detail="해당 lecture의 상위 학습목표를 찾을 수 없습니다.")
            row = StudySession(user_id=user.id, lecture_id=request.lecture_id, learning_objective_id=objective_id, status="created")
            db.add(row)
            db.commit()
            db.refresh(row)
            return _study_session_response(row, objective.title, None)

    @app.get("/api/study-sessions", response_model=list[StudySessionResponse])
    def list_study_sessions(session_cookie: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> list[StudySessionResponse]:
        user = _get_user_from_cookie(session_cookie)
        with get_session() as db:
            rows = db.execute(
                select(StudySession, LearningObjective.title.label("objective_title"), Evaluation.total_score.label("total_score"))
                .join(LearningObjective, LearningObjective.id == StudySession.learning_objective_id)
                .outerjoin(Evaluation, Evaluation.study_session_id == StudySession.id)
                .where(StudySession.user_id == user.id)
                .order_by(StudySession.created_at.desc())
            ).all()
            return [
                _study_session_response(row.StudySession, row.objective_title, row.total_score)
                for row in rows
            ]

    @app.get("/api/study-sessions/{session_id}", response_model=StudySessionDetailResponse)
    def get_study_session_detail(session_id: str, session_cookie: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> StudySessionDetailResponse:
        user = _get_user_from_cookie(session_cookie)
        study_session_id = _parse_uuid(session_id)
        if study_session_id is None:
            raise HTTPException(status_code=400, detail="session_id는 UUID 형식이어야 합니다.")
        with get_session() as db:
            study_session = db.scalar(
                select(StudySession).where(StudySession.id == study_session_id, StudySession.user_id == user.id)
            )
            if study_session is None:
                raise HTTPException(status_code=404, detail="study_session을 찾을 수 없습니다.")
            objective = db.get(LearningObjective, study_session.learning_objective_id)
            transcription = db.scalar(select(Transcription).where(Transcription.study_session_id == study_session_id))
            evaluation = db.scalar(select(Evaluation).where(Evaluation.study_session_id == study_session_id))
            if transcription is None or evaluation is None:
                raise HTTPException(status_code=409, detail="아직 평가가 완료되지 않은 세션입니다.")
            payload = evaluation.evaluation_json
            return StudySessionDetailResponse(
                id=str(study_session.id),
                lecture_id=study_session.lecture_id,
                objective_title=objective.title if objective is not None else "",
                status=study_session.status,
                pass_status=study_session.pass_status,
                total_score=float(evaluation.total_score),
                started_at=study_session.started_at.isoformat(),
                completed_at=study_session.completed_at.isoformat() if study_session.completed_at else None,
                transcript_raw=transcription.raw_text,
                transcript_corrected=transcription.corrected_text,
                segments=payload["segments"],
                claims=payload["claims"],
                quantitative=payload["quantitative"],
                qualitative=payload["qualitative"],
            )

    @app.get("/api/study-sessions/{session_id}/hint", response_model=HintResponse)
    def get_study_hint(session_id: str, session_cookie: str | None = Cookie(default=None, alias=settings.auth_cookie_name)) -> HintResponse:
        user = _get_user_from_cookie(session_cookie)
        study_session_id = _parse_uuid(session_id)
        if study_session_id is None:
            raise HTTPException(status_code=400, detail="session_id는 UUID 형식이어야 합니다.")
        with get_session() as db:
            study_session = db.scalar(select(StudySession).where(StudySession.id == study_session_id, StudySession.user_id == user.id))
            if study_session is None:
                raise HTTPException(status_code=404, detail="study_session을 찾을 수 없습니다.")
            key_objectives = db.scalars(
                select(LearningObjective.title)
                .where(
                    LearningObjective.parent_id == study_session.learning_objective_id,
                    LearningObjective.is_active.is_(True),
                )
                .order_by(LearningObjective.display_order)
            ).all()
            study_session.hint_used = True
            db.commit()
        return HintResponse(session_id=str(study_session_id), lecture_id=study_session.lecture_id, key_objectives=key_objectives)

    @app.post("/api/stt/transcribe", response_model=TranscriptionJobResponse, status_code=status.HTTP_202_ACCEPTED)
    async def transcribe_audio(
        background_tasks: BackgroundTasks,
        session_id: str = Form(...),
        topic: str = Form("기초통계"),
        audio_file: UploadFile = File(...),
    ) -> TranscriptionJobResponse:
        suffix = Path(audio_file.filename or "").suffix.lower()
        if suffix not in AUDIO_SUFFIXES or audio_file.content_type not in AUDIO_CONTENT_TYPES:
            raise HTTPException(status_code=415, detail="WAV, WebM 또는 M4A 오디오 파일만 업로드할 수 있습니다.")
        term_db_path = TERM_DB_BY_TOPIC.get(topic)
        if term_db_path is None:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 topic입니다: {topic}")
        _review_id, stored_filename = await app.state.storage.save_audio(audio_file)
        audio_file_id = _persist_audio_file(app, session_id, stored_filename, audio_file)
        job_id = f"job-{uuid4().hex[:12]}"
        app.state.transcription_jobs[job_id] = {
            "job_id": job_id,
            "session_id": session_id,
            "topic": topic,
            "status": "transcribing",
            "transcript_raw": None,
            "transcript_corrected": None,
            "error": None,
            "audio_file_id": audio_file_id,
            "transcription_id": None,
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
        expected_lecture_id = LECTURE_ID_BY_TOPIC.get(request.topic)
        if expected_lecture_id != request.lecture_id:
            raise HTTPException(
                status_code=400,
                detail="topic과 lecture_id가 일치하지 않습니다.",
            )
        job = app.state.transcription_jobs.get(request.job_id) if request.job_id else None
        if job is not None:
            job["status"] = "evaluating"
        from openai import OpenAI, OpenAIError
        from src.config import Settings

        try:
            rag_settings = Settings.from_env(require_api_key=True)
            evaluation = evaluate_selected_topic(
                transcript=request.transcript_corrected,
                lecture_id=request.lecture_id,
                objective_id=request.objective_id,
                settings=rag_settings,
                client=OpenAI(api_key=rag_settings.openai_api_key),
            )
        except (FileNotFoundError, RuntimeError, ValueError, OpenAIError) as exc:
            if job is not None:
                job["status"] = "failed"
                job["error"] = str(exc)
            raise HTTPException(status_code=502, detail=f"Rubric 평가에 실패했습니다: {exc}") from exc
        response = ReviewSubmitResponse(
            review_id=f"review-{uuid4().hex[:12]}",
            session_id=request.session_id,
            lecture_id=request.lecture_id,
            objective_id=request.objective_id,
            score=evaluation["quantitative"]["total"]["score"],
            pass_status=_pass_status(float(evaluation["quantitative"]["total"]["score"])),
            transcript=request.transcript_raw,
            corrected_transcript=request.transcript_corrected,
            segments=evaluation["segments"],
            claims=evaluation["claims"],
            quantitative=evaluation["quantitative"],
            qualitative=evaluation["qualitative"],
            status="evaluated",
        )
        _persist_evaluation(request, evaluation, job)
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
        LOGGER.info("STT 시작: job_id=%s audio=%s model=medium beam=5", job_id, audio_path)
        stt = WhisperSttBackend(SttConfig(model_size="medium", beam_size=5))
        raw = stt.transcribe(audio_path, initial_prompt=initial_prompt, hotwords=hotwords)
        job["transcript_raw"] = raw
        job["status"] = "correcting"
        LOGGER.info("STT 완료: job_id=%s chars=%s", job_id, len(raw))
        corrected = correct_with_llm(raw, term_db.to_term_db_used(), GroqLLMClient())
        if not corrected.strip():
            raise RuntimeError("LLM이 빈 보정 결과를 반환했습니다.")
        job["transcript_corrected"] = corrected
        job["transcription_id"] = _persist_transcription(job)
        job["status"] = "corrected"
        LOGGER.info("보정 완료: job_id=%s chars=%s", job_id, len(corrected))
    except Exception as exc:
        job["status"] = "failed"
        job["error"] = str(exc)
        LOGGER.exception("STT/보정 실패: job_id=%s", job_id)


def _pass_status(total_score: float) -> str:
    return "P" if total_score >= settings.pass_score_threshold else "NP"


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _parse_uuid(value: str | None) -> UUID | None:
    try:
        return UUID(value) if value else None
    except ValueError:
        return None


def _persist_audio_file(app: FastAPI, session_id: str, stored_filename: str, upload: UploadFile) -> str | None:
    study_session_id = _parse_uuid(session_id)
    if study_session_id is None:
        return None
    with get_session() as db:
        if db.get(StudySession, study_session_id) is None:
            raise HTTPException(status_code=404, detail="study_session을 찾을 수 없습니다.")
        study_session = db.get(StudySession, study_session_id)
        study_session.status = "processing"
        row = AudioFile(study_session_id=study_session_id, storage_key=str(app.state.storage.audio_path(stored_filename)), original_filename=upload.filename, mime_type=upload.content_type or "application/octet-stream")
        db.add(row)
        db.commit()
        return str(row.id)


def _persist_transcription(job: dict) -> str | None:
    study_session_id = _parse_uuid(job.get("session_id"))
    audio_file_id = _parse_uuid(job.get("audio_file_id"))
    if study_session_id is None or audio_file_id is None:
        return None
    with get_session() as db:
        row = Transcription(study_session_id=study_session_id, audio_file_id=audio_file_id, raw_text=job["transcript_raw"], corrected_text=job["transcript_corrected"], stt_model="faster-whisper-medium", beam_size=5, correction_model="groq")
        db.add(row)
        db.commit()
        return str(row.id)


def _persist_evaluation(request: ReviewSubmitRequest, evaluation: dict, job: dict | None) -> None:
    study_session_id = _parse_uuid(request.session_id)
    transcription_id = _parse_uuid(job.get("transcription_id") if job else None)
    if study_session_id is None or transcription_id is None:
        return
    scores = evaluation["quantitative"]["scores"]
    total_score = float(evaluation["quantitative"]["total"]["score"])
    evaluation_pass_status = _pass_status(total_score)
    with get_session() as db:
        db.add(Evaluation(study_session_id=study_session_id, transcription_id=transcription_id, essential_score=scores["essential"]["score"], supporting_score=scores["supporting"]["score"], coverage_score=scores["coverage"]["score"], total_score=total_score, pass_status=evaluation_pass_status, evaluation_json=evaluation))
        study_session = db.get(StudySession, study_session_id)
        if study_session is not None:
            study_session.status = "completed"
            if evaluation_pass_status == "P" or study_session.pass_status != "P":
                study_session.pass_status = evaluation_pass_status
            study_session.completed_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()


def _get_user_from_cookie(session_cookie: str | None) -> User:
    if not session_cookie:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    with get_session() as db:
        user = db.scalar(select(User).join(AuthSession, AuthSession.user_id == User.id).where(AuthSession.session_token_hash == _hash_token(session_cookie), AuthSession.revoked_at.is_(None), AuthSession.expires_at > datetime.now(UTC).replace(tzinfo=None)))
    if user is None:
        raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 로그인 세션입니다.")
    return user


def _study_session_response(row: StudySession, objective_title: str, total_score: float | None) -> StudySessionResponse:
    return StudySessionResponse(
        id=str(row.id),
        lecture_id=row.lecture_id,
        learning_objective_id=str(row.learning_objective_id),
        objective_title=objective_title,
        status=row.status,
        pass_status=row.pass_status,
        total_score=float(total_score) if total_score is not None else None,
        hint_used=row.hint_used,
        started_at=row.started_at.isoformat(),
        completed_at=row.completed_at.isoformat() if row.completed_at else None,
    )
