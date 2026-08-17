from sttcorrect.llm.correction import build_correction_prompt, correct_with_llm
from sttcorrect.schema import TermDBUsed


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


def test_correct_with_llm_calls_client_with_built_prompt(fake_llm_client):
    term_db_used = TermDBUsed(safe=["RDBMS"], content_word_collision=[], particle_collision=["Row"])
    result = correct_with_llm("원본", term_db_used, fake_llm_client)
    assert result == fake_llm_client.response
    assert "원본" in fake_llm_client.last_prompt
    assert "Row" in fake_llm_client.last_prompt
