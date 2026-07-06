"""Tests for the performance compiler serializer."""

from __future__ import annotations

import json
import pytest

from cse.language.cir import build_cir
from cse.performance.compiler import compile_performance
from cse.performance.compiler.exceptions import TimelineSerializationError
from cse.performance.compiler.serializer import deserialize_timeline, serialize_timeline


class TestSerializer:
    def test_round_trip(self):
        cir = build_cir("Hello world.")
        tl = compile_performance(cir)
        
        json_str = serialize_timeline(tl)
        assert isinstance(json_str, str)
        
        restored = deserialize_timeline(json_str)
        assert restored.uuid == tl.uuid
        assert restored.version == tl.version
        assert len(restored.events) == len(tl.events)
        
        for e1, e2 in zip(tl.events, restored.events):
            assert e1.uuid == e2.uuid
            assert e1.event_type == e2.event_type
            assert e1.timestamp_ms == e2.timestamp_ms
            assert e1.parameters == e2.parameters

    def test_invalid_json_raises(self):
        with pytest.raises(TimelineSerializationError):
            deserialize_timeline("not json")

    def test_missing_fields_raises(self):
        with pytest.raises(TimelineSerializationError):
            deserialize_timeline('{"version": "1.0.0"}')
