"""Tests for performance compiler validator."""

from __future__ import annotations

import pytest
import uuid

from cse.performance.compiler.events import (
    EVENT_SPEAK_END,
    EVENT_SPEAK_START,
    EVENT_TOKEN,
    PerformanceEvent,
)
from cse.performance.compiler.exceptions import TimelineValidationError
from cse.performance.compiler.timeline import PerformanceTimeline, PerformanceMetadata
from cse.performance.compiler import get_version

def _make_timeline(events: tuple[PerformanceEvent, ...]) -> PerformanceTimeline:
    return PerformanceTimeline(
        uuid=uuid.uuid4(),
        version=get_version(),
        events=events,
        metadata=PerformanceMetadata(),
    )


class TestValidateTimeline:
    def test_missing_uuid_raises(self):
        ev = PerformanceEvent(uuid=None, timestamp_ms=0, event_type=EVENT_TOKEN, parameters={}) # type: ignore
        tl = _make_timeline((ev,))
        with pytest.raises(TimelineValidationError, match="UUID"):
            from cse.performance.compiler.validator import validate_timeline
            validate_timeline(tl)

    def test_negative_timestamp_raises(self):
        ev = PerformanceEvent(uuid=uuid.uuid4(), timestamp_ms=-1, event_type=EVENT_TOKEN, parameters={})
        tl = _make_timeline((ev,))
        with pytest.raises(TimelineValidationError, match="[Tt]imestamp"):
            from cse.performance.compiler.validator import validate_timeline
            validate_timeline(tl)

    def test_duplicate_uuid_raises(self):
        shared_id = uuid.uuid4()
        ev1 = PerformanceEvent(uuid=shared_id, timestamp_ms=0, event_type=EVENT_SPEAK_START, parameters={})
        ev2 = PerformanceEvent(uuid=shared_id, timestamp_ms=10, event_type=EVENT_SPEAK_END, parameters={})
        tl = _make_timeline((ev1, ev2))
        with pytest.raises(TimelineValidationError, match="[Dd]uplicate"):
            from cse.performance.compiler.validator import validate_timeline
            validate_timeline(tl)

    def test_invalid_event_order_raises(self):
        ev1 = PerformanceEvent(uuid=uuid.uuid4(), timestamp_ms=100, event_type=EVENT_SPEAK_START, parameters={})
        ev2 = PerformanceEvent(uuid=uuid.uuid4(), timestamp_ms=0, event_type=EVENT_SPEAK_START, parameters={})
        tl = _make_timeline((ev1, ev2))
        with pytest.raises(TimelineValidationError, match="[Oo]rder"):
            from cse.performance.compiler.validator import validate_timeline
            validate_timeline(tl)

    def test_invalid_parameters_raises(self):
        ev = PerformanceEvent(uuid=uuid.uuid4(), timestamp_ms=0, event_type="UNKNOWN", parameters={})
        tl = _make_timeline((ev,))
        with pytest.raises(TimelineValidationError, match="[Tt]ype|[Pp]aram"):
            from cse.performance.compiler.validator import validate_timeline
            validate_timeline(tl)

    def test_invalid_attribute_ranges_raises(self):
        ev = PerformanceEvent(uuid=uuid.uuid4(), timestamp_ms=0, event_type=EVENT_TOKEN, parameters={"token": "a", "warmth": 1.5})
        tl = _make_timeline((ev,))
        with pytest.raises(TimelineValidationError, match="[Rr]ange"):
            from cse.performance.compiler.validator import validate_timeline
            validate_timeline(tl)
