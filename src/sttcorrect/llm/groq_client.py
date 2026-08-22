import os
import time

import requests
from dotenv import load_dotenv

from sttcorrect.llm.correction import SYSTEM_INSTRUCTION

from sttcorrect.llm.correction import SYSTEM_INSTRUCTION


def _retry_wait_seconds(resp: requests.Response, attempt: int) -> float:
    """429 응답의 Retry-After 헤더를 우선 쓰고, 없으면 지수 백오프(2s, 4s, 8s...)로
    대체한다. 무료 티어의 분당 토큰 한도(TPM)에 실측으로 걸린 적이 있어(용어 186개를
    청크로 나눠 연속 호출할 때) 추가."""
    retry_after = resp.headers.get("retry-after")
    if retry_after is not None:
        try:
            return float(retry_after)
        except ValueError:
            pass
    return float(2 ** (attempt + 1))


class GroqLLMClient:
    """Groq의 OpenAI 호환 chat/completions 엔드포인트(https://api.groq.com/openai/v1)를
    requests로 호출. 팀 통합 LLM으로 교체 시 base_url/model/인증 방식만 바꾸면 되도록
    LLMClient 인터페이스만 구현."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "openai/gpt-oss-120b",
        timeout: float = 60.0,
        max_tokens: int = 4096,
        max_retries: int = 3,
    ) -> None:
        load_dotenv()
        self._api_key = api_key or os.environ["GROQ_API_KEY"]
        self._model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._max_retries = max_retries
        self._base_url = "https://api.groq.com/openai/v1"

    def call_llm(self, prompt: str) -> str:
        # gpt-oss 계열은 추론(reasoning) 모델이라 completion_tokens의 상당 부분을 눈에 안
        # 보이는 사고 과정에 먼저 쓴다 — max_tokens를 명시하지 않으면 API 기본값이
        # 낮아서 긴 응답(예: 용어 186개 발음 JSON)이 중간에 잘리는 걸 실측으로 확인했다
        # (finish_reason="length"). 명시적으로 넉넉히 잡아 이 truncation을 방지한다.
        for attempt in range(self._max_retries + 1):
            resp = requests.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": self._max_tokens,
                },
                timeout=self._timeout,
            )
            # 429(분당 토큰/요청 한도 초과)는 재시도하면 보통 풀린다 — 무료 티어에서
            # 청크 여러 개를 연속 호출할 때 실제로 겪은 상황. 다른 에러는 즉시 올린다.
            if resp.status_code == 429 and attempt < self._max_retries:
                time.sleep(_retry_wait_seconds(resp, attempt))
                continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        raise AssertionError("unreachable")  # for 루프는 return 또는 continue로만 빠져나감
