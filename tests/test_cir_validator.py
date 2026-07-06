"""Tests for the CIR validator.

PRD §16: empty doc, missing UUID, invalid version, invalid language,
invalid offsets, duplicate UUIDs, malformed hierarchy.
"""

from __future__ import annotations

import uuid

import pytest

from cse.language.cir.builder import build_cir
from cse.language.cir.exceptions import CIRValidationError
from cse.language.cir.schema import (
    CIR_VERSION,
    CIRDocument,
    CIRMetadata,
    CIRSpeechSegment,
    CIRUtterance,
)
from cse.language.cir.validator import validate


class TestValidateGoodDocument:
    def test_valid_document_passes(self):
        doc = build_cir("Hello world.")
        validate(doc)  # should not raise

    def test_multi_sentence_passes(self):
        doc = build_cir("Hello. World. Goodbye.")
        validate(doc)


class TestValidateEmptyDocument:
    def test_no_utterances_raises(self):
        doc = CIRDocument(
            uuid=uuid.uuid4(),
            version=CIR_VERSION,
            raw_text="hello",
            language="en",
            utterances=(),
        )
        with pytest.raises(CIRValidationError, match="[Ee]mpty"):
            validate(doc)


class TestValidateInvalidVersion:
    def test_wrong_version_raises(self):
        doc = CIRDocument(
            uuid=uuid.uuid4(),
            version="0.0.0",
            raw_text="hello",
            language="en",
            utterances=(
                CIRUtterance(
                    uuid=uuid.uuid4(),
                    text="hello",
                    segments=(
                        CIRSpeechSegment(
                            uuid=uuid.uuid4(),
                            text="hello",
                            tokens=(),
                            segment_index=0,
                            source_offset=0,
                            length=5,
                        ),
                    ),
                ),
            ),
        )
        with pytest.raises(CIRValidationError, match="[Vv]ersion"):
            validate(doc)


class TestValidateInvalidLanguage:
    def test_empty_language_raises(self):
        doc = CIRDocument(
            uuid=uuid.uuid4(),
            version=CIR_VERSION,
            raw_text="hello",
            language="",
            utterances=(
                CIRUtterance(
                    uuid=uuid.uuid4(),
                    text="hello",
                    segments=(
                        CIRSpeechSegment(
                            uuid=uuid.uuid4(),
                            text="hello",
                            tokens=(),
                            segment_index=0,
                            source_offset=0,
                            length=5,
                        ),
                    ),
                ),
            ),
        )
        with pytest.raises(CIRValidationError, match="[Ll]anguage"):
            validate(doc)


class TestValidateDuplicateUUIDs:
    def test_duplicate_uuids_raises(self):
        shared_id = uuid.uuid4()
        doc = CIRDocument(
            uuid=shared_id,
            version=CIR_VERSION,
            raw_text="hello",
            language="en",
            utterances=(
                CIRUtterance(
                    uuid=shared_id,  # duplicate!
                    text="hello",
                    segments=(
                        CIRSpeechSegment(
                            uuid=uuid.uuid4(),
                            text="hello",
                            tokens=(),
                            segment_index=0,
                            source_offset=0,
                            length=5,
                        ),
                    ),
                ),
            ),
        )
        with pytest.raises(CIRValidationError, match="[Dd]uplicate"):
            validate(doc)


class TestValidateMalformedHierarchy:
    def test_non_cir_document_raises(self):
        with pytest.raises(CIRValidationError):
            validate("not a document")  # type: ignore[arg-type]

    def test_utterance_without_segments_raises(self):
        doc = CIRDocument(
            uuid=uuid.uuid4(),
            version=CIR_VERSION,
            raw_text="hello",
            language="en",
            utterances=(
                CIRUtterance(
                    uuid=uuid.uuid4(),
                    text="hello",
                    segments=(),
                ),
            ),
        )
        with pytest.raises(CIRValidationError, match="[Ss]egment"):
            validate(doc)
