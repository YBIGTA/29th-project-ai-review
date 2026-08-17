from sttcorrect.term_db.term_candidates import extract_candidate_terms, filter_function_words


def test_extract_candidate_terms_finds_various_forms():
    text = "The RDBMS is composed of Table and Row. Neo4j and MySQL8 are graph/relational DBs."
    candidates = extract_candidate_terms(text)
    assert "RDBMS" in candidates
    assert "Table" in candidates
    assert "Row" in candidates
    assert "Neo4j" in candidates
    assert "MySQL8" in candidates


def test_filter_function_words_only_removes_closed_set():
    candidates = {"The", "A", "Transaction", "Trigger", "Primary", "RDBMS"}
    filtered = filter_function_words(candidates)
    assert "The" not in filtered
    assert "A" not in filtered
    assert "Transaction" in filtered
    assert "Trigger" in filtered
    assert "Primary" in filtered
    assert "RDBMS" in filtered


def test_domain_terms_survive_full_pipeline_without_frequency_filtering():
    """빈도/wordfreq 기반 필터링을 재도입하지 않는다는 회귀 가드.
    Transaction/Trigger/Primary는 흔한 영단어처럼 보이지만 이 도메인의 핵심 용어이므로
    반드시 살아남아야 한다 (명세 3.1절에서 wordfreq 필터링이 기각된 이유)."""
    text = (
        "A Transaction must satisfy ACID. The Trigger fires before Insert. "
        "The Primary key uniquely identifies a Row in a Table."
    )
    survivors = filter_function_words(extract_candidate_terms(text))
    for term in ("Transaction", "Trigger", "Primary"):
        assert term in survivors
