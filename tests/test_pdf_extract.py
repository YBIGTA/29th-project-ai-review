from sttcorrect.term_db.pdf_extract import dedup_lines


def test_dedup_lines_removes_repeated_header_keeps_first_occurrence():
    pages = [
        "DB Lecture 1\nTable and Row basics\nMore content",
        "DB Lecture 1\nTransaction basics\nEven more content",
        "DB Lecture 1\nTrigger basics\nStill more content",
    ]
    deduped = dedup_lines(pages, repeat_threshold=0.3)
    assert deduped[0].splitlines()[0] == "DB Lecture 1"
    assert "DB Lecture 1" not in deduped[1]
    assert "DB Lecture 1" not in deduped[2]
    # 반복 안 되는 줄은 페이지마다 그대로 유지
    assert "Table and Row basics" in deduped[0]
    assert "Transaction basics" in deduped[1]
    assert "Trigger basics" in deduped[2]


def test_dedup_lines_below_threshold_is_kept_on_every_page():
    pages = ["Shared line\nUnique A", "Other content only"]
    deduped = dedup_lines(pages, repeat_threshold=0.6)
    # 2페이지 중 1페이지에만 등장(1/2=0.5 < 0.6)하므로 반복으로 간주되지 않음
    assert "Shared line" in deduped[0]


def test_dedup_lines_empty_input():
    assert dedup_lines([]) == []
