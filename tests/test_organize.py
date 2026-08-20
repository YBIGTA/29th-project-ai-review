from sttcorrect.llm.organize import build_organize_prompt, organize_transcript


def test_build_organize_prompt_includes_transcript():
    prompt = build_organize_prompt("원본 구어체 텍스트")
    assert "원본 구어체 텍스트" in prompt


def test_organize_transcript_calls_client_with_built_prompt(fake_llm_client):
    result = organize_transcript("원본 구어체 텍스트", fake_llm_client)
    assert result == fake_llm_client.response
    assert "원본 구어체 텍스트" in fake_llm_client.last_prompt
