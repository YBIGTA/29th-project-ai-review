import json
import re

from sttcorrect.llm.base import LLMClient

_PROMPT_TEMPLATE = (
    "다음은 데이터베이스(DB) 강의에서 등장하는 영어 전문용어 목록입니다. "
    "각 용어가 강의에서 어떻게 한국어로 발음/음차되는지 알려주세요.\n\n"
    "용어 목록: {term_list}\n\n"
    "반드시 아래 JSON 형식으로만 답하세요. 목록에 있는 용어에 대해서만 답하고, "
    "용어를 추가하거나 생략하지 마세요. 다른 설명은 출력하지 마세요.\n"
    '{{"용어1": "한글발음1", "용어2": "한글발음2"}}'
)

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)

# 한 번에 너무 많은 용어를 요청하면 응답이 중간에 잘린다 — gpt-oss 계열은 추론
# 모델이라 completion 토큰의 상당 부분을 눈에 안 보이는 사고 과정에 먼저 쓰고,
# 실제 JSON 본문은 나머지 예산으로 작성한다. 실측 결과 186개를 한 번에 요청하면
# finish_reason="length"로 잘렸지만(추론에 1812/3072 토큰 소모), 40개씩 나누면
# 매번 완결된 JSON으로 끝났다. 과목이 커져도(여러 주차 --merge) 안전하도록 나눈다.
_CHUNK_SIZE = 40


def build_pronunciation_prompt(terms: list[str]) -> str:
    return _PROMPT_TEMPLATE.format(term_list=", ".join(terms))


def _strip_code_fence(text: str) -> str:
    return _CODE_FENCE_RE.sub("", text).strip()


def _parse_response(response: str, terms: list[str]) -> dict[str, str]:
    """한 청크 분량 응답을 파싱한다. Grounding: 응답 키를 대소문자 무시하고 그
    청크의 입력 목록과 대조해, 일치하는 것만 입력의 canonical 표기(대소문자)로
    반환한다 — LLM이 "DROP"을 "DROp"처럼 대소문자 오타로 반환해도 구제되면서,
    목록에 아예 없는 용어를 지어내는 건 여전히 걸러진다. 파싱 실패/형식 이상 시
    빈 dict 반환 (호출측은 해당 용어의 korean_variants를 비운 채로 두고, 기존
    seed/fallback 분류 로직이 이어받는다 — 크래시하지 않음)."""
    try:
        raw = json.loads(_strip_code_fence(response))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    canonical_by_lower = {term.lower(): term for term in terms}
    result: dict[str, str] = {}
    for term, pronunciation in raw.items():
        if not isinstance(term, str) or not isinstance(pronunciation, str):
            continue
        canonical = canonical_by_lower.get(term.lower())
        pronunciation = pronunciation.strip()
        if canonical is not None and pronunciation:
            result[canonical] = pronunciation
    return result


def generate_pronunciations(terms: list[str], llm: LLMClient) -> dict[str, str]:
    """후보 용어 리스트를 _CHUNK_SIZE개씩 나눠 LLM에 전달해 한국어 발음을 생성한다.
    청크 하나가 통째로 실패해도(파싱 실패 등) 나머지 청크는 정상 처리된다."""
    result: dict[str, str] = {}
    for i in range(0, len(terms), _CHUNK_SIZE):
        chunk = terms[i : i + _CHUNK_SIZE]
        response = llm.call_llm(build_pronunciation_prompt(chunk))
        result.update(_parse_response(response, chunk))
    return result
