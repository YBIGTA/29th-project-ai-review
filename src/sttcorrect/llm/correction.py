from sttcorrect.llm.base import LLMClient
from sttcorrect.schema import TermDBUsed

SYSTEM_INSTRUCTION = """당신은 STT 표기 오류만 보정하는 편집기입니다.
사용자의 지식, 주장, 오개념을 평가하거나 정정하지 마세요.
사실관계, 개념 정의, 인과관계, 수치, 예시, 결론은 원문이 틀렸더라도 그대로 유지하세요.
확실한 음성 인식 오류가 아니면 원문 표현을 바꾸지 마세요."""

PROMPT_TEMPLATE = """다음은 한국어 STT로 전사된 텍스트입니다.

허용되는 수정은 아래 두 가지뿐입니다.
1. 용어 DB와 발음이 명백히 대응하는 STT 오인식의 용어 표기 보정
2. 띄어쓰기, 문장부호, 문장 분리 같은 형식 정리

다음 작업은 절대 하지 마세요.
- 사용자가 말한 오개념, 잘못된 정의, 잘못된 인과관계나 결론을 정정하지 않기
- 문장 의미를 더 자연스럽게 재작성하지 않기
- 원문에 없는 개념, 예시, 수치, 이름을 추가하지 않기
- 내용을 요약하거나 생략하지 않기
- 확실하지 않은 단어를 추측해 바꾸지 않기

원문의 주장이나 설명이 강의자료와 다르더라도 그것은 사용자의 발화이며 그대로 보존해야 합니다.
문장 구조와 정보 순서를 최대한 유지하세요.

일반 용어: {safe_terms}
※ 아래 단어는 한국어 문법요소/일상어와 발음이 겹칠 수 있어 문맥을 보고 신중히 판단하세요: {risky_terms}

원본 전사:
---
{transcript}
---

수정된 텍스트만 출력하세요."""


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
