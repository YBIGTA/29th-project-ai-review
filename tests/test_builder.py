import json
from pathlib import Path

from sttcorrect.schema import TermDB, TermEntry
from sttcorrect.term_db import builder
from sttcorrect.term_db.collision import CollisionSeed

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = REPO_ROOT / "config" / "seed_collision_terms.yaml"

SAMPLE_TEXT = (
    "The RDBMS 는 관계형 데이터베이스이고, Table 그리고 Row 두 요소로 구성된다. "
    "Neo4j 는 그래프 DB의 예시이다."
)


def test_build_term_db_attaches_llm_generated_pronunciation(fake_llm_client, monkeypatch):
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: SAMPLE_TEXT)
    fake_llm_client.response = json.dumps({"RDBMS": "알디비엠에스", "Row": "로우"}, ensure_ascii=False)

    term_db = builder.build_term_db(
        "dummy.pdf", topic="DB", seed_path=str(SEED_PATH), llm=fake_llm_client
    )
    entries_by_term = {e.term: e for e in term_db.entries}

    assert entries_by_term["RDBMS"].korean_variants == ["알디비엠에스"]
    assert entries_by_term["RDBMS"].source == "acronym"

    # Row는 LLM이 준 발음이 붙고, curated seed 테이블에 의해 particle_collision으로 분류된다
    assert entries_by_term["Row"].korean_variants == ["로우"]
    assert entries_by_term["Row"].collision_label == "particle_collision"

    # Neo4j는 LLM 응답에 없으므로 korean_variants가 빈 채로 남는다 (크래시 없이)
    assert entries_by_term["Neo4j"].source == "alphanumeric"
    assert entries_by_term["Neo4j"].korean_variants == []

    assert term_db.topic == "DB"


def test_build_term_db_ignores_llm_hallucinated_term_not_in_candidates(fake_llm_client, monkeypatch):
    # LLM이 후보 목록에 없는 "Foo"를 지어내 응답에 포함시켜도 최종 DB에 들어가면 안 된다
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: SAMPLE_TEXT)
    fake_llm_client.response = json.dumps({"RDBMS": "알디비엠에스", "Foo": "푸"}, ensure_ascii=False)

    term_db = builder.build_term_db("dummy.pdf", seed_path=str(SEED_PATH), llm=fake_llm_client)
    entries_by_term = {e.term: e for e in term_db.entries}
    assert "Foo" not in entries_by_term


def test_fold_case_variants_merges_acronym_and_capitalized_form():
    entries_by_term = {
        "Key": TermEntry(term="Key", korean_variants=["키"], collision_label="safe", source="capitalized"),
        "KEY": TermEntry(term="KEY", korean_variants=["케이"], collision_label="safe", source="acronym"),
    }
    folded = builder._fold_case_variants(entries_by_term)
    # acronym이 capitalized보다 우선순위가 높으므로 canonical 표기는 "KEY"
    assert list(folded.keys()) == ["KEY"]
    assert folded["KEY"].korean_variants == ["케이", "키"]


def test_fold_case_variants_preserves_agreeing_particle_collision_label():
    # Row/ROW 둘 다 이미 particle_collision인 케이스 — 병합이 라벨을 깨지 않아야 한다는 sanity check
    entries_by_term = {
        "Row": TermEntry(
            term="Row", korean_variants=["로우"], collision_label="particle_collision", source="capitalized"
        ),
        "ROW": TermEntry(term="ROW", korean_variants=[], collision_label="particle_collision", source="acronym"),
    }
    folded = builder._fold_case_variants(entries_by_term)
    assert list(folded.keys()) == ["ROW"]
    assert folded["ROW"].korean_variants == ["로우"]


def test_build_term_db_case_folds_before_calling_llm(fake_llm_client, monkeypatch):
    # KEY(acronym 후보)와 Key(capitalized 후보)가 같은 텍스트에 섞여 있어도 fold가 먼저 실행돼
    # LLM에는 canonical 표기 "KEY" 하나로만 물어봐야 한다 (중복 API 호출 낭비 방지)
    text = "The KEY and Key are important terms."
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: text)
    fake_llm_client.response = json.dumps({"KEY": "키"}, ensure_ascii=False)

    term_db = builder.build_term_db("dummy.pdf", seed_path=str(SEED_PATH), llm=fake_llm_client)
    entries_by_term = {e.term: e for e in term_db.entries}

    assert "Key" not in entries_by_term
    assert "용어 목록: KEY" in fake_llm_client.last_prompt  # fold 후 딱 1개만 LLM에 전달됐는지
    assert entries_by_term["KEY"].korean_variants == ["키"]


def test_build_term_db_includes_compound_term_with_curated_collision_label(fake_llm_client, monkeypatch):
    text = "PRIMARY KEY는 테이블에서 각 행을 유일하게 식별한다."
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: text)
    fake_llm_client.response = json.dumps({"PRIMARY KEY": "프라이머리 키"}, ensure_ascii=False)

    term_db = builder.build_term_db("dummy.pdf", seed_path=str(SEED_PATH), llm=fake_llm_client)
    entries_by_term = {e.term: e for e in term_db.entries}

    assert entries_by_term["PRIMARY KEY"].source == "compound"
    # seed_collision_terms.yaml의 curated 규칙으로 content_word_collision 분류
    assert entries_by_term["PRIMARY KEY"].collision_label == "content_word_collision"


def test_build_term_db_adds_derived_acronym_when_literal_never_appears(fake_llm_client, monkeypatch):
    text = "Data Control Language 는 데이터베이스 사용 권한을 관리한다. Transaction Control Language 는 트랜잭션을 제어한다."
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: text)
    fake_llm_client.response = json.dumps({}, ensure_ascii=False)

    term_db = builder.build_term_db("dummy.pdf", seed_path=str(SEED_PATH), llm=fake_llm_client)
    entries_by_term = {e.term: e for e in term_db.entries}

    assert entries_by_term["DCL"].source == "derived_acronym"
    assert entries_by_term["TCL"].source == "derived_acronym"


def test_build_term_db_skips_derived_acronym_when_literal_already_present(fake_llm_client, monkeypatch):
    text = "DDL: 데이터베이스 정의(스키마)를 정의/변경하는 언어이다. Data Definition Language 는 스키마를 정의한다."
    monkeypatch.setattr(builder, "extract_and_dedup", lambda pdf_path: text)
    fake_llm_client.response = json.dumps({}, ensure_ascii=False)

    term_db = builder.build_term_db("dummy.pdf", seed_path=str(SEED_PATH), llm=fake_llm_client)
    entries_by_term = {e.term: e for e in term_db.entries}

    assert [t for t in entries_by_term if t.upper() == "DDL"] == ["DDL"]  # 중복 없음
    assert entries_by_term["DDL"].source == "acronym"  # 리터럴 source 유지


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
