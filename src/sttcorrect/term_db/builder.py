from pathlib import Path

from sttcorrect.schema import TermDB, TermEntry
from sttcorrect.term_db.collision import CollisionSeed, classify_terms, load_collision_seed
from sttcorrect.term_db.mapping_pairs import extract_mapping_pairs
from sttcorrect.term_db.pdf_extract import extract_and_dedup
from sttcorrect.term_db.term_candidates import (
    ACRONYM_RE,
    ALNUM_MIXED_RE,
    CAPITALIZED_RE,
    extract_candidate_terms,
    filter_function_words,
)


def _source_for_candidate(term: str) -> str:
    """candidate 문자열이 여러 정규식에 동시에 매치될 수 있으므로 acronym > alphanumeric >
    capitalized 순으로 단일 source를 부여한다."""
    if ACRONYM_RE.fullmatch(term):
        return "acronym"
    if ALNUM_MIXED_RE.fullmatch(term):
        return "alphanumeric"
    return "capitalized"


def _build_term_db_from_text(text: str, topic: str | None, seed_path: str) -> TermDB:
    """build_term_db의 2~6단계(PDF 텍스트를 이미 확보한 이후의 로직)를 순수 함수로 분리.
    build_term_dbs가 extract_and_dedup을 한 번만 호출해 영어/한국어 DB를 함께 빌드할 수
    있도록 하기 위함."""
    candidates = filter_function_words(extract_candidate_terms(text))
    pairs = extract_mapping_pairs(text)

    entries_by_term: dict[str, TermEntry] = {
        term: TermEntry(
            term=term,
            korean_variants=[],
            collision_label="safe",  # placeholder — classify_terms가 아래에서 재할당
            source=_source_for_candidate(term),
        )
        for term in candidates
    }

    for english_term, korean_variant in pairs:
        existing = entries_by_term.get(english_term)
        if existing is not None:
            if korean_variant not in existing.korean_variants:
                entries_by_term[english_term] = existing.model_copy(
                    update={"korean_variants": existing.korean_variants + [korean_variant]}
                )
        else:
            entries_by_term[english_term] = TermEntry(
                term=english_term,
                korean_variants=[korean_variant],
                collision_label="safe",
                source="mapping_pair",
            )

    seed = load_collision_seed(seed_path)
    classified_entries = classify_terms(list(entries_by_term.values()), seed)
    return TermDB(topic=topic, entries=classified_entries)


def build_term_db(
    pdf_path: str,
    topic: str | None = None,
    seed_path: str = "config/seed_collision_terms.yaml",
) -> TermDB:
    text = extract_and_dedup(pdf_path)
    return _build_term_db_from_text(text, topic, seed_path)


def merge_term_dbs(dbs: list[TermDB], seed: CollisionSeed) -> TermDB:
    """여러 TermDB를 하나로 누적 병합한다 (build_term_db의 entries_by_term 병합 방식과
    동일하게 term 문자열 정확 일치 기준).
    1. entries_by_term: dict[str, TermEntry]를 dbs 순서대로 채운다.
       - 처음 보는 term: 그대로 등록
       - 이미 등록된 term: korean_variants를 순서 보존 + 중복 제거로 union하고,
         source는 먼저 등록된 db의 값을 그대로 유지한다 (source는 참고용 메타데이터일 뿐
         classify_term 결과에는 영향을 주지 않는다)
    2. 병합이 끝난 뒤 classify_terms(entries, seed)를 다시 실행해 collision_label을
       재계산한다 (korean_variants가 늘어나면서 safe였던 라벨이 collision으로 바뀔 수 있음)
    3. topic은 dbs를 순서대로 스캔하며 None이 아닌 마지막 값을 최종값으로 채택한다
       (새 빌드에서 --topic을 생략하면 기존 topic이 유지되고, 지정하면 덮어쓴다)
    4. TermDB(topic=merged_topic, entries=...) 반환. course_id는 스키마상 존재하지만
       현재 어디서도 쓰이지 않으므로 병합 로직에서 다루지 않는다.
    """
    entries_by_term: dict[str, TermEntry] = {}
    merged_topic: str | None = None

    for db in dbs:
        if db.topic is not None:
            merged_topic = db.topic
        for entry in db.entries:
            existing = entries_by_term.get(entry.term)
            if existing is None:
                entries_by_term[entry.term] = entry
                continue
            merged_variants = list(existing.korean_variants)
            for variant in entry.korean_variants:
                if variant not in merged_variants:
                    merged_variants.append(variant)
            entries_by_term[entry.term] = existing.model_copy(
                update={"korean_variants": merged_variants}
            )

    reclassified = classify_terms(list(entries_by_term.values()), seed)
    return TermDB(topic=merged_topic, entries=reclassified)


def save_term_db(term_db: TermDB, out_path: str) -> None:
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(term_db.model_dump_json(ensure_ascii=False, indent=2), encoding="utf-8")


def load_term_db(path: str) -> TermDB:
    return TermDB.model_validate_json(Path(path).read_text(encoding="utf-8"))
