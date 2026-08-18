from typing import Protocol


class LLMClient(Protocol):
    def call_llm(self, prompt: str) -> str: ...
