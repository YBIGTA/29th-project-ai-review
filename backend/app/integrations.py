from __future__ import annotations

from typing import TypedDict

class EvaluationResult(TypedDict):
    quantitative: dict[str, object]
    qualitative: dict[str, list[str]]


def mock_evaluation(transcript: str) -> EvaluationResult:
    del transcript
    return {
        "quantitative": {
            "concept_recall": 0.72,
            "concept_precision": 0.84,
            "concept_f1": 0.77,
            "scores": {
                "accuracy": {"score": 32, "max_score": 40, "rubric_level": 3, "reason": "핵심 개념을 대체로 정확하게 설명했습니다."},
                "coverage": {"score": 29, "max_score": 40, "rubric_level": 3, "reason": "주요 주제를 다루었지만 일부 개념이 누락되었습니다."},
                "structural_understanding": {"score": 14, "max_score": 20, "rubric_level": 3, "reason": "개념 간 관계를 대체로 일관되게 설명했습니다."}
            },
            "total": {"score": 75, "max_score": 100, "rubric_level": 3, "reason": "세 평가 영역을 종합한 Mock 결과입니다."}
        },
        "qualitative": {
            "missing_concepts": ["세부 근거와 예시"],
            "incorrect_concepts": [],
            "misconnected_concepts": [],
            "review_suggestions": ["핵심 개념 사이의 관계를 한 문장씩 설명해 보세요."]
        }
    }
