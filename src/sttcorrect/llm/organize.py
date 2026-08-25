from sttcorrect.llm.base import LLMClient

PROMPT_TEMPLATE = """다음은 강의를 녹음해 전사하고 전문용어를 교정한 텍스트입니다.
구어체 필러와 말버릇만 제거하고, 나머지는 원문을 최대한 그대로 유지해주세요.

지켜야 할 원칙:
- "그러니까", "이제", "음", "-는데요" 같은 구어체 filler와 말버릇만 제거하세요. 그 외의
  단어, 표현, 어순, 문장 구조는 바꾸지 마세요 — 문어체로 "다시 쓰는" 것이 아니라, 불필요한
  군더더기만 걷어내는 최소한의 편집입니다.
- 내용을 요약하거나 생략하지 마세요. 원문에 있는 모든 개념과 설명을 빠짐없이, 원래
  표현 그대로 포함해야 합니다.
- 문단이나 소제목으로 구조를 나누지 마세요. 하나의 연속된 흐름으로 유지하세요.
- 전문용어(영어 표기 포함)는 원문 그대로 유지하세요 — 임의로 다른 표현으로 바꾸지
  마세요.
- 원문에 없는 내용을 추측해서 추가하지 마세요.
- 원문의 순서를 그대로 유지하세요.

원문: {transcript}

정리된 텍스트만 출력하세요."""


def build_organize_prompt(transcript: str) -> str:
    return PROMPT_TEMPLATE.format(transcript=transcript)


def organize_transcript(transcript: str, llm: LLMClient) -> str:
    """build_organize_prompt 후 llm.call_llm 호출. llm은 DI로 주입 —
    correction.py의 correct_with_llm과 동일한 패턴."""
    return llm.call_llm(build_organize_prompt(transcript))
