from sttcorrect.llm.base import LLMClient
from sttcorrect.llm.correction import correct_with_llm
from sttcorrect.schema import TermDB, TranscriptionResult
from sttcorrect.stt.whisper_backend import WhisperSttBackend
from sttcorrect.term_db.prompt_builder import build_stt_hints


def run_pipeline(
    audio_path: str,
    term_db: TermDB,
    session_id: str,
    topic: str,
    stt: WhisperSttBackend | None = None,
    llm: LLMClient | None = None,
) -> TranscriptionResult:
    """1. initial_prompt, hotwords = build_stt_hints(term_db)
    2. stt = stt or WhisperSttBackend()
    3. transcript_raw = stt.transcribe(audio_path, initial_prompt, hotwords)
    4. term_db_used = term_db.to_term_db_used()
    5. llm = llm or GroqLLMClient()
    6. transcript_corrected = correct_with_llm(transcript_raw, term_db_used, llm)
    7. TranscriptionResult(session_id, topic, transcript_raw, transcript_corrected, term_db_used) 반환"""
    initial_prompt, hotwords = build_stt_hints(term_db)

    stt = stt or WhisperSttBackend()
    transcript_raw = stt.transcribe(audio_path, initial_prompt=initial_prompt, hotwords=hotwords)

    if llm is None:
        from sttcorrect.llm.groq_client import GroqLLMClient

        llm = GroqLLMClient()

    term_db_used = term_db.to_term_db_used()
    transcript_corrected = correct_with_llm(transcript_raw, term_db_used, llm)

    return TranscriptionResult(
        session_id=session_id,
        topic=topic,
        transcript_raw=transcript_raw,
        transcript_corrected=transcript_corrected,
        term_db_used=term_db_used,
    )
