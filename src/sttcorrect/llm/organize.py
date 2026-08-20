from sttcorrect.llm.base import LLMClient

PROMPT_TEMPLATE = """다음은 강의를 녹음해 전사하고 전문용어를 교정한 텍스트입니다.
구어체로 되어 있는 이 내용을 의미와 맥락은 그대로 유지한 채, 기술 문서/강의 노트처럼
정리된 문어체로 다시 써주세요.

지켜야 할 원칙:
- 내용을 요약하거나 생략하지 마세요. 원문에 있는 모든 개념과 설명을 빠짐없이 포함해야
  합니다 — 압축된 요약이 아니라, 같은 내용을 더 읽기 좋은 형태로 정리하는 작업입니다.
- "그러니까", "이제", "음" 같은 구어체 filler와 말버릇은 제거하되, 실제 설명 내용은
  그대로 보존하세요.
- 전문용어(영어 표기 포함)는 원문 그대로 유지하세요 — 임의로 다른 표현으로 바꾸지
  마세요.
- 원문에 없는 내용을 추측해서 추가하지 마세요.
- 필요하면 문단이나 소제목으로 구조를 나눠도 좋지만, 원문의 논리적 순서는 유지하세요.

원문: {transcript}

정리된 텍스트만 출력하세요."""


def build_organize_prompt(transcript: str) -> str:
    return PROMPT_TEMPLATE.format(transcript=transcript)


def organize_transcript(transcript: str, llm: LLMClient) -> str:
    """build_organize_prompt 후 llm.call_llm 호출. llm은 DI로 주입 —
    correction.py의 correct_with_llm과 동일한 패턴."""
    return llm.call_llm(build_organize_prompt(transcript))
