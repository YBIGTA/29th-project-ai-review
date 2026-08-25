from sttcorrect.term_db.term_candidates import (
    extract_candidate_terms,
    extract_derived_acronyms,
    filter_function_words,
)


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


def test_extract_candidate_terms_matches_english_word_immediately_before_hangul():
    # 파이썬 re는 한글 음절도 \w로 취급해서, 한글 조사가 공백 없이 바로 붙으면
    # \b 경계가 안 생겨 예전엔 통째로 매치가 실패했다 (실측: DB.pdf에서 Rollback/
    # RDB/Out이 이 패턴으로 후보에서 누락됨).
    candidates = extract_candidate_terms("Rollback됩니다 그리고 RDB는 예시이다")
    assert "Rollback" in candidates
    assert "RDB" in candidates


def test_extract_candidate_terms_does_not_split_genuinely_longer_word():
    # 끝 경계를 (?![A-Za-z0-9])로 바꿔도 PrimaryXyz 같은 진짜 다른 단어를
    # "Primary"로 잘라먹으면 안 된다.
    candidates = extract_candidate_terms("PrimaryXyz는 다른 단어다")
    assert "PrimaryXyz" in candidates
    assert "Primary" not in candidates


def test_extract_candidate_terms_includes_adjacent_compound_phrase():
    candidates = extract_candidate_terms("PRIMARY KEY는 테이블에서 행을 식별한다.")
    assert "PRIMARY KEY" in candidates


def test_extract_candidate_terms_compound_does_not_cross_newline():
    # PDF 슬라이드는 줄바꿈으로 서로 무관한 항목을 나누는 경우가 많다
    # (예: "Beyond RDBMS\n6.\nDB와 DBMS") — 줄이 다른 단어까지 하나의 구로
    # 잘못 묶이면 안 된다.
    candidates = extract_candidate_terms("Beyond RDBMS\n6.\nExample")
    assert "Beyond RDBMS\n6.\nExample" not in candidates
    assert not any("\n" in c for c in candidates)


def test_filter_function_words_removes_compound_containing_function_word():
    # COMPOUND_RE가 관사+실제용어("The KEY")까지 하나의 후보로 잡을 수 있는데,
    # 구성 단어 중 하나라도 FUNCTION_WORDS면 전체를 걸러야 한다.
    candidates = {"The KEY", "PRIMARY KEY", "Data Control Language"}
    filtered = filter_function_words(candidates)
    assert "The KEY" not in filtered
    assert "PRIMARY KEY" in filtered
    assert "Data Control Language" in filtered


def test_extract_derived_acronyms_from_title_case_phrase():
    text = "Data Control Language 는 권한을 관리하는 언어이다. Transaction Control Language 는 트랜잭션을 제어한다."
    derived = extract_derived_acronyms(text)
    assert "DCL" in derived
    assert "TCL" in derived


def test_extract_derived_acronyms_requires_at_least_three_words():
    assert extract_derived_acronyms("Primary Key 는 무엇인가?") == set()


def test_extract_derived_acronyms_does_not_cross_newline():
    derived = extract_derived_acronyms("Data Control\nLanguage 는 예시이다")
    assert "DCL" not in derived
