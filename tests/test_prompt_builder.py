from sttcorrect.schema import TermDB, TermEntry
from sttcorrect.term_db.prompt_builder import build_stt_hints


def _entry(term: str) -> TermEntry:
    return TermEntry(term=term, collision_label="safe", source="acronym")


def test_build_stt_hints_format():
    term_db = TermDB(entries=[_entry("RDBMS"), _entry("Row")])
    initial_prompt, hotwords = build_stt_hints(term_db)
    assert "RDBMS" in initial_prompt
    assert "Row" in initial_prompt
    assert initial_prompt.startswith("이 강의에는")
    assert hotwords == "RDBMS, Row"


def test_build_stt_hints_uses_all_terms_regardless_of_collision_label():
    term_db = TermDB(
        entries=[
            TermEntry(term="Safe1", collision_label="safe", source="capitalized"),
            TermEntry(term="Risky1", collision_label="particle_collision", source="capitalized"),
        ]
    )
    _, hotwords = build_stt_hints(term_db)
    assert "Safe1" in hotwords
    assert "Risky1" in hotwords


def test_build_stt_hints_truncates_to_max_terms():
    term_db = TermDB(entries=[_entry(f"Term{i}") for i in range(10)])
    initial_prompt, hotwords = build_stt_hints(term_db, max_terms=3)
    assert hotwords == "Term0, Term1, Term2"
    assert "Term3" not in hotwords
    assert "Term9" not in initial_prompt
