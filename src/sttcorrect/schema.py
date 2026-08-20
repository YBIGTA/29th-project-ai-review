from typing import Literal

from pydantic import BaseModel, Field


class TermDBUsed(BaseModel):
    safe: list[str] = Field(default_factory=list)
    content_word_collision: list[str] = Field(default_factory=list)
    particle_collision: list[str] = Field(default_factory=list)


class TranscriptionResult(BaseModel):
    session_id: str
    topic: str
    transcript_raw: str
    transcript_corrected: str
    term_db_used: TermDBUsed


class OrganizedTranscript(BaseModel):
    """오디오 전사/1차 보정(run_pipeline)과는 별개의 2차 후보정 단계
    (cli/organize_transcript.py)의 출력. TranscriptionResult와 다른 파일에 저장된다."""

    session_id: str
    topic: str
    organized_text: str


class TermEntry(BaseModel):
    term: str
    korean_variants: list[str] = Field(default_factory=list)
    collision_label: Literal["safe", "content_word_collision", "particle_collision"]
    source: Literal["capitalized", "acronym", "alphanumeric", "mapping_pair", "compound", "derived_acronym"]


class TermDB(BaseModel):
    """빌드 단계의 rich 표현. 최종 출력에 들어가는 flat한 TermDBUsed와는 다른 표현이므로 섞지 말 것."""

    course_id: str | None = None
    topic: str | None = None
    entries: list[TermEntry] = Field(default_factory=list)

    def to_term_db_used(self) -> TermDBUsed:
        """entries를 collision_label별로 묶어 순서 보존 + 중복 제거한 문자열 리스트로 변환"""
        buckets: dict[str, dict[str, None]] = {
            "safe": {},
            "content_word_collision": {},
            "particle_collision": {},
        }
        for entry in self.entries:
            buckets[entry.collision_label][entry.term] = None
        return TermDBUsed(
            safe=list(buckets["safe"]),
            content_word_collision=list(buckets["content_word_collision"]),
            particle_collision=list(buckets["particle_collision"]),
        )
