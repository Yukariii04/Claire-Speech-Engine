"""Performance Timeline serializer."""

from __future__ import annotations

import json
from uuid import UUID

from cse.performance.compiler.events import PerformanceEvent
from cse.performance.compiler.exceptions import TimelineSerializationError
from cse.performance.compiler.timeline import PerformanceMetadata, PerformanceTimeline


def serialize_timeline(timeline: PerformanceTimeline) -> str:
    """Convert a PerformanceTimeline to a JSON string."""
    try:
        data = {
            "uuid": str(timeline.uuid),
            "version": timeline.version,
            "events": [
                {
                    "uuid": str(e.uuid),
                    "timestamp_ms": e.timestamp_ms,
                    "event_type": e.event_type,
                    "parameters": e.parameters,
                }
                for e in timeline.events
            ],
            "metadata": {
                "source": timeline.metadata.source,
                "cir_uuid": timeline.metadata.cir_uuid,
            },
        }
        return json.dumps(data, indent=2)
    except Exception as exc:
        raise TimelineSerializationError(f"Serialization failed: {exc}") from exc


def deserialize_timeline(json_string: str) -> PerformanceTimeline:
    """Reconstruct a PerformanceTimeline from a JSON string."""
    try:
        data = json.loads(json_string)
        events = tuple(
            PerformanceEvent(
                uuid=UUID(e["uuid"]),
                timestamp_ms=e["timestamp_ms"],
                event_type=e["event_type"],
                parameters=e["parameters"],
            )
            for e in data["events"]
        )
        return PerformanceTimeline(
            uuid=UUID(data["uuid"]),
            version=data["version"],
            events=events,
            metadata=PerformanceMetadata(
                source=data["metadata"]["source"],
                cir_uuid=data["metadata"]["cir_uuid"],
            ),
        )
    except Exception as exc:
        raise TimelineSerializationError(f"Deserialization failed: {exc}") from exc
