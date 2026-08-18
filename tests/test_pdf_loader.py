import fitz

from src.pdf_loader import load_pdf_pages, page_image_data_url, split_long_text


def test_split_long_text_keeps_all_content():
    text = "첫 번째 줄\n두 번째 줄\n세 번째 줄"
    parts = split_long_text(text, max_chars=10)

    assert all(len(part) <= 10 for part in parts)
    assert "".join(parts) == text


def test_split_long_text_does_not_split_short_text():
    assert split_long_text("짧은 문장", max_chars=100) == ["짧은 문장"]


def test_loader_renders_and_keeps_text_empty_pages(tmp_path):
    path = tmp_path / "sample.pdf"
    document = fitz.open()
    first = document.new_page(width=640, height=360)
    first.insert_text((40, 60), "Visible text")
    document.new_page(width=640, height=360)
    document.save(path)
    document.close()

    result = load_pdf_pages(path, render_dpi=72)

    assert result.total_pages == 2
    assert len(result.pages) == 2
    assert result.empty_pages == [2]
    assert result.pages[0].image_png.startswith(b"\x89PNG")
    assert result.pages[0].image_width == 640
    assert result.pages[0].image_height == 360
    assert page_image_data_url(result.pages[0]).startswith("data:image/png;base64,")
