from sttcorrect.llm.correction import build_correction_prompt, correct_with_llm
from sttcorrect.schema import TermDBUsed
from tests.conftest import FakeLLMClient


def test_build_correction_prompt_merges_safe_and_content_word_collision():
    term_db_used = TermDBUsed(
        safe=["RDBMS", "Transaction"],
        content_word_collision=["Key", "Set"],
        particle_collision=["Row"],
    )
    prompt = build_correction_prompt("원본 텍스트", term_db_used)
    assert "RDBMS, Transaction, Key, Set" in prompt
    assert "Row" in prompt
    assert "원본 텍스트" in prompt


def test_build_correction_prompt_isolates_particle_collision_as_risky():
    term_db_used = TermDBUsed(
        safe=["RDBMS"],
        content_word_collision=["Key"],
        particle_collision=["Row"],
    )
    prompt = build_correction_prompt("t", term_db_used)
    safe_line = next(line for line in prompt.splitlines() if line.startswith("일반 용어:"))
    risky_line = next(line for line in prompt.splitlines() if "신중히 판단" in line)
    assert "Row" not in safe_line
    assert "Row" in risky_line
    assert "Key" not in risky_line


def test_build_correction_prompt_handles_empty_risky_terms():
    term_db_used = TermDBUsed(safe=["RDBMS"], content_word_collision=[], particle_collision=[])
    prompt = build_correction_prompt("t", term_db_used)
    # 빈 리스트여도 예외 없이 빈 문자열로 렌더링돼야 한다
    risky_line = next(line for line in prompt.splitlines() if "신중히 판단" in line)
    assert risky_line.endswith(": ")


def test_build_correction_prompt_instructs_restoring_english_terms():
    term_db_used = TermDBUsed(safe=["RDBMS"], content_word_collision=[], particle_collision=[])
    prompt = build_correction_prompt("t", term_db_used)
    assert "영어 원어" in prompt


def test_correct_with_llm_calls_client_with_built_prompt(fake_llm_client):
    term_db_used = TermDBUsed(safe=["RDBMS"], content_word_collision=[], particle_collision=["Row"])
    result = correct_with_llm("원본", term_db_used, fake_llm_client)
    assert result == fake_llm_client.response
    assert "원본" in fake_llm_client.last_prompt
    assert "Row" in fake_llm_client.last_prompt


def test_correct_with_llm_splits_long_transcript_into_sentence_chunks():
    # 실측: 4분 분량 강의 전사본을 통째로 보정 요청하면 추론 모델(gpt-oss)의
    # completion 토큰 예산(사고 과정이 79% 소모)을 넘어 응답이 잘렸다. 문장
    # 경계에서 청크로 나눠 각각 호출해야 한다.
    term_db_used = TermDBUsed(safe=["RDBMS"], content_word_collision=[], particle_collision=[])
    sentence1 = "가" * 400 + "."
    sentence2 = "나" * 400 + "."
    transcript = f"{sentence1} {sentence2}"
    llm = FakeLLMClient(responses=["보정1", "보정2"])
    result = correct_with_llm(transcript, term_db_used, llm)
    assert len(llm.prompts) == 2
    assert sentence1 in llm.prompts[0]
    assert sentence2 not in llm.prompts[0]
    assert sentence2 in llm.prompts[1]
    assert result == "보정1 보정2"


def test_correct_with_llm_falls_back_to_original_chunk_when_response_is_empty():
    # 실측 사례: 추론 모델이 completion 토큰 예산을 사고 과정에 다 써버려 특정
    # 청크만 빈 문자열로 돌아온 적이 있다 — 이때 그 청크의 내용을 잃지 않도록
    # 보정 실패분은 원문 그대로 유지해야 한다.
    term_db_used = TermDBUsed(safe=["RDBMS"], content_word_collision=[], particle_collision=[])
    sentence1 = "가" * 400 + "."
    sentence2 = "나" * 400 + "."
    transcript = f"{sentence1} {sentence2}"
    llm = FakeLLMClient(responses=["", "보정2"])
    result = correct_with_llm(transcript, term_db_used, llm)
    assert result == f"{sentence1} 보정2"
