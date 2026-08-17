from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PageText:
    page: int
    text: str
    image_png: bytes
    image_width: int
    image_height: int
    raster_image_count: int
    vector_drawing_count: int


@dataclass(frozen=True)
class PdfLoadResult:
    source_file: str
    total_pages: int
    pages: list[PageText]
    empty_pages: list[int]


def load_pdf_pages(pdf_path: Path, *, render_dpi: int = 160) -> PdfLoadResult:
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF 파일이 없습니다: {pdf_path}")
    if render_dpi < 72:
        raise ValueError("render_dpi는 72 이상이어야 합니다.")

    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF가 설치되지 않았습니다. requirements.txt를 설치하세요."
        ) from exc

    pages: list[PageText] = []
    empty_pages: list[int] = []
    with fitz.open(pdf_path) as document:
        total_pages = document.page_count
        for index, pdf_page in enumerate(document):
            page_number = index + 1
            text = pdf_page.get_text("text", sort=True).strip()
            if not text:
                empty_pages.append(page_number)
            pixmap = pdf_page.get_pixmap(
                dpi=render_dpi,
                colorspace=fitz.csRGB,
                alpha=False,
            )
            image_png = pixmap.tobytes("png")
            if not image_png.startswith(b"\x89PNG\r\n\x1a\n"):
                raise RuntimeError(f"p.{page_number} PNG 렌더링에 실패했습니다.")
            pages.append(
                PageText(
                    page=page_number,
                    text=text,
                    image_png=image_png,
                    image_width=pixmap.width,
                    image_height=pixmap.height,
                    raster_image_count=len(pdf_page.get_images(full=True)),
                    vector_drawing_count=len(pdf_page.get_drawings()),
                )
            )

    return PdfLoadResult(
        source_file=pdf_path.name,
        total_pages=total_pages,
        pages=pages,
        empty_pages=empty_pages,
    )


def page_image_data_url(page: PageText) -> str:
    encoded = base64.b64encode(page.image_png).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def split_long_text(text: str, max_chars: int) -> list[str]:
    """Split a long page on paragraph/line boundaries without losing text."""
    if max_chars < 1:
        raise ValueError("max_chars는 1 이상이어야 합니다.")
    if len(text) <= max_chars:
        return [text]

    units = text.splitlines(keepends=True)
    parts: list[str] = []
    current = ""
    for unit in units:
        while len(unit) > max_chars:
            if current:
                parts.append(current)
                current = ""
            parts.append(unit[:max_chars])
            unit = unit[max_chars:]
        if current and len(current) + len(unit) > max_chars:
            parts.append(current)
            current = ""
        current += unit
    if current:
        parts.append(current)
    return parts
