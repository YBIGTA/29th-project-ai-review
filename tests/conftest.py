import pytest


class FakeSttBackend:
    """WhisperSttBackend와 동일한 transcribe(wav_path, initial_prompt, hotwords) 시그니처를
    갖는 테스트용 더미. 실제 모델 로드 없이 고정된 텍스트를 반환하고 받은 인자를 기록한다."""

    def __init__(self, response: str = "STT 원본 결과") -> None:
        self.response = response
        self.last_call: dict | None = None

    def transcribe(self, wav_path, initial_prompt=None, hotwords=None) -> str:
        self.last_call = {
            "wav_path": wav_path,
            "initial_prompt": initial_prompt,
            "hotwords": hotwords,
        }
        return self.response


@pytest.fixture
def fake_stt_backend() -> FakeSttBackend:
    return FakeSttBackend()


class FakeLLMClient:
    """LLMClient Protocol을 만족하는 테스트용 더미. 실제 API 호출 없이 고정된 응답이나
    마지막으로 받은 prompt를 기록한다. 2-pass 보정(한국어 DB pass + 영어 DB pass)처럼
    call_llm이 한 세션에서 여러 번 호출될 수 있는 경우를 검증하기 위해 responses로
    호출 순서별 응답을 지정하고 prompts로 전체 호출 이력을 조회할 수 있다."""

    def __init__(self, response: str = "corrected transcript", responses: list[str] | None = None) -> None:
        self.response = response
        self._responses = responses
        self.last_prompt: str | None = None
        self.prompts: list[str] = []

    def call_llm(self, prompt: str) -> str:
        self.last_prompt = prompt
        self.prompts.append(prompt)
        if self._responses is not None:
            idx = min(len(self.prompts) - 1, len(self._responses) - 1)
            return self._responses[idx]
        return self.response


@pytest.fixture
def fake_llm_client() -> FakeLLMClient:
    return FakeLLMClient()
