from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation import (  # noqa: E402
    load_profile,
    load_rubric,
    validate_profile_against_rubric,
)


def main() -> int:
    processed_dir = PROJECT_ROOT / "data" / "processed"
    rubric_dir = PROJECT_ROOT / "data" / "evaluation" / "rubrics"
    profile_dir = PROJECT_ROOT / "data" / "evaluation" / "profiles"
    errors: list[str] = []

    for rubric_path in sorted(rubric_dir.glob("*.json")):
        rubric = load_rubric(rubric_path)
        lecture_path = processed_dir / f"{rubric.lecture_id}.json"
        if not lecture_path.exists():
            errors.append(f"{rubric_path.name}: 구조화 강의 파일이 없습니다.")
            continue

        lecture = json.loads(lecture_path.read_text(encoding="utf-8"))
        chunks = {chunk["chunk_id"]: chunk for chunk in lecture["chunks"]}
        evidence_items = [
            evidence
            for objective in rubric.learning_objectives
            for claim in objective.reference_claims
            for evidence in claim.evidence
        ] + [
            evidence for relation in rubric.relations for evidence in relation.evidence
        ]

        for evidence in evidence_items:
            chunk = chunks.get(evidence.chunk_id)
            if chunk is None:
                errors.append(
                    f"{rubric_path.name}: 없는 chunk_id {evidence.chunk_id}"
                )
            elif chunk["page"] != evidence.page:
                errors.append(
                    f"{rubric_path.name}: {evidence.chunk_id} 페이지 불일치 "
                    f"({evidence.page} != {chunk['page']})"
                )

        print(
            f"OK {rubric.lecture_id}: "
            f"objectives={len(rubric.learning_objectives)}, "
            f"claims={sum(len(x.reference_claims) for x in rubric.learning_objectives)}, "
            f"relations={len(rubric.relations)}, "
            f"chains={len(rubric.relation_chains)}"
        )

    rubrics = {
        path.stem: load_rubric(path) for path in sorted(rubric_dir.glob("*.json"))
    }
    for profile_path in sorted(profile_dir.glob("*.json")):
        profile = load_profile(profile_path)
        rubric = rubrics.get(profile.lecture_id)
        if rubric is None:
            errors.append(
                f"{profile_path.name}: lecture rubric이 없습니다: {profile.lecture_id}"
            )
            continue
        try:
            validate_profile_against_rubric(profile, rubric)
        except ValueError as exc:
            errors.append(f"{profile_path.name}: {exc}")
        else:
            expected_objectives = sum(
                group.minimum_objectives for group in profile.objective_groups
            )
            expected_relations = sum(
                group.minimum_relations for group in profile.relation_groups
            )
            print(
                f"OK {profile.profile_id}: "
                f"expected_objectives={expected_objectives}, "
                f"expected_relations={expected_relations}, "
                f"max_seconds={profile.max_seconds}"
            )

    if errors:
        print("\n검증 오류:")
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
