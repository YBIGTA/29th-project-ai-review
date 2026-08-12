from __future__ import annotations

from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .integrations import mock_review
from .material_processing import MaterialProcessingStore, process_material
from .schemas import MaterialStatusResponse, MaterialUploadResponse, ReviewSubmitResponse
from .storage import LocalStorage

PDF_CONTENT_TYPE = "application/pdf"
AUDIO_SUFFIXES = {".wav", ".webm"}
AUDIO_CONTENT_TYPES = {"audio/wav", "audio/x-wav", "audio/webm", "video/webm"}


def _uploaded_pdf_stem(filename: str) -> str:
    return Path(filename.replace("\\", "/")).stem


def create_app(storage_root: str | Path | None = None) -> FastAPI:
    app = FastAPI(
        title="AI Review API",
        version="0.1.0",
        description="Mock-first backend for material upload and oral review submission.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.storage = LocalStorage(storage_root or settings.storage_dir)
    app.state.material_statuses = MaterialProcessingStore()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/api/materials/upload",
        response_model=MaterialUploadResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def upload_material(
        background_tasks: BackgroundTasks,
        pdf_file: UploadFile = File(..., description="학습 자료 PDF 파일"),
    ) -> MaterialUploadResponse:
        filename = pdf_file.filename or ""
        if Path(filename).suffix.lower() != ".pdf" or pdf_file.content_type not in {
            PDF_CONTENT_TYPE,
            "application/octet-stream",
        }:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="PDF 파일만 업로드할 수 있습니다.",
            )

        header = await pdf_file.read(5)
        await pdf_file.seek(0)
        if header != b"%PDF-":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효한 PDF 파일이 아닙니다.",
            )

        pdf_id, _stored_filename = await app.state.storage.save_material(pdf_file)
        app.state.material_statuses.start(pdf_id)
        background_tasks.add_task(
            process_material,
            pdf_id,
            app.state.storage.material_path(pdf_id),
            app.state.material_statuses,
        )
        return MaterialUploadResponse(pdf_id=pdf_id, filename=_uploaded_pdf_stem(filename))

    @app.get(
        "/api/materials/{pdf_id}/status",
        response_model=MaterialStatusResponse,
    )
    def material_status(pdf_id: str) -> MaterialStatusResponse:
        material_status = app.state.material_statuses.get(pdf_id)
        if material_status is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 pdf_id의 처리 상태를 찾을 수 없습니다.",
            )
        return MaterialStatusResponse(**material_status)

    @app.post(
        "/api/reviews/submit",
        response_model=ReviewSubmitResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def submit_review(
        pdf_id: str = Form(...),
        audio_file: UploadFile = File(..., description="WAV 또는 WebM 오디오 파일"),
    ) -> ReviewSubmitResponse:
        material_status = app.state.material_statuses.get(pdf_id)
        if material_status and material_status["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="학습 자료 분석이 완료된 후 리뷰를 제출할 수 있습니다.",
            )
        pdf_path = app.state.storage.material_path(pdf_id)
        if not pdf_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 pdf_id의 학습 자료를 찾을 수 없습니다.",
            )

        audio_filename = audio_file.filename or ""
        audio_suffix = Path(audio_filename).suffix.lower()
        if audio_suffix not in AUDIO_SUFFIXES or audio_file.content_type not in AUDIO_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="WAV 또는 WebM 오디오 파일만 업로드할 수 있습니다.",
            )

        header = await audio_file.read(1)
        await audio_file.seek(0)
        if not header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="빈 오디오 파일은 제출할 수 없습니다.",
            )

        review_id, stored_audio_filename = await app.state.storage.save_audio(audio_file)
        audio_path = app.state.storage.audio_path(stored_audio_filename)
        transcript, evaluation = mock_review(pdf_path, audio_path)
        return ReviewSubmitResponse(
            review_id=review_id,
            pdf_id=pdf_id,
            audio_filename=stored_audio_filename,
            score=evaluation["score"],
            transcript=transcript,
            feedback={
                "summary": evaluation["summary"],
                "strengths": evaluation["strengths"],
                "missing_points": evaluation["missing_points"],
                "suggestions": evaluation["suggestions"],
            },
            status="mock",
        )

    return app


app = create_app()
