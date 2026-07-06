"""CIR Builder — transforms raw text into a CIRDocument.

Responsibilities (PRD §15):
  - Split into utterances (sentence boundary detection).
  - Create speech segments (one per utterance for now).
  - Create lexical tokens (word-level, no phonemes/emotion/pauses).
  - Assign deterministic UUIDs.
  - Assign source offsets and lengths.
  - Assign metadata.
"""

from __future__ import annotations

import re

from cse.language.cir.exceptions import CIRBuilderError
from cse.language.cir.ids import generate_id
from cse.language.cir.schema import (
    CIR_VERSION,
    CIRDocument,
    CIRLexicalToken,
    CIRMetadata,
    CIRSpeechSegment,
    CIRUtterance,
)

# Sentence-boundary regex: split on .!? followed by whitespace or end-of-string.
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

# Word + trailing punctuation regex.
_TOKEN_RE = re.compile(r"(\S+?)(([.!?,;:\"'\u2018\u2019\u201C\u201D\u2026)}\]]+)\s*$|\s*$)")


def build_cir(text: str) -> CIRDocument:
    """Parse *text* into an immutable ``CIRDocument``.

    Args:
        text: Raw English UTF-8 input.

    Returns:
        A fully-populated CIRDocument.

    Raises:
        CIRBuilderError: If *text* is not a non-empty string.
    """
    if not isinstance(text, str):
        raise CIRBuilderError(f"Expected str, got {type(text).__name__}")
    if not text.strip():
        raise CIRBuilderError("Input text is empty or whitespace-only")

    raw_text = text
    stripped = text.strip()

    # -- split into sentences --------------------------------------------------
    sentence_texts = _split_sentences(stripped)

    # -- build utterances ------------------------------------------------------
    utterances: list[CIRUtterance] = []
    # Track the offset within `stripped` for each sentence
    search_start = 0
    for sent_text in sentence_texts:
        offset_in_stripped = stripped.index(sent_text, search_start)
        utt = _build_utterance(sent_text, offset_in_stripped, len(utterances), raw_text)
        utterances.append(utt)
        search_start = offset_in_stripped + len(sent_text)

    doc_id = generate_id(f"doc:{raw_text}")
    return CIRDocument(
        uuid=doc_id,
        version=CIR_VERSION,
        raw_text=raw_text,
        language="en",
        utterances=tuple(utterances),
        metadata=CIRMetadata(),
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    """Split *text* on sentence-ending punctuation (.!?)."""
    parts = _SENTENCE_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def _build_utterance(
    text: str,
    source_offset: int,
    utt_index: int,
    raw_text: str,
) -> CIRUtterance:
    """Build a single ``CIRUtterance`` with one segment."""
    segment = _build_segment(text, source_offset, 0, raw_text)
    utt_id = generate_id(f"utt:{utt_index}:{raw_text}")
    return CIRUtterance(
        uuid=utt_id,
        text=text,
        segments=(segment,),
        metadata=CIRMetadata(),
    )


def _build_segment(
    text: str,
    source_offset: int,
    segment_index: int,
    raw_text: str,
) -> CIRSpeechSegment:
    """Build a single ``CIRSpeechSegment`` with tokenized words."""
    tokens = _tokenize(text, source_offset, raw_text)
    seg_id = generate_id(f"seg:{segment_index}:{source_offset}:{text}:{raw_text}")
    return CIRSpeechSegment(
        uuid=seg_id,
        text=text,
        tokens=tuple(tokens),
        segment_index=segment_index,
        source_offset=source_offset,
        length=len(text),
        metadata=CIRMetadata(),
    )


def _tokenize(
    text: str,
    base_offset: int,
    raw_text: str,
) -> list[CIRLexicalToken]:
    """Tokenize *text* into ``CIRLexicalToken`` objects.

    Splits on whitespace, strips trailing punctuation from each word.
    """
    tokens: list[CIRLexicalToken] = []
    # Use finditer to get word positions precisely
    position = 0
    for match in re.finditer(r"\S+", text):
        raw_word = match.group()
        word_start = match.start()

        # Separate trailing punctuation
        m = re.match(r"^(.*?)([.!?,;:\"'\u2018\u2019\u201C\u201D\u2026)}\]]+)$", raw_word)
        if m and m.group(1):
            word = m.group(1)
            punct = m.group(2)
        else:
            word = raw_word
            punct = ""

        # Determine whitespace after this token
        end_pos = match.end()
        if end_pos < len(text) and text[end_pos] == " ":
            ws_after = " "
        else:
            ws_after = ""

        tok_id = generate_id(f"tok:{position}:{base_offset + word_start}:{word}:{raw_text}")
        tokens.append(
            CIRLexicalToken(
                uuid=tok_id,
                text=word,
                normalized=word.lower(),
                position=position,
                source_offset=base_offset + word_start,
                length=len(word),
                whitespace_after=ws_after,
                punctuation_after=punct,
            )
        )
        position += 1

    return tokens
