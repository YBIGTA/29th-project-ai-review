from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import LECTURES, Settings, resolve_pdf_path
from src.pdf_loader import load_pdf_pages


def main() -> None:
    settings = Settings.from_env()
    failed = False
    for lecture in LECTURES.values():
        try:
            path = resolve_pdf_path(settings, lecture)
            result = load_pdf_pages(path, render_dpi=settings.page_render_dpi)
            extracted_chars = sum(len(page.text) for page in result.pages)
            raster_pages = sum(page.raster_image_count > 0 for page in result.pages)
            print(
                f"{lecture.lecture_id}: {result.total_pages} pages, "
                f"{len(result.pages)} rendered pages, {extracted_chars} text chars, "
                f"raster-image-pages={raster_pages}, text-empty={result.empty_pages}"
            )
        except Exception as exc:
            failed = True
            print(f"{lecture.lecture_id}: 실패: {exc}", file=sys.stderr)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
