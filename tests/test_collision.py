from pathlib import Path

from sttcorrect.schema import TermEntry
from sttcorrect.term_db.collision import CollisionSeed, classify_term, classify_terms, load_collision_seed

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = REPO_ROOT / "config" / "seed_collision_terms.yaml"


def test_load_collision_seed_normalizes_known_terms_keys_to_lowercase():
    seed = load_collision_seed(str(SEED_PATH))
    # YAML 원본 키는 "Row"지만 조회는 소문자로 하므로 소문자 키로 정규화돼 있어야 한다.
    assert "row" in seed.known_terms
    assert seed.known_terms["row"]["label"] == "particle_collision"


def test_classify_term_curated_table_has_top_priority():
    seed = load_collision_seed(str(SEED_PATH))
    assert classify_term("Row", seed) == "particle_collision"
    assert classify_term("row", seed) == "particle_collision"
    assert classify_term("ROW", seed) == "particle_collision"
    assert classify_term("Key", seed) == "content_word_collision"
    assert classify_term("Set", seed) == "content_word_collision"


def test_classify_term_curated_wins_even_if_observed_variant_suggests_otherwise():
    seed = CollisionSeed(
        particles=["로"],
        content_word_homophones=["키"],
        known_terms={"widget": {"korean": "위젯", "label": "safe"}},
    )
    # korean_variants가 particles에 걸리더라도 curated known_terms가 있으면 그 값이 우선한다.
    assert classify_term("Widget", seed, korean_variants=["로"]) == "safe"


def test_classify_term_uses_observed_korean_variants_when_not_curated():
    seed = CollisionSeed(particles=["로"], content_word_homophones=["키"], known_terms={})
    assert classify_term("Something", seed, korean_variants=["로"]) == "particle_collision"
    assert classify_term("Cache", seed, korean_variants=["키"]) == "content_word_collision"
    assert classify_term("RDBMS", seed, korean_variants=["알디비엠에스"]) == "safe"


def test_classify_term_falls_back_to_transliteration_guess():
    # "row"의 음차 추정("로우")을 이 테스트용 seed의 content_word_homophones에 넣어
    # curated/관찰값 둘 다 없을 때만 3단계 fallback이 동작하는지 확인한다.
    seed = CollisionSeed(particles=["가"], content_word_homophones=["로우"], known_terms={})
    assert classify_term("Row", seed) == "content_word_collision"


def test_classify_term_transliteration_guess_with_no_match_falls_to_safe():
    seed = CollisionSeed(particles=["가"], content_word_homophones=["나"], known_terms={})
    # "two" -> "투" 로 추정되지만 seed 어디에도 걸리지 않음
    assert classify_term("Two", seed) == "safe"


def test_classify_term_default_safe_when_everything_fails():
    seed = CollisionSeed(particles=["가"], content_word_homophones=["나"], known_terms={})
    # "Transaction"은 curated에도 없고, 관찰값도 없고, 음차 추정 테이블에도 없다 (None 반환)
    assert classify_term("Transaction", seed) == "safe"


def test_classify_terms_applies_label_to_each_entry_without_mutating_other_fields():
    seed = load_collision_seed(str(SEED_PATH))
    entries = [
        TermEntry(term="RDBMS", collision_label="safe", source="acronym"),
        TermEntry(term="Row", korean_variants=["로우"], collision_label="safe", source="capitalized"),
        TermEntry(term="Key", collision_label="safe", source="capitalized"),
    ]
    classified = classify_terms(entries, seed)
    labels = {e.term: e.collision_label for e in classified}
    assert labels == {
        "RDBMS": "safe",
        "Row": "particle_collision",
        "Key": "content_word_collision",
    }
    # source/korean_variants는 그대로 보존
    row_entry = next(e for e in classified if e.term == "Row")
    assert row_entry.korean_variants == ["로우"]
    assert row_entry.source == "capitalized"
