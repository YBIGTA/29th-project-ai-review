import os

import requests
from dotenv import load_dotenv


class GroqLLMClient:
    """Groq의 OpenAI 호환 chat/completions 엔드포인트(https://api.groq.com/openai/v1)를
    requests로 호출. 팀 통합 LLM으로 교체 시 base_url/model/인증 방식만 바꾸면 되도록
    LLMClient 인터페이스만 구현."""

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float = 60.0) -> None:
        load_dotenv()
        self._api_key = api_key or os.environ["GROQ_API_KEY"]
        self._model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self._timeout = timeout
        self._base_url = "https://api.groq.com/openai/v1"

    def call_llm(self, prompt: str) -> str:
        resp = requests.post(
            f"{self._base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
