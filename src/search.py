from __future__ import annotations

import re

from openai import OpenAI

from src.config import LECTURES, Settings
from src.embedding import create_embeddings, create_query_embedding
from src.schemas import (
    EvidenceHit,
    SearchHit,
    SegmentSearchResult,
    TranscriptSearchResult,
    TranscriptSegment,
)
from src.vector_store import LectureVectorStore


DEFAULT_SEGMENT_TARGET_CHARS = 220
DEFAULT_SEGMENT_MAX_CHARS = 360
DEFAULT_SEGMENT_MIN_CHARS = 60
DEFAULT_MAX_SEGMENTS = 12
DEFAULT_TOP_K_PER_SEGMENT = 5
DEFAULT_MAX_EVIDENCE = 12

_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?。！？])\s+")
_TOPIC_SHIFT_PATTERN = (
    r"(?:먼저|우선|첫째|첫\s*번째로?|다음으로|둘째|두\s*번째로?|"
    r"한편|반면(?:에)?|하지만|그러나|따라서|그러므로|"
    r"마지막으로|끝으로|이제)"
)
_TOPIC_SHIFT_SPLIT_RE = re.compile(
    rf"\s+(?={_TOPIC_SHIFT_PATTERN}(?:\s|[,，]))"
)
_TOPIC_SHIFT_START_RE = re.compile(rf"^{_TOPIC_SHIFT_PATTERN}(?:\s|[,，])")


def search(
    *,
    client: OpenAI,
    settings: Settings,
    query: str,
    top_k: int | None = None,
    lecture_id: str | None = None,
) -> list[SearchHit]:
    embedding = create_query_embedding(
        client=client, query=query, model=settings.embedding_model
    )
    store = LectureVectorStore(
        path=settings.vector_db_path,
        collection_name=settings.collection_name,
        embedding_model=settings.embedding_model,
    )
    return store.query(
        query_embedding=embedding,
        top_k=top_k or settings.top_k,
        lecture_id=lecture_id,
    )


def segment_transcript(
    transcript: str,
    *,
    min_chars: int = DEFAULT_SEGMENT_MIN_CHARS,
    target_chars: int = DEFAULT_SEGMENT_TARGET_CHARS,
    max_chars: int = DEFAULT_SEGMENT_MAX_CHARS,
    max_segments: int = DEFAULT_MAX_SEGMENTS,
) -> list[TranscriptSegment]:
    cleaned = transcript.strip()
    if not cleaned:
        raise ValueError("STT 답변은 비어 있을 수 없습니다.")
    if target_chars < 1:
        raise ValueError("target_chars는 1 이상이어야 합니다.")
    if min_chars < 1 or min_chars > target_chars:
        raise ValueError("min_chars는 1 이상 target_chars 이하여야 합니다.")
    if max_chars < target_chars:
        raise ValueError("max_chars는 target_chars 이상이어야 합니다.")
    if max_segments < 1:
        raise ValueError("max_segments는 1 이상이어야 합니다.")

    paragraphs = [
        re.sub(r"\s+", " ", paragraph).strip()
        for paragraph in re.split(r"\n\s*\n+", cleaned)
        if paragraph.strip()
    ]
    segment_texts: list[str] = []
    for paragraph in paragraphs:
        pieces = _semantic_pieces(paragraph, max_chars=max_chars)
        current: list[str] = []
        current_length = 0
        for piece in pieces:
            projected = current_length + (1 if current else 0) + len(piece)
            starts_new_topic = bool(_TOPIC_SHIFT_START_RE.match(piece))
            if current and (
                (starts_new_topic and current_length >= min_chars)
                or current_length >= target_chars
                or projected > max_chars
            ):
                segment_texts.append(" ".join(current))
                current = []
                current_length = 0
            current.append(piece)
            current_length += (1 if current_length else 0) + len(piece)
        if current:
            segment_texts.append(" ".join(current))

    segment_texts = _limit_segment_count(segment_texts, max_segments=max_segments)
    return [
        TranscriptSegment(
            segment_id=f"seg_{index:02d}",
            index=index,
            text=text,
        )
        for index, text in enumerate(segment_texts, start=1)
    ]


