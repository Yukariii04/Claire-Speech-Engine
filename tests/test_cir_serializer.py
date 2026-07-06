"""Tests for the CIR serializer — lossless round-trip (PRD §17)."""

from __future__ import annotations

import json

import pytest

from cse.language.cir.builder import build_cir
from cse.language.cir.exceptions import CIRSerializationError
from cse.language.cir.schema import CIR_VERSION, CIRDocument
from cse.language.cir.serializer import deserialize, serialize


class TestSerialize:
    def test_returns_string(self):
        doc = build_cir("Hello world.")
        result = serialize(doc)
        assert isinstance(result, str)

    def test_valid_json(self):
        doc = build_cir("Hello world.")
        result = serialize(doc)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_contains_version(self):
        doc = build_cir("Hello world.")
        parsed = json.loads(serialize(doc))
        assert parsed["version"] == CIR_VERSION

    def test_contains_uuid(self):
        doc = build_cir("Hello world.")
        parsed = json.loads(serialize(doc))
        assert "uuid" in parsed

    def test_contains_utterances(self):
        doc = build_cir("Hello world.")
        parsed = json.loads(serialize(doc))
        assert "utterances" in parsed
        assert len(parsed["utterances"]) == 1


class TestDeserialize:
    def test_returns_cir_document(self):
        doc = build_cir("Hello world.")
        json_str = serialize(doc)
        restored = deserialize(json_str)
        assert isinstance(restored, CIRDocument)

    def test_invalid_json_raises(self):
        with pytest.raises(CIRSerializationError):
            deserialize("not json {{{")

    def test_missing_fields_raises(self):
        with pytest.raises(CIRSerializationError):
            deserialize('{"version": "2.0.0"}')


class TestRoundTrip:
    def test_simple_round_trip(self):
        original = build_cir("Hello world.")
        restored = deserialize(serialize(original))
        assert restored.uuid == original.uuid
        assert restored.version == original.version
        assert restored.raw_text == original.raw_text
        assert restored.language == original.language

    def test_multi_sentence_round_trip(self):
        original = build_cir("Hello. Goodbye. Thanks.")
        restored = deserialize(serialize(original))
        assert len(restored.utterances) == len(original.utterances)
        for orig_u, rest_u in zip(original.utterances, restored.utterances):
            assert orig_u.text == rest_u.text
            assert orig_u.uuid == rest_u.uuid

    def test_token_data_preserved(self):
        original = build_cir("Hello world.")
        restored = deserialize(serialize(original))
        orig_tokens = original.utterances[0].segments[0].tokens
        rest_tokens = restored.utterances[0].segments[0].tokens
        for o, r in zip(orig_tokens, rest_tokens):
            assert o.text == r.text
            assert o.uuid == r.uuid
            assert o.position == r.position
            assert o.source_offset == r.source_offset
            assert o.length == r.length
            assert o.whitespace_after == r.whitespace_after
            assert o.punctuation_after == r.punctuation_after

    def test_metadata_preserved(self):
        original = build_cir("Hello.")
        restored = deserialize(serialize(original))
        assert restored.metadata.created_version == original.metadata.created_version
        assert restored.metadata.source == original.metadata.source
        assert restored.metadata.locale == original.metadata.locale

    def test_unicode_round_trip(self):
        original = build_cir("Héllo wörld.")
        restored = deserialize(serialize(original))
        assert restored.raw_text == original.raw_text

    def test_emoji_round_trip(self):
        original = build_cir("Hello 🌍.")
        restored = deserialize(serialize(original))
        assert restored.raw_text == original.raw_text

    def test_deserialized_is_immutable(self):
        doc = build_cir("Hello.")
        restored = deserialize(serialize(doc))
        with pytest.raises(AttributeError):
            restored.raw_text = "other"  # type: ignore[misc]
