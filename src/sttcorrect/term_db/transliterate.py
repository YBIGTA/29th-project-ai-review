# seed_collision_terms.yaml의 curated 테이블에 없는 짧은 단어 몇 개만 다루는 최소 fallback.
# 범용 영한 음차/G2P 엔진이 아니다 — hangulize는 영어 역방향을 지원하지 않아 기각되었고,
# 범용 음차기를 새로 만드는 것도 1차 범위 밖이므로 흔한 1음절 CS 단어만 하드코딩한다.
_TRANSLITERATION_TABLE = {
    "row": "로우",
    "key": "키",
    "set": "셋",
    "one": "원",
    "two": "투",
    "list": "리스트",
    "get": "겟",
    "put": "풋",
    "end": "엔드",
}


def guess_korean_transliteration(term: str) -> str | None:
    """아주 제한적인 규칙 기반 fallback 음차 추정. collision.classify_term에서
    curated 테이블/실제 관찰값을 모두 확인한 뒤 최후 fallback으로만 사용.
    매칭 실패 시 None → 호출측은 기본값 'safe' 처리"""
    return _TRANSLITERATION_TABLE.get(term.lower())
