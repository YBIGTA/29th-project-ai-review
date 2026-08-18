from sttcorrect.schema import TermDB

_PROMPT_PREFIX = "이 강의에는 다음과 같은 전문 용어가 자주 등장합니다: "


def build_stt_hints(term_db: TermDB, max_terms: int = 30) -> tuple[str, str]:
    """(initial_prompt, hotwords) 반환.
    initial_prompt: 짧은 한국어 프레이밍 문장 + 쉼표로 이은 용어 목록
    hotwords: 쉼표로 이은 용어 원문
    collision_label과 무관하게 전체 용어 사용 (음향 힌트 단계에서는 위험도 구분 무의미).
    max_terms로 길이 제한 (향후 절차 3번: 실측 후 튜닝)"""
    terms = [entry.term for entry in term_db.entries][:max_terms]
    initial_prompt = _PROMPT_PREFIX + ", ".join(terms)
    hotwords = ", ".join(terms)
    return initial_prompt, hotwords
