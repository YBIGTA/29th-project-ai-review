from typing import TYPE_CHECKING, Literal

import yaml
from pydantic import BaseModel

from sttcorrect.term_db.transliterate import guess_korean_transliteration

if TYPE_CHECKING:
    from sttcorrect.schema import TermEntry


class CollisionSeed(BaseModel):
    particles: list[str]
    content_word_homophones: list[str]
    known_terms: dict[str, dict]


def load_collision_seed(path: str = "config/seed_collision_terms.yaml") -> CollisionSeed:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    # YAML의 known_terms 키는 원표기(Row/Key/...)이지만 classify_term은 term.lower()로 조회하므로
    # 로드 시점에 키를 소문자로 정규화해 둔다 (그대로 두면 curated 최우선 규칙이 항상 미스난다).
    raw["known_terms"] = {k.lower(): v for k, v in raw.get("known_terms", {}).items()}
    return CollisionSeed(**raw)


def classify_term(
    term: str,
    seed: CollisionSeed,
    korean_variants: list[str] | None = None,
) -> Literal["safe", "content_word_collision", "particle_collision"]:
    """우선순위 (신뢰도 높은 순):
    1. seed.known_terms[term.lower()] — 수동 curated 테이블, 최우선
    2. korean_variants(PDF 실제 관찰값)가 seed.particles / seed.content_word_homophones에 걸리는지
    3. guess_korean_transliteration(term) fallback, 동일하게 멤버십 체크
    4. 기본값 'safe'
    """
    known = seed.known_terms.get(term.lower())
    if known is not None:
        return known["label"]

    variants = set(korean_variants or [])
    if variants & set(seed.particles):
        return "particle_collision"
    if variants & set(seed.content_word_homophones):
        return "content_word_collision"

    guess = guess_korean_transliteration(term)
    if guess is not None:
        if guess in seed.particles:
            return "particle_collision"
        if guess in seed.content_word_homophones:
            return "content_word_collision"

    return "safe"


def classify_terms(entries: list["TermEntry"], seed: CollisionSeed) -> list["TermEntry"]:
    """각 entry에 classify_term 적용 후 반환"""
    classified = []
    for entry in entries:
        label = classify_term(entry.term, seed, entry.korean_variants)
        classified.append(entry.model_copy(update={"collision_label": label}))
    return classified
