import re

# 끝을 \b 대신 (?![A-Za-z0-9])로 막는 이유: 파이썬 re는 한글 음절도 \w로 취급해서,
# "PRIMARY키"처럼 한글 조사가 공백 없이 바로 붙으면 "Y"와 "키" 사이에 \b 경계가
# 생기지 않아 매치 자체가 실패한다 (실측: DB.pdf에서 이 패턴으로 Rollback/RDB/Out이
# 후보에서 통째로 누락됨). "그 뒤에 영문자/숫자가 더 안 옴"이라는 lookahead로 바꾸면
# 한글이 바로 붙어도 매치하면서, PrimaryXyz 같은 진짜 다른 단어까지 잘라먹진 않는다.
CAPITALIZED_RE = re.compile(r"\b[A-Z][a-zA-Z]+(?![A-Za-z0-9])")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}(?![A-Za-z0-9])")
ALNUM_MIXED_RE = re.compile(r"\b[A-Za-z]+\d[A-Za-z0-9]*(?![A-Za-z0-9])")  # 예: Neo4j, MySQL8

# CAPITALIZED_RE/ACRONYM_RE가 잡는 "단어" 하나를 공백으로 1~2번 더 이어붙인 구간까지
# 잡는다 (PRIMARY KEY, FOREIGN KEY, NOT NULL, Data Integrity 등). PDF 원문에 실제로
# 인접해서 등장하는 것만 잡으므로 grounded — 우연히 무관한 단어가 붙어 나오는 경우도
# 섞일 수 있지만, 그래봐야 term_db entry 하나 더 생기는 것뿐이라 비용이 낮다.
# 줄바꿈은 제외([ \t]+만 허용) — PDF 슬라이드는 줄바꿈으로 서로 무관한 항목을 나누는
# 경우가 많아서(예: "Beyond RDBMS\n6.\nDB와 DBMS"), \s+로 허용하면 줄이 다른 무관한
# 단어까지 하나의 구로 잘못 묶인다.
COMPOUND_RE = re.compile(
    r"\b(?:[A-Z][a-zA-Z]+|[A-Z]{2,})(?:[ \t]+(?:[A-Z][a-zA-Z]+|[A-Z]{2,})){1,2}(?![A-Za-z0-9])"
)

# 문법적 기능어(관사/전치사 등)만 걸러내는 닫힌 집합. 빈도/wordfreq 기반 필터가 아님에 주의.
FUNCTION_WORDS = {
    "The", "A", "An", "Of", "In", "On", "At", "And", "Or", "For", "To", "Is", "Are", "With", "By", "As",
}


def extract_candidate_terms(text: str) -> set[str]:
    """4개 정규식의 합집합. 빈도/wordfreq/TF-IDF 필터링을 절대 추가하지 않는다
    (명세 3.1절에서 Transaction/Trigger/Primary 같은 핵심 용어가 걸러지는 문제로 기각됨)"""
    return (
        set(CAPITALIZED_RE.findall(text))
        | set(ACRONYM_RE.findall(text))
        | set(ALNUM_MIXED_RE.findall(text))
        | set(COMPOUND_RE.findall(text))
    )


def filter_function_words(candidates: set[str]) -> set[str]:
    """FUNCTION_WORDS(관사/전치사 등 닫힌 집합)만 제거. 단일 단어는 완전 일치로,
    복합어(COMPOUND_RE가 만든 공백 포함 문자열)는 구성 단어 중 하나라도
    FUNCTION_WORDS에 있으면 전체를 제거한다 (예: "The KEY"는 "The" 때문에 제거되지만
    "Data Control Language"는 그대로 유지). 도메인 일반단어까지 거르려던 '하드코딩
    stopword 리스트' 접근(기각됨)과는 다르다는 점을 테스트로 명시할 것"""
    return {c for c in candidates if not (set(c.split()) & FUNCTION_WORDS)}


# Title-Case 3단어 이상 구(예: "Data Control Language")에서 약어를 파생시킨다.
# DCL/TCL처럼 PDF 원문에 리터럴 약어 자체가 한 번도 등장하지 않고 풀네임으로만
# 존재하는 경우를 위한 것 — 위 COMPOUND_RE와 달리 "새 문자열(약어)"을 합성하므로
# 완전히 grounded하진 않지만, 최소 3단어를 요구해 우연한 오탐 위험을 낮췄다.
# COMPOUND_RE와 동일한 이유로 줄바꿈은 제외([ \t]+만 허용).
_TITLE_PHRASE_RE = re.compile(r"\b(?:[A-Z][a-z]+[ \t]+){2,}[A-Z][a-z]+(?![A-Za-z0-9])")


def extract_derived_acronyms(text: str) -> set[str]:
    """'Data Control Language' -> 'DCL'처럼 각 단어 첫 글자를 모아 약어 후보를 만든다.
    이미 리터럴 약어로 관측됐는지는 호출부(builder.py)에서 판단 — 이 함수는 순수
    후보 생성만 한다."""
    return {
        "".join(w[0] for w in m.group().split())
        for m in _TITLE_PHRASE_RE.finditer(text)
    }
