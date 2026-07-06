"""CIR immutable object hierarchy.

All objects are frozen dataclasses with tuple-based collections
(no mutable state, no runtime state, no backend references).

Hierarchy (PRD §7):
    CIRDocument → CIRUtterance → CIRSpeechSegment → CIRLexicalToken
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

# Schema version — matches PRD-002 version.
CIR_VERSION = "2.0.0"


# ---------------------------------------------------------------------------
# Metadata (PRD §12)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CIRMetadata:
    """Metadata attached to every CIR object."""

    created_version: str = CIR_VERSION
    source: str = "builder"
    locale: str = "en-US"


# ---------------------------------------------------------------------------
# CIRLexicalToken (PRD §11)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CIRLexicalToken:
    """One lexical element in a speech segment."""

    uuid: UUID
    text: str
    normalized: str
    position: int
    source_offset: int
    length: int
    whitespace_after: str
    punctuation_after: str


# ---------------------------------------------------------------------------
# CIRSpeechSegment (PRD §10)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CIRSpeechSegment:
    """The smallest meaningful performance unit."""

    uuid: UUID
    text: str
    tokens: tuple[CIRLexicalToken, ...]
    segment_index: int
    source_offset: int
    length: int
    metadata: CIRMetadata = field(default_factory=CIRMetadata)


# ---------------------------------------------------------------------------
# CIRUtterance (PRD §9)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CIRUtterance:
    """One spoken utterance (typically one sentence)."""

    uuid: UUID
    text: str
    segments: tuple[CIRSpeechSegment, ...]
    metadata: CIRMetadata = field(default_factory=CIRMetadata)


# ---------------------------------------------------------------------------
# CIRDocument (PRD §8)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CIRDocument:
    """Top-level CIR object representing a complete input."""

    uuid: UUID
    version: str
    raw_text: str
    language: str
    utterances: tuple[CIRUtterance, ...]
    metadata: CIRMetadata = field(default_factory=CIRMetadata)
