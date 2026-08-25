from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from backend.app.database import get_session
from backend.app.models import LearningObjective


def load_rubrics() -> list[dict]:
    rubric_dir = ROOT / "data" / "evaluation" / "rubrics"
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(rubric_dir.glob("*.json"))]


def seed_learning_objectives() -> tuple[int, int]:
    created_parents = 0
    created_children = 0

    with get_session() as db:
        for rubric in load_rubrics():
            lecture_id = rubric["lecture_id"]
            for order, objective in enumerate(rubric["top_level_objectives"], start=1):
                parent = db.scalar(
                    select(LearningObjective).where(
                        LearningObjective.lecture_id == lecture_id,
                        LearningObjective.parent_id.is_(None),
                        LearningObjective.rag_objective_id == objective["objective_id"],
                    )
                )
                if parent is None:
                    parent = LearningObjective(
                        lecture_id=lecture_id,
                        rag_objective_id=objective["objective_id"],
                        title=objective["title"],
                        description=objective.get("description"),
                        level="parent",
                        importance=3,
                        display_order=order,
                        is_active=True,
                    )
                    db.add(parent)
                    db.flush()
                    created_parents += 1
                else:
                    parent.title = objective["title"]
                    parent.description = objective.get("description")
                    parent.display_order = order
                    parent.is_active = True

                for child_order, sub_objective in enumerate(objective["sub_objectives"], start=1):
                    child = db.scalar(
                        select(LearningObjective).where(
                            LearningObjective.parent_id == parent.id,
                            LearningObjective.title == sub_objective["title"],
                        )
                    )
                    if child is None:
                        db.add(
                            LearningObjective(
                                lecture_id=lecture_id,
                                parent_id=parent.id,
                                title=sub_objective["title"],
                                level="child",
                                importance=3,
                                display_order=child_order,
                                is_active=True,
                            )
                        )
                        created_children += 1
                    else:
                        child.display_order = child_order
                        child.is_active = True
        db.commit()

    return created_parents, created_children


if __name__ == "__main__":
    parents, children = seed_learning_objectives()
    print(f"완료: 상위 학습목표 {parents}개, 하위 학습목표 {children}개를 새로 추가했습니다.")
