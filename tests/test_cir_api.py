"""Tests for the CIR public API (__init__.py)."""

from __future__ import annotations

from cse.language.cir import (
    build_cir,
    deserialize,
    get_version,
    serialize,
    validate,
)
from cse.language.cir.schema import CIR_VERSION, CIRDocument


class TestPublicAPI:
    def test_get_version(self):
        assert get_version() == CIR_VERSION

    def test_build_cir_accessible(self):
        doc = build_cir("Hello.")
        assert isinstance(doc, CIRDocument)

    def test_validate_accessible(self):
        doc = build_cir("Hello.")
        validate(doc)  # should not raise

    def test_serialize_accessible(self):
        doc = build_cir("Hello.")
        result = serialize(doc)
        assert isinstance(result, str)

    def test_deserialize_accessible(self):
        doc = build_cir("Hello.")
        restored = deserialize(serialize(doc))
        assert isinstance(restored, CIRDocument)

    def test_full_pipeline(self):
        """End-to-end: build → validate → serialize → deserialize."""
        doc = build_cir("I really missed you.")
        validate(doc)
        json_str = serialize(doc)
        restored = deserialize(json_str)
        assert restored.uuid == doc.uuid
        assert restored.raw_text == doc.raw_text
