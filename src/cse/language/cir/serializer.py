"""CIR Serializer — lossless Python ↔ JSON round-trip (PRD §17)."""

from __future__ import annotations

import json
from uuid import UUID

from cse.language.cir.exceptions import CIRSerializationError
from cse.language.cir.schema import (
    CIRDocument,
    CIRLexicalToken,
    CIRMetadata,
    CIRSpeechSegment,
    CIRUtterance,
)


# ---------------------------------------------------------------------------
# Serialize
# ---------------------------------------------------------------------------

def serialize(document: CIRDocument) -> str:
    """Convert a ``CIRDocument`` to a JSON string.

    Args:
        document: The CIR document to serialize.

    Returns:
        A JSON string representing the document.

    Raises:
        CIRSerializationError: On encoding failure.
    """
    try:
        return json.dumps(_doc_to_dict(document), ensure_ascii=False, indent=2)
    except Exception as exc:
        raise CIRSerializationError(f"Serialization failed: {exc}") from exc


def _doc_to_dict(doc: CIRDocument) -> dict:
    return {
        "uuid": str(doc.uuid),
        "version": doc.version,
        "raw_text": doc.raw_text,
        "language": doc.language,
        "utterances": [_utt_to_dict(u) for u in doc.utterances],
        "metadata": _meta_to_dict(doc.metadata),
    }


def _utt_to_dict(utt: CIRUtterance) -> dict:
    return {
        "uuid": str(utt.uuid),
        "text": utt.text,
        "segments": [_seg_to_dict(s) for s in utt.segments],
        "metadata": _meta_to_dict(utt.metadata),
    }


def _seg_to_dict(seg: CIRSpeechSegment) -> dict:
    return {
        "uuid": str(seg.uuid),
        "text": seg.text,
        "tokens": [_tok_to_dict(t) for t in seg.tokens],
        "segment_index": seg.segment_index,
        "source_offset": seg.source_offset,
        "length": seg.length,
        "metadata": _meta_to_dict(seg.metadata),
    }


def _tok_to_dict(tok: CIRLexicalToken) -> dict:
    return {
        "uuid": str(tok.uuid),
        "text": tok.text,
        "normalized": tok.normalized,
        "position": tok.position,
        "source_offset": tok.source_offset,
        "length": tok.length,
        "whitespace_after": tok.whitespace_after,
        "punctuation_after": tok.punctuation_after,
    }


def _meta_to_dict(meta: CIRMetadata) -> dict:
    return {
        "created_version": meta.created_version,
        "source": meta.source,
        "locale": meta.locale,
    }


# ---------------------------------------------------------------------------
# Deserialize
# ---------------------------------------------------------------------------

def deserialize(json_string: str) -> CIRDocument:
    """Reconstruct a ``CIRDocument`` from a JSON string.

    Args:
        json_string: A JSON string previously produced by ``serialize``.

    Returns:
        An immutable CIRDocument.

    Raises:
        CIRSerializationError: On decoding failure or missing fields.
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as exc:
        raise CIRSerializationError(f"Invalid JSON: {exc}") from exc

    try:
        return _dict_to_doc(data)
    except (KeyError, TypeError, ValueError) as exc:
        raise CIRSerializationError(f"Deserialization failed: {exc}") from exc


def _dict_to_doc(data: dict) -> CIRDocument:
    return CIRDocument(
        uuid=UUID(data["uuid"]),
        version=data["version"],
        raw_text=data["raw_text"],
        language=data["language"],
        utterances=tuple(_dict_to_utt(u) for u in data["utterances"]),
        metadata=_dict_to_meta(data["metadata"]),
    )


def _dict_to_utt(data: dict) -> CIRUtterance:
    return CIRUtterance(
        uuid=UUID(data["uuid"]),
        text=data["text"],
        segments=tuple(_dict_to_seg(s) for s in data["segments"]),
        metadata=_dict_to_meta(data["metadata"]),
    )


def _dict_to_seg(data: dict) -> CIRSpeechSegment:
    return CIRSpeechSegment(
        uuid=UUID(data["uuid"]),
        text=data["text"],
        tokens=tuple(_dict_to_tok(t) for t in data["tokens"]),
        segment_index=data["segment_index"],
        source_offset=data["source_offset"],
        length=data["length"],
        metadata=_dict_to_meta(data["metadata"]),
    )


def _dict_to_tok(data: dict) -> CIRLexicalToken:
    return CIRLexicalToken(
        uuid=UUID(data["uuid"]),
        text=data["text"],
        normalized=data["normalized"],
        position=data["position"],
        source_offset=data["source_offset"],
        length=data["length"],
        whitespace_after=data["whitespace_after"],
        punctuation_after=data["punctuation_after"],
    )


def _dict_to_meta(data: dict) -> CIRMetadata:
    return CIRMetadata(
        created_version=data["created_version"],
        source=data["source"],
        locale=data["locale"],
    )
