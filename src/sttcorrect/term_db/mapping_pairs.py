import re

_PAREN_EN_KO = re.compile(r"([A-Za-z][A-Za-z0-9]+)\s*\(([가-힣]+)\)")  # "RDBMS(알디비엠에스)"
_PAREN_KO_EN = re.compile(r"([가-힣]+)\s*\(([A-Za-z][A-Za-z0-9 ]+)\)")  # "관계형 데이터베이스(RDBMS)"
_DASH_EN_KO = re.compile(r"([A-Za-z][A-Za-z0-9]+)\s*[-–:]\s*([가-힣]+)")


def extract_mapping_pairs(text: str) -> list[tuple[str, str]]:
    """PDF 텍스트에서 영-한 병기 패턴을 찾아 (영어용어, 한글표기) 쌍 목록으로 반환.
    이후 TermEntry.korean_variants에 병합됨"""
    pairs: list[tuple[str, str]] = []
    for en, ko in _PAREN_EN_KO.findall(text):
        pairs.append((en, ko))
    for ko, en in _PAREN_KO_EN.findall(text):
        pairs.append((en.strip(), ko))
    for en, ko in _DASH_EN_KO.findall(text):
        pairs.append((en, ko))
    return pairs
