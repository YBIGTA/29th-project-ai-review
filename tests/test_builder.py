from pathlib import Path

from sttcorrect.schema import TermDB
from sttcorrect.term_db import builder
from sttcorrect.term_db.collision import CollisionSeed

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = REPO_ROOT / "config" / "seed_collision_terms.yaml"

SAMPLE_TEXT = (
    "The RDBMS(알디비엠에스)를 구성하는 핵심 개념은 Table과 Row이다. "
    "Row - 로우, 각 행을 의미한다. "
    "Neo4j 는 그래프 DB의 예시이다."
)


def test_build_term_db_merges_candidates_with_mapping_pairs(monkeypatch):
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: SAMPLE_TEXT)

    term_db = builder.build_term_db("dummy.pdf", topic="DB", seed_path=str(SEED_PATH))
    entries_by_term = {e.term: e for e in term_db.entries}

    # candidate + mapping-pair 병합: RDBMS는 candidate로도, 괄호 병기로도 등장 -> 하나로 합쳐지고
    # korean_variants에 "알디비엠에스"가 부착돼야 한다.
    assert "RDBMS" in entries_by_term
    assert "알디비엠에스" in entries_by_term["RDBMS"].korean_variants
    assert entries_by_term["RDBMS"].source == "acronym"

    # Row는 candidate + dash 병기 두 군데서 관찰되고, curated 테이블에 의해 particle_collision
    assert "로우" in entries_by_term["Row"].korean_variants
    assert entries_by_term["Row"].collision_label == "particle_collision"

    # Neo4j는 alphanumeric candidate로만 존재 (병기 없음)
    assert entries_by_term["Neo4j"].source == "alphanumeric"
    assert entries_by_term["Neo4j"].korean_variants == []

    assert term_db.topic == "DB"


def test_build_term_db_creates_mapping_pair_only_entry(monkeypatch):
    # candidate 정규식으로는 안 걸리는 소문자 영어 용어가 괄호 병기에만 등장하는 경우
    text = "hello world(헬로월드)는 예시 문장이다."
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: text)

    term_db = builder.build_term_db("dummy.pdf", seed_path=str(SEED_PATH))
    entries_by_term = {e.term: e for e in term_db.entries}
    assert "world" in entries_by_term
    assert entries_by_term["world"].source == "mapping_pair"
    assert entries_by_term["world"].korean_variants == ["헬로월드"]


def test_save_and_load_term_db_roundtrip(tmp_path):
    term_db = TermDB.model_validate(
        {
            "topic": "DB",
            "entries": [
                {"term": "RDBMS", "collision_label": "safe", "source": "acronym"},
                {
                    "term": "Row",
                    "korean_variants": ["로우"],
                    "collision_label": "particle_collision",
                    "source": "capitalized",
                },
            ],
        }
    )
    out_path = tmp_path / "term_db.json"
    builder.save_term_db(term_db, str(out_path))

    loaded = builder.load_term_db(str(out_path))
    assert loaded == term_db


def test_merge_term_dbs_reclassifies_after_unioning_variants():
    seed = CollisionSeed(particles=["로"], content_word_homophones=["키"], known_terms={})
    db1 = TermDB.model_validate(
        {
            "topic": "DB",
            "entries": [
                {
                    "term": "Widget",
                    "korean_variants": ["위젯"],
                    "collision_label": "safe",
                    "source": "capitalized",
                },
            ],
        }
    )
    db2 = TermDB.model_validate(
        {
            "entries": [
                {
                    "term": "Widget",
                    "korean_variants": ["로"],
                    "collision_label": "safe",
                    "source": "mapping_pair",
                },
            ],
        }
    )

    merged = builder.merge_term_dbs([db1, db2], seed)
    entry = {e.term: e for e in merged.entries}["Widget"]

    # 단독으로는 safe였지만 db2가 부착한 "로" variant 때문에 병합 후 particle_collision이 된다
    assert entry.korean_variants == ["위젯", "로"]
    assert entry.collision_label == "particle_collision"
    # source는 먼저 등록된(db1) 값을 유지 — 참고용 메타데이터일 뿐 분류에는 영향 없음
    assert entry.source == "capitalized"


def test_merge_term_dbs_passes_through_term_only_in_one_db():
    seed = CollisionSeed(particles=[], content_word_homophones=[], known_terms={})
    db1 = TermDB.model_validate(
        {"entries": [{"term": "RDBMS", "collision_label": "safe", "source": "acronym"}]}
    )
    db2 = TermDB.model_validate(
        {"entries": [{"term": "Neo4j", "collision_label": "safe", "source": "alphanumeric"}]}
    )

    merged = builder.merge_term_dbs([db1, db2], seed)
    entries_by_term = {e.term: e for e in merged.entries}

    assert set(entries_by_term) == {"RDBMS", "Neo4j"}
    assert entries_by_term["Neo4j"].source == "alphanumeric"


def test_merge_term_dbs_topic_uses_last_non_null():
    seed = CollisionSeed(particles=[], content_word_homophones=[], known_terms={})
    db_with_topic = TermDB.model_validate({"topic": "DB", "entries": []})
    db_without_topic = TermDB.model_validate({"entries": []})
    db_other_topic = TermDB.model_validate({"topic": "Algorithms", "entries": []})

    # 새 빌드에서 --topic을 생략하면 기존 topic이 유지된다
    assert builder.merge_term_dbs([db_with_topic, db_without_topic], seed).topic == "DB"
    # 새 빌드에서 --topic을 다르게 지정하면 마지막 값이 이긴다
    assert builder.merge_term_dbs([db_with_topic, db_other_topic], seed).topic == "Algorithms"
