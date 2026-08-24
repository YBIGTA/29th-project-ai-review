from __future__ import annotations

import re

from src.schemas import TranscriptSegment


DEFAULT_SEGMENT_TARGET_CHARS = 220
DEFAULT_SEGMENT_MAX_CHARS = 360
DEFAULT_SEGMENT_MIN_CHARS = 60
DEFAULT_MAX_SEGMENTS = 12

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

    while len(segment_texts) > max_segments:
        shortest_index = min(range(len(segment_texts) - 1), key=lambda i: len(segment_texts[i]))
        segment_texts[shortest_index : shortest_index + 2] = [
            f"{segment_texts[shortest_index]} {segment_texts[shortest_index + 1]}"
        ]
    return [
        TranscriptSegment(segment_id=f"seg_{index:02d}", index=index, text=text)
        for index, text in enumerate(segment_texts, start=1)
    ]


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
