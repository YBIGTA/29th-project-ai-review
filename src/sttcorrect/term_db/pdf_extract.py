from pathlib import Path


def extract_page_texts(pdf_path: str | Path) -> list[str]:
    """PyMuPDF(fitz)로 페이지별 page.get_text() 추출. 이미지 전용 페이지는 빈 문자열 반환
    (OCR은 명세상 범위 밖)"""
    import pymupdf

    with pymupdf.open(str(pdf_path)) as doc:
        return [page.get_text() for page in doc]


def dedup_lines(pages: list[str], repeat_threshold: float = 0.3) -> list[str]:
    """정규화한(공백 제거) 비어있지 않은 줄이 등장하는 서로 다른 페이지 수의 비율이
    repeat_threshold 이상이면(슬라이드 헤더/푸터/강의 제목 등) 반복 줄로 간주해
    최초 등장 페이지에서만 남기고 이후 페이지에서는 제거한다."""
    total_pages = len(pages)
    if total_pages == 0:
        return []

    page_line_lists = [
        [line.strip() for line in page.splitlines() if line.strip()] for page in pages
    ]

    page_counts: dict[str, int] = {}
    for lines in page_line_lists:
        for line in set(lines):
            page_counts[line] = page_counts.get(line, 0) + 1

    repeated = {
        line for line, count in page_counts.items() if count / total_pages >= repeat_threshold
    }

    seen: set[str] = set()
    deduped_pages: list[str] = []
    for lines in page_line_lists:
        kept: list[str] = []
        for line in lines:
            if line in repeated:
                if line in seen:
                    continue
                seen.add(line)
            kept.append(line)
        deduped_pages.append("\n".join(kept))
    return deduped_pages


def extract_and_dedup(pdf_path: str | Path) -> str:
    """extract_page_texts + dedup_lines 결과를 하나의 텍스트로 합침"""
    pages = extract_page_texts(pdf_path)
    deduped = dedup_lines(pages)
    return "\n".join(deduped)
