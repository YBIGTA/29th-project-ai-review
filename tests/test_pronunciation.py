import json

from sttcorrect.term_db.pronunciation import build_pronunciation_prompt, generate_pronunciations
from tests.conftest import FakeLLMClient


def test_build_pronunciation_prompt_includes_all_terms():
    prompt = build_pronunciation_prompt(["RDBMS", "Key", "Row"])
    assert "RDBMS, Key, Row" in prompt


def test_generate_pronunciations_parses_json_response(fake_llm_client):
    fake_llm_client.response = json.dumps({"RDBMS": "알디비엠에스", "Key": "키"}, ensure_ascii=False)
    result = generate_pronunciations(["RDBMS", "Key"], fake_llm_client)
    assert result == {"RDBMS": "알디비엠에스", "Key": "키"}


def test_generate_pronunciations_strips_markdown_code_fence(fake_llm_client):
    fake_llm_client.response = '```json\n{"RDBMS": "알디비엠에스"}\n```'
    result = generate_pronunciations(["RDBMS"], fake_llm_client)
    assert result == {"RDBMS": "알디비엠에스"}


def test_generate_pronunciations_matches_case_insensitively_but_returns_canonical_casing(fake_llm_client):
    # 실측 사례: LLM이 "DROP"을 "DROp"(오타)로 응답 — 대소문자만 다르면 구제하되,
    # 반환 키는 입력 목록의 canonical 표기("DROP")를 써야 한다
    fake_llm_client.response = json.dumps({"DROp": "드롭"}, ensure_ascii=False)
    result = generate_pronunciations(["DROP"], fake_llm_client)
    assert result == {"DROP": "드롭"}


def test_generate_pronunciations_ignores_hallucinated_extra_terms(fake_llm_client):
    # 입력 목록에 없는 "Foo"를 LLM이 지어내 응답에 포함시켜도 결과에서 제외돼야 한다
    fake_llm_client.response = json.dumps(
        {"RDBMS": "알디비엠에스", "Foo": "푸"}, ensure_ascii=False
    )
    result = generate_pronunciations(["RDBMS"], fake_llm_client)
    assert result == {"RDBMS": "알디비엠에스"}
    assert "Foo" not in result


def test_generate_pronunciations_handles_missing_terms_gracefully(fake_llm_client):
    # LLM이 "Row"를 응답에서 빠뜨려도 나머지는 정상 반영되고 크래시하지 않는다
    fake_llm_client.response = json.dumps({"RDBMS": "알디비엠에스"}, ensure_ascii=False)
    result = generate_pronunciations(["RDBMS", "Row"], fake_llm_client)
    assert result == {"RDBMS": "알디비엠에스"}


def test_generate_pronunciations_malformed_json_returns_empty_dict(fake_llm_client):
    fake_llm_client.response = "이건 JSON이 아닙니다"
    result = generate_pronunciations(["RDBMS"], fake_llm_client)
    assert result == {}


def test_generate_pronunciations_empty_terms_list_skips_llm_call(fake_llm_client):
    result = generate_pronunciations([], fake_llm_client)
    assert result == {}
    assert fake_llm_client.last_prompt is None


def test_generate_pronunciations_splits_large_term_list_into_chunks():
    # 실측: gpt-oss 계열은 추론 토큰을 먼저 쓰는 모델이라, 용어 목록이 크면(예: 186개)
    # 응답이 중간에 잘렸다(finish_reason="length"). 40개씩 나눠서 호출해야 한다.
    terms = [f"Term{i}" for i in range(50)]
    llm = FakeLLMClient(
        responses=[
            json.dumps({t: "발음" for t in terms[:40]}, ensure_ascii=False),
            json.dumps({t: "발음" for t in terms[40:]}, ensure_ascii=False),
        ]
    )
    result = generate_pronunciations(terms, llm)
    assert len(llm.prompts) == 2
    assert len(result) == 50
    assert all(term in result for term in terms)


def test_generate_pronunciations_one_broken_chunk_does_not_affect_others():
    terms = [f"Term{i}" for i in range(50)]
    llm = FakeLLMClient(
        responses=[
            "이건 JSON이 아닙니다",  # 첫 청크는 깨진 응답
            json.dumps({t: "발음" for t in terms[40:]}, ensure_ascii=False),  # 두번째는 정상
        ]
    )
    result = generate_pronunciations(terms, llm)
    assert len(result) == 10
    assert all(term in result for term in terms[40:])
    assert all(term not in result for term in terms[:40])
