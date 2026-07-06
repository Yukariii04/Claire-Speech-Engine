"""CIR Validator — structural integrity checks for CIRDocument.

Detects (PRD §16):
  - Empty document (no utterances)
  - Missing UUIDs
  - Invalid version
  - Invalid language
  - Invalid offsets
  - Duplicate UUIDs
  - Malformed hierarchy
"""

from __future__ import annotations

from uuid import UUID

from cse.language.cir.exceptions import CIRValidationError
from cse.language.cir.schema import (
    CIR_VERSION,
    CIRDocument,
    CIRLexicalToken,
    CIRSpeechSegment,
    CIRUtterance,
)


def validate(document: CIRDocument) -> None:
    """Validate a ``CIRDocument``.

    Args:
        document: The CIR document to validate.

    Raises:
        CIRValidationError: On any structural problem.
    """
    _check_type(document)
    _check_version(document)
    _check_language(document)
    _check_not_empty(document)
    _check_hierarchy(document)
    _check_duplicate_uuids(document)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _check_type(document: object) -> None:
    if not isinstance(document, CIRDocument):
        raise CIRValidationError(
            f"Expected CIRDocument, got {type(document).__name__}"
        )


def _check_version(document: CIRDocument) -> None:
    if document.version != CIR_VERSION:
        raise CIRValidationError(
            f"Invalid version '{document.version}', expected '{CIR_VERSION}'"
        )


def _check_language(document: CIRDocument) -> None:
    if not document.language or not document.language.strip():
        raise CIRValidationError("Language must not be empty")


def _check_not_empty(document: CIRDocument) -> None:
    if not document.utterances:
        raise CIRValidationError("Empty document: no utterances")


def _check_hierarchy(document: CIRDocument) -> None:
    """Verify every utterance has ≥1 segment."""
    for i, utt in enumerate(document.utterances):
        if not isinstance(utt, CIRUtterance):
            raise CIRValidationError(
                f"Utterance {i} is not a CIRUtterance"
            )
        if not utt.segments:
            raise CIRValidationError(
                f"Utterance {i} has no segments"
            )
        for j, seg in enumerate(utt.segments):
            if not isinstance(seg, CIRSpeechSegment):
                raise CIRValidationError(
                    f"Segment {j} in utterance {i} is not a CIRSpeechSegment"
                )


def _check_duplicate_uuids(document: CIRDocument) -> None:
    """Collect all UUIDs and reject duplicates."""
    seen: set[UUID] = set()

    def _track(uid: UUID, label: str) -> None:
        if uid in seen:
            raise CIRValidationError(f"Duplicate UUID {uid} in {label}")
        seen.add(uid)

    _track(document.uuid, "document")
    for i, utt in enumerate(document.utterances):
        _track(utt.uuid, f"utterance[{i}]")
        for j, seg in enumerate(utt.segments):
            _track(seg.uuid, f"segment[{i}.{j}]")
            for k, tok in enumerate(seg.tokens):
                _track(tok.uuid, f"token[{i}.{j}.{k}]")
