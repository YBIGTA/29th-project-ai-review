from sttcorrect.llm.base import LLMClient
from sttcorrect.schema import TermDBUsed

PROMPT_TEMPLATE = """다음은 한국어 STT로 전사된 텍스트입니다. 아래 용어 목록을 참고해
발음이 잘못 인식된 부분을 자연스럽게 교정하세요. 문장 구조는 바꾸지 마세요.
원문의 내용을 임의로 생략하거나 지어내지 마세요 — 알아듣기 어려운 부분이라도 반드시
원문 그대로 유지하고, 실제 원문에 없는 단어(예: 이름, 값)를 추측해서 채워 넣지 마세요.

일반 용어: {safe_terms}
※ 아래 단어는 한국어 문법요소/일상어와 발음이 겹칠 수 있어 문맥을 보고 신중히 판단하세요: {risky_terms}

원본 전사: {transcript}
교정된 텍스트만 출력하세요."""


def build_correction_prompt(transcript: str, term_db_used: TermDBUsed) -> str:
    """명세 7.2절의 정확한 병합 규칙 구현:
    safe_terms = term_db_used.safe + term_db_used.content_word_collision
    risky_terms = term_db_used.particle_collision (이것만 분리)
    3분류 TermDBUsed -> 프롬프트 상 2분류로 축약"""
    safe_terms = term_db_used.safe + term_db_used.content_word_collision
    risky_terms = term_db_used.particle_collision
    return PROMPT_TEMPLATE.format(
        safe_terms=", ".join(safe_terms),
        risky_terms=", ".join(risky_terms),
        transcript=transcript,
    )


def correct_with_llm(transcript: str, term_db_used: TermDBUsed, llm: LLMClient) -> str:
    """build_correction_prompt 후 llm.call_llm 호출. llm은 DI로 주입 —
    파이프라인/테스트가 실제 백엔드 없이 Fake를 넣을 수 있게 함"""
    return llm.call_llm(build_correction_prompt(transcript, term_db_used))
