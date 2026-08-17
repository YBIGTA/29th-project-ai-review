import re

CAPITALIZED_RE = re.compile(r"\b[A-Z][a-zA-Z]+\b")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}\b")
ALNUM_MIXED_RE = re.compile(r"\b[A-Za-z]+\d[A-Za-z0-9]*\b")  # 예: Neo4j, MySQL8

# 문법적 기능어(관사/전치사 등)만 걸러내는 닫힌 집합. 빈도/wordfreq 기반 필터가 아님에 주의.
FUNCTION_WORDS = {
    "The", "A", "An", "Of", "In", "On", "At", "And", "Or", "For", "To", "Is", "Are", "With", "By", "As",
}


def extract_candidate_terms(text: str) -> set[str]:
    """3개 정규식의 합집합. 빈도/wordfreq/TF-IDF 필터링을 절대 추가하지 않는다
    (명세 3.1절에서 Transaction/Trigger/Primary 같은 핵심 용어가 걸러지는 문제로 기각됨)"""
    return (
        set(CAPITALIZED_RE.findall(text))
        | set(ACRONYM_RE.findall(text))
        | set(ALNUM_MIXED_RE.findall(text))
    )


def filter_function_words(candidates: set[str]) -> set[str]:
    """FUNCTION_WORDS(관사/전치사 등 닫힌 집합)만 제거. 도메인 일반단어까지 거르려던
    '하드코딩 stopword 리스트' 접근(기각됨)과는 다르다는 점을 테스트로 명시할 것"""
    return {c for c in candidates if c not in FUNCTION_WORDS}
