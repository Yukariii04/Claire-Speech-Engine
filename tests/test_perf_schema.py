"""Tests for Performance Timeline schemas."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from cse.performance.compiler.events import (
    EVENT_TOKEN,
    PerformanceEvent,
)
from cse.performance.compiler.timeline import (
    PerformanceMetadata,
    PerformanceTimeline,
)
from cse.performance.compiler import get_version


def _make_event(overrides: dict[str, Any] | None = None) -> PerformanceEvent:
    defaults = {
        "uuid": uuid.uuid4(),
        "timestamp_ms": 0,
        "event_type": EVENT_TOKEN,
        "parameters": {"token": "test"},
    }
    if overrides:
        defaults.update(overrides)
    return PerformanceEvent(**defaults)  # type: ignore[arg-type]


class TestPerformanceMetadata:
    def test_defaults(self):
        m = PerformanceMetadata()
        assert m.source == "compiler"
        assert m.cir_uuid == ""

    def test_immutable(self):
        m = PerformanceMetadata()
        with pytest.raises(AttributeError):
            m.source = "other"  # type: ignore[misc]


class TestPerformanceEvent:
    def test_fields(self):
        ev = _make_event({"timestamp_ms": 150})
        assert ev.timestamp_ms == 150
        assert ev.event_type == EVENT_TOKEN
        assert ev.parameters["token"] == "test"

    def test_immutable(self):
        ev = _make_event()
        with pytest.raises(AttributeError):
            ev.timestamp_ms = 100  # type: ignore[misc]


class TestPerformanceTimeline:
    def test_events_are_tuple(self):
        ev = _make_event()
        tl = PerformanceTimeline(
            uuid=uuid.uuid4(),
            version=get_version(),
            events=(ev,),
        )
        assert isinstance(tl.events, tuple)
        assert tl.events[0] == ev

    def test_immutable(self):
        ev = _make_event()
        tl = PerformanceTimeline(
            uuid=uuid.uuid4(),
            version=get_version(),
            events=(ev,),
        )
        with pytest.raises(AttributeError):
            tl.version = "0.0.0"  # type: ignore[misc]
