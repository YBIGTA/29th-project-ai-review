import re

from sttcorrect.llm.base import LLMClient
from sttcorrect.schema import TermDBUsed

SYSTEM_INSTRUCTION = """당신은 STT 표기 오류만 보정하는 편집기입니다.
사용자의 지식, 주장, 오개념을 평가하거나 정정하지 마세요.
사실관계, 개념 정의, 인과관계, 수치, 예시, 결론은 원문이 틀렸더라도 그대로 유지하세요.
확실한 음성 인식 오류가 아니면 원문 표현을 바꾸지 마세요."""

PROMPT_TEMPLATE = """다음은 한국어 STT로 전사된 텍스트입니다. 아래 용어 목록을 참고해
발음이 잘못 인식된 부분을 자연스럽게 교정하세요. 문장 구조는 바꾸지 마세요.
원문의 내용을 임의로 생략하거나 지어내지 마세요 — 알아듣기 어려운 부분이라도 반드시
원문 그대로 유지하고, 실제 원문에 없는 단어(예: 이름, 값)를 추측해서 채워 넣지 마세요.
아래 용어 목록에 있는 단어가 한글 발음으로 잘못 전사되어 나타난 경우에만, 그 발음과
가장 가깝게 대응되는 영어 원어 표기로 복원하세요 (예: "포린키" -> "Foreign Key",
"트랜젝션" -> "Transaction"). 원문에 이미 올바른 한국어 표현(예: "무결성", "데이터베이스"
같은 정상 한국어 단어/외래어)이 쓰인 경우는 절대 영어로 바꾸지 말고 그대로 두세요.
발음이 여러 용어와 비슷해 보여도 실제로 들린 발음과 가장 가까운 것 하나만 고르고,
다른 용어로 착각해서 바꾸지 마세요.

일반 용어: {safe_terms}
※ 아래 단어는 한국어 문법요소/일상어와 발음이 겹칠 수 있어 문맥을 보고 신중히 판단하세요: {risky_terms}

원본 전사: {transcript}
교정된 텍스트만 출력하세요."""

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# gpt-oss 계열은 추론 모델이라 completion_tokens의 상당 부분(실측: 4분 분량 강의
# 보정 요청 시 79%)을 눈에 안 보이는 사고 과정에 먼저 쓴다. 전사본을 통째로 한
# 번에 보정 요청하면 남는 예산이 출력 길이를 못 따라가 응답이 잘리거나
# (finish_reason="length") 빈 문자열로 돌아오는 걸 실측으로 확인했다 —
# pronunciation.py의 청크 분할과 같은 원인·같은 해법이라 문장 단위로 나눠 호출한다.
_CHUNK_CHAR_LIMIT = 600


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


def _split_into_chunks(transcript: str, limit: int) -> list[str]:
    """문장 경계(.!?)에서만 나눠 청크를 만든다 — 문장 중간이 잘리지 않게 하기
    위함. 문장 하나가 limit보다 길어도 쪼개지 않고 그대로 한 청크로 둔다
    (내용 보존이 우선이라 강제로 자르지 않음)."""
    sentences = _SENTENCE_SPLIT_RE.split(transcript.strip())
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        if current and current_len + len(sentence) > limit:
            chunks.append(" ".join(current))
            current = []
            current_len = 0
        current.append(sentence)
        current_len += len(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks


def correct_with_llm(transcript: str, term_db_used: TermDBUsed, llm: LLMClient) -> str:
    """긴 전사본을 문장 단위 청크로 나눠 각각 보정 후 이어붙인다 — 한 번에
    통째로 보내면 추론 모델의 completion 토큰 예산을 넘어 잘리는 문제(실측
    확인)를 피하기 위함. llm은 DI로 주입 — 파이프라인/테스트가 실제 백엔드
    없이 Fake를 넣을 수 있게 함.
    청크 하나의 보정 응답이 비어있으면(예: 그 호출만 토큰 예산을 넘어 실패)
    내용을 잃지 않도록 원문 청크를 그대로 사용한다."""
    chunks = _split_into_chunks(transcript, _CHUNK_CHAR_LIMIT)
    corrected = []
    for chunk in chunks:
        result = llm.call_llm(build_correction_prompt(chunk, term_db_used))
        corrected.append(result if result.strip() else chunk)
    return " ".join(corrected)
