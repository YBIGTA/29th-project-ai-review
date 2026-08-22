import json

from sttcorrect.schema import (
    OrganizedTranscript,
    TermDB,
    TermDBUsed,
    TermEntry,
    TranscriptionResult,
)


def test_transcription_result_matches_spec_json_shape():
    result = TranscriptionResult(
        session_id="abc123",
        topic="DB",
        transcript_raw="STT 원본 결과 (한국어)",
        transcript_corrected="LLM 보정 결과",
        term_db_used=TermDBUsed(
            safe=["RDBMS", "Transaction", "MongoDB"],
            content_word_collision=["Key", "Set", "One"],
            particle_collision=["Row"],
        ),
    )
    dumped = json.loads(result.model_dump_json())
    assert set(dumped.keys()) == {
        "session_id",
        "topic",
        "transcript_raw",
        "transcript_corrected",
        "term_db_used",
    }
    assert set(dumped["term_db_used"].keys()) == {
        "safe",
        "content_word_collision",
        "particle_collision",
    }
    assert dumped["session_id"] == "abc123"
    assert dumped["term_db_used"]["particle_collision"] == ["Row"]


def test_transcription_result_dumps_korean_without_escaping():
    result = TranscriptionResult(
        session_id="s1",
        topic="DB",
        transcript_raw="한국어",
        transcript_corrected="한국어 보정",
        term_db_used=TermDBUsed(),
    )
    dumped_json = result.model_dump_json(ensure_ascii=False, indent=2)
    assert "한국어" in dumped_json
    assert "\\uud55c" not in dumped_json


def test_organized_transcript_matches_expected_json_shape():
    organized = OrganizedTranscript(session_id="abc123", topic="DB", organized_text="정리된 텍스트")
    dumped = json.loads(organized.model_dump_json())
    assert set(dumped.keys()) == {"session_id", "topic", "organized_text"}
    assert dumped["organized_text"] == "정리된 텍스트"


def test_organized_transcript_dumps_korean_without_escaping():
    organized = OrganizedTranscript(session_id="s1", topic="DB", organized_text="한국어 정리본")
    dumped_json = organized.model_dump_json(ensure_ascii=False, indent=2)
    assert "한국어 정리본" in dumped_json
    assert "\\uud55c" not in dumped_json


def test_to_term_db_used_groups_by_collision_label():
    term_db = TermDB(
        topic="DB",
        entries=[
            TermEntry(term="RDBMS", collision_label="safe", source="acronym"),
            TermEntry(term="Key", collision_label="content_word_collision", source="capitalized"),
            TermEntry(term="Row", collision_label="particle_collision", source="capitalized"),
        ],
    )
    used = term_db.to_term_db_used()
    assert used.safe == ["RDBMS"]
    assert used.content_word_collision == ["Key"]
    assert used.particle_collision == ["Row"]


def test_to_term_db_used_preserves_order_and_dedupes():
    term_db = TermDB(
        entries=[
            TermEntry(term="RDBMS", collision_label="safe", source="acronym"),
            TermEntry(term="Transaction", collision_label="safe", source="capitalized"),
            TermEntry(term="RDBMS", collision_label="safe", source="acronym"),
        ],
    )
    used = term_db.to_term_db_used()
    assert used.safe == ["RDBMS", "Transaction"]
