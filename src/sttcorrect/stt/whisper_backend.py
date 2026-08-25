from dataclasses import dataclass
from pathlib import Path


@dataclass
class SttConfig:
    model_size: str = "medium"
    device: str = "cpu"
    compute_type: str = "int8"
    cpu_threads: int = 4
    language: str = "ko"
    vad_filter: bool = True
    condition_on_previous_text: bool = False
    beam_size: int = 5


class WhisperSttBackend:
    def __init__(self, config: SttConfig | None = None) -> None:
        self._config = config or SttConfig()
        self._model = None  # lazy load — 생성/임포트 시점에 모델 로드 금지

    def _load_model(self):
        from faster_whisper import WhisperModel

        if self._model is None:
            self._model = WhisperModel(
                self._config.model_size,
                device=self._config.device,
                compute_type=self._config.compute_type,
                cpu_threads=self._config.cpu_threads,
            )
        return self._model

    def transcribe(
        self,
        wav_path: str | Path,
        initial_prompt: str | None = None,
        hotwords: str | None = None,
    ) -> str:
        """명세 5절의 파라미터 그대로 model.transcribe 호출, segment.text를 이어붙여 반환"""
        model = self._load_model()
        segments, _info = model.transcribe(
            str(wav_path),
            language=self._config.language,
            vad_filter=self._config.vad_filter,
            initial_prompt=initial_prompt,
            hotwords=hotwords,
            condition_on_previous_text=self._config.condition_on_previous_text,
            beam_size=self._config.beam_size,
        )
        return " ".join(seg.text.strip() for seg in segments)