def search_transcript(
    *,
    client: OpenAI,
    settings: Settings,
    transcript: str,
    lecture_id: str,
    top_k_per_segment: int = DEFAULT_TOP_K_PER_SEGMENT,
    max_evidence: int = DEFAULT_MAX_EVIDENCE,
    max_distance: float | None = None,
    min_chars: int = DEFAULT_SEGMENT_MIN_CHARS,
    target_chars: int = DEFAULT_SEGMENT_TARGET_CHARS,
    max_chars: int = DEFAULT_SEGMENT_MAX_CHARS,
    max_segments: int = DEFAULT_MAX_SEGMENTS,
    store: LectureVectorStore | None = None,
) -> TranscriptSearchResult:
    if lecture_id not in LECTURES:
        raise ValueError(
            f"알 수 없는 lecture_id입니다: {lecture_id}. "
            f"가능한 값: {', '.join(LECTURES)}"
        )
    if top_k_per_segment < 1:
        raise ValueError("top_k_per_segment는 1 이상이어야 합니다.")
    if max_evidence < 1:
        raise ValueError("max_evidence는 1 이상이어야 합니다.")
    if max_distance is not None and max_distance < 0:
        raise ValueError("max_distance는 0 이상이어야 합니다.")

    segments = segment_transcript(
        transcript,
        min_chars=min_chars,
        target_chars=target_chars,
        max_chars=max_chars,
        max_segments=max_segments,
    )
    embeddings = create_embeddings(
        client=client,
        texts=[segment.text for segment in segments],
        model=settings.embedding_model,
        batch_size=settings.embedding_batch_size,
    )
    vector_store = store or LectureVectorStore(
        path=settings.vector_db_path,
        collection_name=settings.collection_name,
        embedding_model=settings.embedding_model,
    )
    hit_groups = vector_store.query_many(
        query_embeddings=embeddings,
        top_k=top_k_per_segment,
        lecture_id=lecture_id,
    )
    if len(hit_groups) != len(segments):
        raise RuntimeError("STT 구간 수와 ChromaDB 검색 결과 묶음 수가 다릅니다.")

    segment_results = [
        SegmentSearchResult(segment=segment, hits=hits)
        for segment, hits in zip(segments, hit_groups)
    ]
    evidence = _select_diverse_evidence(
        segment_results,
        max_evidence=max_evidence,
        max_distance=max_distance,
    )
    return TranscriptSearchResult(
        lecture_id=lecture_id,
        segment_results=segment_results,
        evidence=evidence,
    )


def _semantic_pieces(paragraph: str, *, max_chars: int) -> list[str]:
    sentences = [
        sentence.strip()
        for sentence in _SENTENCE_BOUNDARY_RE.split(paragraph)
        if sentence.strip()
    ]
    pieces: list[str] = []
    for sentence in sentences:
        shifted = [
            piece.strip()
            for piece in _TOPIC_SHIFT_SPLIT_RE.split(sentence)
            if piece.strip()
        ]
        for piece in shifted:
            pieces.extend(_split_oversized_piece(piece, max_chars=max_chars))
    return pieces


def _split_oversized_piece(text: str, *, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    if len(words) == 1:
        return [text[start : start + max_chars] for start in range(0, len(text), max_chars)]

    result: list[str] = []
    current: list[str] = []
    current_length = 0
    for word in words:
        projected = current_length + (1 if current else 0) + len(word)
        if current and projected > max_chars:
            result.append(" ".join(current))
            current = []
            current_length = 0
        current.append(word)
        current_length += (1 if current_length else 0) + len(word)
    if current:
        result.append(" ".join(current))
    return result


def _limit_segment_count(texts: list[str], *, max_segments: int) -> list[str]:
    result = list(texts)
    while len(result) > max_segments:
        merge_at = min(
            range(len(result) - 1),
            key=lambda index: len(result[index]) + len(result[index + 1]),
        )
        result[merge_at : merge_at + 2] = [
            f"{result[merge_at]} {result[merge_at + 1]}"
        ]
    return result


def _select_diverse_evidence(
    segment_results: list[SegmentSearchResult],
    *,
    max_evidence: int,
    max_distance: float | None,
) -> list[EvidenceHit]:
    best_by_chunk: dict[str, SearchHit] = {}
    matched_segments: dict[str, list[str]] = {}
    for result in segment_results:
        for hit in result.hits:
            if max_distance is not None and hit.distance > max_distance:
                continue
            current_best = best_by_chunk.get(hit.chunk_id)
            if current_best is None or hit.distance < current_best.distance:
                best_by_chunk[hit.chunk_id] = hit
            segment_ids = matched_segments.setdefault(hit.chunk_id, [])
            if result.segment.segment_id not in segment_ids:
                segment_ids.append(result.segment.segment_id)

    # First preserve topical coverage by taking each segment's strongest valid hit.
    # Then fill the remaining capacity by global distance, so a weak hit from an
    # earlier segment cannot displace a stronger hit from a later segment.
    coverage_candidates: list[SearchHit] = []
    for result in segment_results:
        strongest = next(
            (
                hit
                for hit in result.hits
                if max_distance is None or hit.distance <= max_distance
            ),
            None,
        )
        if strongest is not None:
            coverage_candidates.append(strongest)

    selected_ids: list[str] = []
    selected_id_set: set[str] = set()
    for hit in coverage_candidates:
        if hit.chunk_id in selected_id_set:
            continue
        selected_ids.append(hit.chunk_id)
        selected_id_set.add(hit.chunk_id)
        if len(selected_ids) == max_evidence:
            break

    remaining_candidates = sorted(
        (
            hit
            for chunk_id, hit in best_by_chunk.items()
            if chunk_id not in selected_id_set
        ),
        key=lambda hit: (hit.distance, hit.chunk_id),
    )
    for hit in remaining_candidates:
        if len(selected_ids) == max_evidence:
            break
        selected_ids.append(hit.chunk_id)
        selected_id_set.add(hit.chunk_id)

    evidence: list[EvidenceHit] = []
    for rank, chunk_id in enumerate(selected_ids, start=1):
        hit = best_by_chunk[chunk_id]
        evidence.append(
            EvidenceHit(
                rank=rank,
                chunk_id=hit.chunk_id,
                lecture_id=hit.lecture_id,
                lecture_name=hit.lecture_name,
                page=hit.page,
                topic=hit.topic,
                content=hit.content,
                best_distance=hit.distance,
                matched_segment_ids=matched_segments[chunk_id],
            )
        )
    return evidence
