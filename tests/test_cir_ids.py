"""Tests for CIR UUID generation (ids.py)."""

from __future__ import annotations

import uuid

from cse.language.cir.ids import CIR_NAMESPACE, generate_id


class TestCIRIds:
    def test_returns_uuid(self):
        result = generate_id("hello")
        assert isinstance(result, uuid.UUID)

    def test_deterministic(self):
        a = generate_id("some text")
        b = generate_id("some text")
        assert a == b

    def test_different_seeds_differ(self):
        a = generate_id("alpha")
        b = generate_id("beta")
        assert a != b

    def test_namespace_is_uuid(self):
        assert isinstance(CIR_NAMESPACE, uuid.UUID)

    def test_uuid5_version(self):
        result = generate_id("test")
        assert result.version == 5
