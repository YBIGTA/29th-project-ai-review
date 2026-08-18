import sys

from sttcorrect.stt.whisper_backend import SttConfig, WhisperSttBackend


def test_construction_does_not_load_model():
    backend = WhisperSttBackend()
    assert backend._model is None


def test_construction_does_not_import_faster_whisper():
    sys.modules.pop("faster_whisper", None)
    WhisperSttBackend(SttConfig(model_size="small"))
    assert "faster_whisper" not in sys.modules
