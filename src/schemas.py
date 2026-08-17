from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class StructuredChunk(StrictModel):
    topic: str = Field(min_length=1)
    concepts: list[str] = Field(default_factory=list)
    raw_text: str
    visual_description: str = ""
    content: str = Field(min_length=1)

    @field_validator("concepts")
    @classmethod
    def normalize_concepts(cls, values: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            cleaned = value.strip()
            key = cleaned.casefold()
            if cleaned and key not in seen:
                result.append(cleaned)
                seen.add(key)
        return result


class StructuredPageResponse(StrictModel):
    chunks: list[StructuredChunk] = Field(min_length=1)


class Chunk(StrictModel):
    chunk_id: str = Field(min_length=1)
    lecture_id: str = Field(min_length=1)
    lecture_name: str = Field(min_length=1)
    page: int = Field(ge=1)
    topic: str = Field(min_length=1)
    concepts: list[str] = Field(default_factory=list)
    raw_text: str
    visual_description: str = ""
    content: str = Field(min_length=1)


class LectureDocument(StrictModel):
    lecture_id: str = Field(min_length=1)
    lecture_name: str = Field(min_length=1)
    source_file: str = Field(min_length=1)
    chunks: list[Chunk]


class CoreConceptCandidate(StrictModel):
    name: str = Field(min_length=1)
    importance: Literal["high", "medium", "low"]
    pages: list[int] = Field(min_length=1)
    description: str = Field(min_length=1)

    @field_validator("pages")
    @classmethod
    def normalize_pages(cls, values: list[int]) -> list[int]:
        if any(page < 1 for page in values):
            raise ValueError("페이지 번호는 1 이상이어야 합니다.")
        return sorted(set(values))


class CoreConceptResponse(StrictModel):
    core_concepts: list[CoreConceptCandidate] = Field(min_length=1)


class CoreConceptDocument(StrictModel):
    lecture_id: str = Field(min_length=1)
    lecture_name: str = Field(min_length=1)
    core_concepts: list[CoreConceptCandidate]


class SearchHit(StrictModel):
    rank: int = Field(ge=1)
    chunk_id: str
    lecture_id: str
    lecture_name: str
    page: int
    topic: str
    content: str
    distance: float
