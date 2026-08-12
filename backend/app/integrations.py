from __future__ import annotations

from pathlib import Path
from typing import TypedDict


class EvaluationResult(TypedDict):
    score: int
    summary: str
    strengths: list[str]
    missing_points: list[str]
    suggestions: list[str]


def run_stt(audio_path: str) -> str:
    """STT integration contract for the Faster-Whisper implementation."""
    raise NotImplementedError(
        "Connect the STT team's run_stt(audio_path: str) -> str implementation."
    )


def evaluate_speech(transcript: str, pdf_path: str) -> EvaluationResult:
    """RAG/LLM evaluation contract for the material-aware review."""
    raise NotImplementedError(
        "Connect the RAG team's evaluate_speech(transcript, pdf_path) implementation."
    )


def mock_review(pdf_path: Path, audio_path: Path) -> tuple[str, EvaluationResult]:
    """Return deterministic-shaped data while STT/RAG integrations are pending."""
    del pdf_path, audio_path
    return (
        "[Mock transcript] 업로드된 학습 자료를 기준으로 한 테스트 전사입니다.",
        {
            "score": 78,
            "summary": "Mock 평가가 정상적으로 생성되었습니다.",
            "strengths": ["핵심 주제를 언급했습니다."],
            "missing_points": ["세부 근거와 예시가 아직 반영되지 않았습니다."],
            "suggestions": ["핵심 개념 사이의 관계를 한 문장씩 설명해 보세요."],
        },
    )
