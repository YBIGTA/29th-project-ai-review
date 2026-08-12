from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Literal

try:
    import fitz  # PyMuPDF
except ImportError:  # Optional until the document-processing stack is installed.
    fitz = None


MaterialStatus = Literal["processing", "completed", "failed"]


class MaterialProcessingStore:
    """In-memory job status store for the first FE-BE integration milestone."""

    def __init__(self) -> None:
        self._statuses: dict[str, dict[str, str]] = {}
        self._lock = Lock()

    def start(self, pdf_id: str) -> None:
        with self._lock:
            self._statuses[pdf_id] = {
                "pdf_id": pdf_id,
                "status": "processing",
                "message": "학습 자료를 분석하고 있습니다.",
            }

    def complete(self, pdf_id: str) -> None:
        with self._lock:
            self._statuses[pdf_id] = {
                "pdf_id": pdf_id,
                "status": "completed",
                "message": "학습 자료 분석이 완료되었습니다.",
            }

    def fail(self, pdf_id: str, error: str) -> None:
        with self._lock:
            self._statuses[pdf_id] = {
                "pdf_id": pdf_id,
                "status": "failed",
                "message": "학습 자료 분석에 실패했습니다.",
                "error": error,
            }

    def get(self, pdf_id: str) -> dict[str, str] | None:
        with self._lock:
            status = self._statuses.get(pdf_id)
            return status.copy() if status else None


def extract_text_and_ocr(pdf_path: Path) -> str:
    """Extract native PDF text; OCR can be added for image-only pages here."""
    if fitz is None:
        return ""

    page_texts: list[str] = []
    with fitz.open(pdf_path) as document:
        for page in document:
            text = page.get_text("text").strip()
            if text:
                page_texts.append(text)
            else:
                # Render this page and pass it to PaddleOCR/EasyOCR when connected.
                page_texts.append(ocr_page(page.get_pixmap()))
    return "\n\n".join(text for text in page_texts if text)


def ocr_page(page_image: object) -> str:
    """OCR adapter seam; replace with the STT/RAG team's Korean OCR implementation."""
    del page_image
    return ""


def index_pdf(pdf_id: str, pdf_path: Path, extracted_text: str) -> None:
    """RAG adapter seam for chunking, embedding, and vector index upsert."""
    del pdf_id, pdf_path, extracted_text


def process_material(
    pdf_id: str,
    pdf_path: Path,
    statuses: MaterialProcessingStore,
) -> None:
    try:
        extracted_text = extract_text_and_ocr(pdf_path)
        index_pdf(pdf_id, pdf_path, extracted_text)
    except Exception as exc:
        statuses.fail(pdf_id, str(exc))
        return
    statuses.complete(pdf_id)
