from __future__ import annotations

from typing import TypedDict

class EvaluationResult(TypedDict):
    score: int
    summary: str
    strengths: list[str]
    missing_points: list[str]
    suggestions: list[str]


def mock_evaluation(transcript: str) -> EvaluationResult:
    del transcript
    return {"score": 78, "summary": "Mock 평가가 정상적으로 생성되었습니다.", "strengths": ["핵심 주제를 언급했습니다."], "missing_points": ["세부 근거와 예시가 아직 반영되지 않았습니다."], "suggestions": ["핵심 개념 사이의 관계를 한 문장씩 설명해 보세요."]}
