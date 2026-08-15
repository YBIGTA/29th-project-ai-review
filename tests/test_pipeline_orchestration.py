from sttcorrect.pipeline import run_pipeline
from sttcorrect.schema import TermDB, TermEntry


def _sample_term_db() -> TermDB:
    return TermDB(
        topic="DB",
        entries=[
            TermEntry(term="RDBMS", collision_label="safe", source="acronym"),
            TermEntry(term="Key", collision_label="content_word_collision", source="capitalized"),
            TermEntry(term="Row", collision_label="particle_collision", source="capitalized"),
        ],
    )


def test_run_pipeline_wires_stt_hints_and_llm_correction(fake_stt_backend, fake_llm_client):
    term_db = _sample_term_db()

    result = run_pipeline(
        audio_path="lecture.wav",
        term_db=term_db,
        session_id="sess1",
        topic="DB",
        stt=fake_stt_backend,
        llm=fake_llm_client,
    )

    # STT는 term_db 기반 힌트(initial_prompt/hotwords)를 받아 호출됐어야 한다
    assert fake_stt_backend.last_call["wav_path"] == "lecture.wav"
    assert "RDBMS" in fake_stt_backend.last_call["initial_prompt"]
    assert "RDBMS" in fake_stt_backend.last_call["hotwords"]

    # transcript_raw는 STT(fake) 결과, transcript_corrected는 LLM(fake) 결과
    assert result.transcript_raw == fake_stt_backend.response
    assert result.transcript_corrected == fake_llm_client.response

    # LLM 프롬프트는 STT의 원본 결과와 particle_collision 용어(Row)를 참고해야 한다
    assert fake_stt_backend.response in fake_llm_client.last_prompt
    assert "Row" in fake_llm_client.last_prompt

    # term_db_used는 TermDB.to_term_db_used()와 동일한 3분류 구조여야 한다
    assert result.term_db_used == term_db.to_term_db_used()
    assert result.session_id == "sess1"
    assert result.topic == "DB"


def test_run_pipeline_does_not_require_real_stt_or_llm_backends(fake_stt_backend, fake_llm_client):
    # Fake만 주입해도 예외 없이 끝까지 실행되어야 한다 (실제 추론/네트워크 호출 없음)
    result = run_pipeline(
        audio_path="lec.wav",
        term_db=_sample_term_db(),
        session_id="s2",
        topic="DB",
        stt=fake_stt_backend,
        llm=fake_llm_client,
    )
    assert result.session_id == "s2"
