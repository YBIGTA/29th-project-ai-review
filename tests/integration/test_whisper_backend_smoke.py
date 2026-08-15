from pathlib import Path

import pytest

from sttcorrect.stt.whisper_backend import WhisperSttBackend

SAMPLE_WAV = Path(__file__).resolve().parent.parent.parent / "data" / "samples" / "sample.wav"


@pytest.mark.skipif(
    not SAMPLE_WAV.exists(),
    reason="실제 샘플 오디오(data/samples/sample.wav)가 없어 스킵 — 향후 절차 2번(모델 크기/속도 실측)용",
)
def test_transcribe_real_sample_audio():
    backend = WhisperSttBackend()
    text = backend.transcribe(str(SAMPLE_WAV))
    assert isinstance(text, str)
    assert len(text) > 0
