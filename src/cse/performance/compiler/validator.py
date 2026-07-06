"""Performance Timeline validator."""

from __future__ import annotations

from uuid import UUID

from cse.performance.compiler.events import EVENT_SPEAK_END, EVENT_SPEAK_START, EVENT_TOKEN, EVENT_EMPHASIS, EVENT_PAUSE, EVENT_BREATH
from cse.performance.compiler.exceptions import TimelineValidationError
from cse.performance.compiler.timeline import PerformanceTimeline, COMPILER_VERSION

_VALID_EVENTS = {
    EVENT_SPEAK_START,
    EVENT_TOKEN,
    EVENT_EMPHASIS,
    EVENT_PAUSE,
    EVENT_BREATH,
    EVENT_SPEAK_END,
}


def validate_timeline(timeline: PerformanceTimeline) -> None:
    """Validate a PerformanceTimeline's structural integrity."""
    if not isinstance(timeline, PerformanceTimeline):
        raise TimelineValidationError("Not a PerformanceTimeline.")

    if timeline.version != COMPILER_VERSION:
        raise TimelineValidationError(f"Invalid version: {timeline.version}")

    seen_uuids: set[UUID] = set()
    seen_uuids.add(timeline.uuid)

    last_time = -1

    for i, ev in enumerate(timeline.events):
        if not ev.uuid:
            raise TimelineValidationError(f"Missing UUID at event {i}")

        if ev.uuid in seen_uuids:
            raise TimelineValidationError(f"Duplicate UUID {ev.uuid} at event {i}")
        seen_uuids.add(ev.uuid)

        if ev.timestamp_ms < 0:
            raise TimelineValidationError(f"Negative timestamp {ev.timestamp_ms} at event {i}")

        if ev.timestamp_ms < last_time:
            raise TimelineValidationError(f"Invalid order: event {i} timestamp {ev.timestamp_ms} < {last_time}")
        last_time = ev.timestamp_ms

        if ev.event_type not in _VALID_EVENTS:
            raise TimelineValidationError(f"Invalid event type: {ev.event_type}")

        _validate_parameters(ev)


def _validate_parameters(ev) -> None:
    p = ev.parameters
    if ev.event_type == EVENT_TOKEN:
        if "token" not in p:
            raise TimelineValidationError(f"Missing 'token' in TOKEN event {ev.uuid}")
        
        # Check attributes
        attrs = [
            "warmth", "energy", "confidence", "affection", "curiosity",
            "playfulness", "breathiness", "tension", "dominance", "excitement"
        ]
        for attr in attrs:
            val = p.get(attr)
            if val is None or not (0.0 <= val <= 1.0):
                raise TimelineValidationError(f"Attribute {attr} out of range in {ev.uuid}")

    elif ev.event_type == EVENT_EMPHASIS:
        val = p.get("strength")
        if val is None or not (0.0 <= val <= 1.0):
            raise TimelineValidationError(f"Emphasis strength out of range in {ev.uuid}")

    elif ev.event_type == EVENT_PAUSE:
        val = p.get("duration_ms")
        if val is None or val < 0:
            raise TimelineValidationError(f"Invalid pause duration in {ev.uuid}")

    elif ev.event_type == EVENT_BREATH:
        val = p.get("type")
        if val not in ("INHALE", "EXHALE"):
            raise TimelineValidationError(f"Invalid breath type {val} in {ev.uuid}")
