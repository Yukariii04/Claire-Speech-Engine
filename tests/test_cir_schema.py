"""Tests for the CIR object hierarchy (schema.py).

Covers immutability, field correctness, and metadata defaults.
"""

from __future__ import annotations

import uuid

import pytest

from cse.language.cir.schema import (
    CIR_VERSION,
    CIRDocument,
    CIRLexicalToken,
    CIRMetadata,
    CIRSpeechSegment,
    CIRUtterance,
)


# ---- helpers ---------------------------------------------------------------

def _make_token(**overrides):
    defaults = dict(
        uuid=uuid.uuid4(),
        text="hello",
        normalized="hello",
        position=0,
        source_offset=0,
        length=5,
        whitespace_after=" ",
        punctuation_after="",
    )
    defaults.update(overrides)
    return CIRLexicalToken(**defaults)


def _make_segment(**overrides):
    tok = _make_token()
    defaults = dict(
        uuid=uuid.uuid4(),
        text="hello",
        tokens=(tok,),
        segment_index=0,
        source_offset=0,
        length=5,
    )
    defaults.update(overrides)
    return CIRSpeechSegment(**defaults)


def _make_utterance(**overrides):
    seg = _make_segment()
    defaults = dict(
        uuid=uuid.uuid4(),
        text="hello",
        segments=(seg,),
    )
    defaults.update(overrides)
    return CIRUtterance(**defaults)


def _make_document(**overrides):
    utt = _make_utterance()
    defaults = dict(
        uuid=uuid.uuid4(),
        version=CIR_VERSION,
        raw_text="hello",
        language="en",
        utterances=(utt,),
    )
    defaults.update(overrides)
    return CIRDocument(**defaults)


# ---- CIRMetadata -----------------------------------------------------------

class TestCIRMetadata:
    def test_defaults(self):
        m = CIRMetadata()
        assert m.created_version == CIR_VERSION
        assert m.source == "builder"
        assert m.locale == "en-US"

    def test_immutable(self):
        m = CIRMetadata()
        with pytest.raises(AttributeError):
            m.source = "other"  # type: ignore[misc]


# ---- CIRLexicalToken -------------------------------------------------------

class TestCIRLexicalToken:
    def test_fields(self):
        tok = _make_token(text="world", position=3, source_offset=10, length=5)
        assert tok.text == "world"
        assert tok.position == 3
        assert tok.source_offset == 10
        assert tok.length == 5

    def test_immutable(self):
        tok = _make_token()
        with pytest.raises(AttributeError):
            tok.text = "other"  # type: ignore[misc]


# ---- CIRSpeechSegment ------------------------------------------------------

class TestCIRSpeechSegment:
    def test_tokens_are_tuple(self):
        seg = _make_segment()
        assert isinstance(seg.tokens, tuple)

    def test_default_metadata(self):
        seg = _make_segment()
        assert seg.metadata.created_version == CIR_VERSION

    def test_immutable(self):
        seg = _make_segment()
        with pytest.raises(AttributeError):
            seg.text = "nope"  # type: ignore[misc]


# ---- CIRUtterance ----------------------------------------------------------

class TestCIRUtterance:
    def test_segments_are_tuple(self):
        utt = _make_utterance()
        assert isinstance(utt.segments, tuple)

    def test_immutable(self):
        utt = _make_utterance()
        with pytest.raises(AttributeError):
            utt.text = "nope"  # type: ignore[misc]


# ---- CIRDocument -----------------------------------------------------------

class TestCIRDocument:
    def test_version(self):
        doc = _make_document()
        assert doc.version == CIR_VERSION

    def test_utterances_are_tuple(self):
        doc = _make_document()
        assert isinstance(doc.utterances, tuple)

    def test_default_metadata(self):
        doc = _make_document()
        assert doc.metadata.locale == "en-US"

    def test_immutable(self):
        doc = _make_document()
        with pytest.raises(AttributeError):
            doc.raw_text = "nope"  # type: ignore[misc]
