from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation import load_rubric  # noqa: E402
from src.evaluation_schemas import LectureRubric, TopicAssessment  # noqa: E402
from src.schemas import LectureDocument  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rubric과 evidence 연결을 검증합니다.")
    parser.add_argument("--write-schemas", action="store_true", help="JSON Schema도 갱신합니다.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evaluation_dir = ROOT / "data" / "evaluation"
    rubric_dir = evaluation_dir / "rubrics"
    paths = sorted(rubric_dir.glob("*.json"))
    if not paths:
        raise SystemExit("Rubric JSON이 없습니다.")

    for path in paths:
        rubric = load_rubric(path)
        processed_path = ROOT / "data" / "processed" / f"{rubric.lecture_id}.json"
        processed = json.loads(processed_path.read_text(encoding="utf-8"))
        document = LectureDocument.model_validate(processed)
        chunks = {chunk["chunk_id"]: chunk for chunk in processed["chunks"]}
        term_ids = {term.term_id for term in document.terminology}
        if len(term_ids) != len(document.terminology):
            raise ValueError(f"{rubric.lecture_id}: terminology term_id 중복")

        if document.schema_version == "2.1.0":
            aliases: dict[str, str] = {}
            for term in document.terminology:
                for related_id in term.not_equivalent_to:
                    if related_id not in term_ids:
                        raise ValueError(f"{term.term_id}: 없는 not_equivalent_to {related_id}")
                forms = [
                    term.canonical_ko,
                    term.canonical_en,
                    *term.abbreviations,
                    *term.accepted_aliases,
                ]
                for form in forms:
                    key = " ".join(form.casefold().split())
                    if not key:
                        continue
                    previous = aliases.get(key)
                    if previous is not None and previous != term.term_id:
                        raise ValueError(
                            f"terminology alias 충돌: {form!r} -> {previous}, {term.term_id}"
                        )
                    aliases[key] = term.term_id

            unit_ids: set[str] = set()
            for chunk in document.chunks:
                unknown_terms = set(chunk.term_ids) - term_ids
                if unknown_terms:
                    raise ValueError(f"{chunk.chunk_id}: 없는 term_id {sorted(unknown_terms)}")
                if chunk.page_role in {
                    "cover", "table_of_contents", "section_divider", "closing"
                } and chunk.evidence_units:
                    raise ValueError(f"{chunk.chunk_id}: {chunk.page_role} 페이지는 evidence가 될 수 없습니다.")
                for unit in chunk.evidence_units:
                    if unit.unit_id in unit_ids:
                        raise ValueError(f"evidence unit_id 중복: {unit.unit_id}")
                    unit_ids.add(unit.unit_id)
                    unknown_unit_terms = set(unit.term_ids) - term_ids
                    if unknown_unit_terms:
                        raise ValueError(f"{unit.unit_id}: 없는 term_id {sorted(unknown_unit_terms)}")

        for objective in rubric.top_level_objectives:
            for sub in objective.sub_objectives:
                for claim in sub.claims:
                    unknown_claim_terms = set(claim.term_ids) - term_ids
                    if unknown_claim_terms:
                        raise ValueError(f"{claim.claim_id}: 없는 term_id {sorted(unknown_claim_terms)}")
                    for evidence in claim.evidence:
                        chunk = chunks.get(evidence.chunk_id)
                        if chunk is None:
                            raise ValueError(f"{claim.claim_id}: 없는 chunk {evidence.chunk_id}")
                        if chunk["page"] != evidence.page:
                            raise ValueError(f"{claim.claim_id}: evidence page 불일치")
                        if document.schema_version == "2.1.0":
                            if evidence.unit_id is None:
                                raise ValueError(f"{claim.claim_id}: unit_id가 필요합니다.")
                            unit = next(
                                (
                                    item
                                    for item in chunk.get("evidence_units", [])
                                    if item["unit_id"] == evidence.unit_id
                                ),
                                None,
                            )
                            if unit is None:
                                raise ValueError(f"{claim.claim_id}: 없는 unit {evidence.unit_id}")
                            if unit["source_excerpt"] != evidence.source_excerpt:
                                raise ValueError(f"{claim.claim_id}: atomic source_excerpt 불일치")
                            if unit["source_status"] != evidence.source_status:
                                raise ValueError(f"{claim.claim_id}: source_status 불일치")
                            if evidence.source_status != "verified":
                                raise ValueError(f"{claim.claim_id}: 검수되지 않은 evidence 사용")
                        elif chunk["content"] != evidence.source_excerpt:
                            raise ValueError(f"{claim.claim_id}: source_excerpt 불일치")
        print(
            f"OK {rubric.lecture_id}: objectives={len(rubric.top_level_objectives)}, "
            f"claims={sum(len(sub.claims) for obj in rubric.top_level_objectives for sub in obj.sub_objectives)}"
        )

    if args.write_schemas:
        targets = {
            "rubric.schema.json": LectureRubric.model_json_schema(),
            "topic_assessment.schema.json": TopicAssessment.model_json_schema(),
            "../processed/processed.schema.json": LectureDocument.model_json_schema(),
        }
        for filename, schema in targets.items():
            (evaluation_dir / filename).write_text(
                json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()
