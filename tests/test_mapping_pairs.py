from sttcorrect.term_db.mapping_pairs import extract_mapping_pairs


def test_extract_paren_en_ko():
    pairs = extract_mapping_pairs("RDBMS(알디비엠에스)를 배운다.")
    assert ("RDBMS", "알디비엠에스") in pairs


def test_extract_paren_ko_en():
    pairs = extract_mapping_pairs("데이터베이스(RDBMS)를 배운다.")
    assert ("RDBMS", "데이터베이스") in pairs


def test_extract_dash_en_ko():
    # 한글 뒤에 조사가 공백 없이 바로 붙으면 정규식이 조사까지 통째로 캡처한다(스켈레톤 정규식의
    # 알려진 한계이며, 이 한계 때문에 이런 짧은 한글 병기 뒤에는 구두점/공백으로 끊어주는 편이 안전).
    pairs = extract_mapping_pairs("Row - 로우, 테이블의 한 행이다.")
    assert ("Row", "로우") in pairs


def test_extract_colon_en_ko():
    pairs = extract_mapping_pairs("Key: 키")
    assert ("Key", "키") in pairs


def test_no_match_returns_empty_list():
    assert extract_mapping_pairs("이 문장에는 병기 패턴이 없다.") == []
