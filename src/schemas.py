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


PageRole = Literal[
    "cover",
    "table_of_contents",
    "section_divider",
    "core_content",
    "example",
    "supplementary_reference",
    "closing",
]
EvidenceUnitType = Literal[
    "definition",
    "formula",
    "procedure",
    "relation",
    "interpretation",
    "assumption",
    "warning",
    "comparison",
    "diagnostic",
    "example",
]
EvidenceSourceType = Literal[
    "text",
    "formula",
    "visual",
    "text_and_formula",
    "text_and_visual",
]
ProcessedSourceStatus = Literal["verified", "needs_review", "source_error"]


class TerminologyEntry(StrictModel):
    term_id: str = Field(min_length=1)
    canonical_ko: str = Field(min_length=1)
    canonical_en: str = ""
    abbreviations: list[str] = Field(default_factory=list)
    accepted_aliases: list[str] = Field(default_factory=list)
    symbols: list[str] = Field(default_factory=list)
    not_equivalent_to: list[str] = Field(default_factory=list)


class EvidenceUnit(StrictModel):
    unit_id: str = Field(min_length=1)
    type: EvidenceUnitType
    source_type: EvidenceSourceType
    source_excerpt: str = Field(min_length=1)
    normalized_explanation: str = Field(min_length=1)
    source_status: ProcessedSourceStatus = "verified"
    term_ids: list[str] = Field(default_factory=list)


class SourceIssue(StrictModel):
    issue_id: str = Field(min_length=1)
    source_text: str = Field(min_length=1)
    issue_type: Literal["typo", "incorrect", "overgeneralized", "ambiguous"]
    correction: str = Field(min_length=1)
    evaluation_policy: Literal["exclude", "warn"] = "exclude"


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
    page_role: PageRole | None = None
    term_ids: list[str] = Field(default_factory=list)
    evidence_units: list[EvidenceUnit] = Field(default_factory=list)
    source_issues: list[SourceIssue] = Field(default_factory=list)


class LectureDocument(StrictModel):
    schema_version: str | None = None
    lecture_id: str = Field(min_length=1)
    lecture_name: str = Field(min_length=1)
    source_file: str = Field(min_length=1)
    terminology: list[TerminologyEntry] = Field(default_factory=list)
    chunks: list[Chunk]


class TranscriptSegment(StrictModel):
    segment_id: str = Field(min_length=1)
    index: int = Field(ge=1)
    text: str = Field(min_length=1)
